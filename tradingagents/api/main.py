# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import os
import json
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from tradingagents.api.models import (
    ChatRequest, ChatResponse,
    AnalysisRequest, AnalysisResponse,
    FeedbackRequest,
    TickerCreate, TickerUpdate
)
from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.bot.state_tracker import get_state_tracker
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.database.learning_ops import LearningOperations
from tradingagents.database.system_ops import SystemOperations
from tradingagents.database.ticker_ops import TickerOperations
from tradingagents.database.rag_ops import RAGOperations
from tradingagents.rag.embeddings import EmbeddingGenerator
from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
from tradingagents.monitoring.metrics import TradingMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Global instances
agent = None
learning_ops = None
system_ops = None
ticker_ops = None
trading_metrics = None  # Initialize in lifespan to avoid Prometheus duplication

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent, learning_ops, system_ops, ticker_ops, trading_metrics
    logger.info("Initializing Conversational Agent...")
    try:
        # Initialize metrics (do this here to avoid Prometheus duplication on reload)
        if trading_metrics is None:
            trading_metrics = TradingMetrics()
        
        # Ensure Langfuse is enabled in config if env vars are present
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            DEFAULT_CONFIG["enable_langfuse"] = True
            logger.info("Langfuse tracing enabled via environment variables")
            
        agent = ConversationalAgent(config=DEFAULT_CONFIG)
        learning_ops = LearningOperations()
        system_ops = SystemOperations()
        ticker_ops = TickerOperations()
        logger.info("Conversational Agent and Learning Ops initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")
    if agent:
        # Flush any pending Langfuse events
        try:
            if hasattr(agent, 'langfuse') and agent.langfuse:
                agent.langfuse.flush()
        except Exception:
            pass

app = FastAPI(
    title="TradingAgents API",
    description="API for the Human-like Trading Assistant",
    version="1.0.0",
    lifespan=lifespan
)

class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check, root, metrics, and docs
        if request.url.path in ["/", "/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"]:
            return await call_next(request)
            
        # Skip auth for internal metrics
        if request.url.path.startswith("/metrics/"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY")
        
        # If no API key is set in env, allow all (dev mode)
        if not expected_key:
            return await call_next(request)
            
        if not api_key or api_key != expected_key:
            return Response("Unauthorized", status_code=401)
            
        return await call_next(request)

app.add_middleware(ApiKeyMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Mount additional Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics/internal", metrics_app)

@app.get("/")
async def root():
    return {"status": "ok", "message": "TradingAgents API is running"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "agent_initialized": agent is not None,
        "agent_has_trading_agent": agent is not None and hasattr(agent, 'trading_agent') if agent else False
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint (non-streaming, for backward compatibility).
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    # Track chat request
    trading_metrics.track_chat_request()

    try:
        # Log prompt metadata if provided
        if request.prompt_type or request.prompt_id:
            logger.info(f"Predefined prompt used - Type: {request.prompt_type}, ID: {request.prompt_id}")
        # Convert Pydantic models to dicts for the agent
        history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # Pass session_id to agent if supported, or handle via context
        # For now, we just call the agent. The agent's internal graph will pick up
        # the global tracer if configured.
        
        # Apply prompt-specific optimizations
        prompt_metadata = None
        if request.prompt_type or request.prompt_id:
            prompt_metadata = {
                "prompt_type": request.prompt_type,
                "prompt_id": request.prompt_id
            }
            logger.info(f"Applying prompt-specific optimizations for {request.prompt_type}/{request.prompt_id}")

        # Track agent processing time
        import time
        start_time = time.time()

        response_text = await agent.chat(
            message=request.message,
            history=history,
            prompt_metadata=prompt_metadata
        )

        # Record processing time
        processing_time = time.time() - start_time
        trading_metrics.track_agent_processing_time(processing_time)
        trading_metrics.track_successful_chat()

        # Log interaction to database for learning
        if learning_ops and request.conversation_id:
            # Log user message with prompt metadata
            learning_ops.log_interaction(
                conversation_id=request.conversation_id,
                role="user",
                content=request.message,
                prompt_type=request.prompt_type,
                prompt_id=request.prompt_id
            )
            
            # Log assistant response (no prompt metadata for assistant messages)
            interaction_id = learning_ops.log_interaction(
                conversation_id=request.conversation_id,
                role="assistant",
                content=response_text
            )
            
            # Add interaction_id to metadata for frontend to send back with feedback
            return ChatResponse(
                response=response_text,
                conversation_id=request.conversation_id,
                metadata={"interaction_id": interaction_id}
            )
        
        return ChatResponse(
            response=response_text,
            conversation_id=request.conversation_id or "new_session"
        )


    except Exception as e:
        trading_metrics.track_failed_chat()
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint with progress indicators.
    Returns Server-Sent Events (SSE) with agent progress and response chunks.
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    async def generate():
        try:
            # Validate request
            if not request.message or not request.message.strip():
                error_data = {
                    "type": "error",
                    "message": "Empty message provided"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"

            # Convert Pydantic models to dicts for the agent
            history = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.conversation_history
            ]

            # Apply prompt-specific optimizations
            prompt_metadata = None
            if request.prompt_type or request.prompt_id:
                prompt_metadata = {
                    "prompt_type": request.prompt_type,
                    "prompt_id": request.prompt_id
                }

            # Initialize state tracker
            state_tracker = get_state_tracker()
            from tradingagents.bot.state_tracker import EddieState

            # Set initial state
            state_tracker.set_state(EddieState.PROCESSING, "Processing your request...")
            state_tracker.clear_active_tools()

            # Stream from the conversational agent (with intent classification)
            full_response = ""
            tool_calls = set()  # Use set to avoid duplicates
            active_tools = []

            async for chunk in agent.chat_stream(
                message=request.message,
                history=history,
                prompt_metadata=prompt_metadata
            ):
                # Parse chunk to detect tool calls and content
                chunk_str = str(chunk)

                # Detect tool calls (format: "🔧 Using tools: tool1, tool2...")
                if "🔧 Using tools:" in chunk_str:
                    # Extract tool names
                    tool_line = chunk_str.split("🔧 Using tools:")[1].split("\n")[0].strip()
                    tool_names = [t.strip() for t in tool_line.replace("...", "").split(",") if t.strip()]

                    for tool_name in tool_names:
                        tool_calls.add(tool_name)
                        if tool_name not in active_tools:
                            active_tools.append(tool_name)
                            state_tracker.add_active_tool(tool_name)

                    # Update state message
                    state_tracker.set_state(EddieState.PROCESSING, f"Using tools: {', '.join(active_tools)}")

                    # Send progress event
                    progress_data = {
                        "type": "progress",
                        "tools": active_tools.copy(),
                        "message": f"Using tools: {', '.join(active_tools)}"
                    }
                    yield f"data: {json.dumps(progress_data)}\n\n"

                # Regular content chunks (skip progress dots and warnings)
                elif chunk_str.strip() and chunk_str != "." and not chunk_str.startswith("⚠️"):
                    # If we have active tools and content starts, mark tools as completed
                    if active_tools and chunk_str.strip():
                        # Tools completed, clear active list
                        completed_data = {
                            "type": "tools_completed",
                            "tools": active_tools.copy()
                        }
                        yield f"data: {json.dumps(completed_data)}\n\n"
                        active_tools = []

                    # Update state to speaking when content starts
                    if not full_response:  # First content chunk
                        state_tracker.set_state(EddieState.SPEAKING, "Generating response...")

                    # Send content chunk
                    content_data = {
                        "type": "content",
                        "chunk": chunk_str
                    }
                    yield f"data: {json.dumps(content_data)}\n\n"
                    full_response += chunk_str
            
            # Reset state to idle after completion
            state_tracker.set_state(EddieState.IDLE, "Ready")
            state_tracker.clear_active_tools()
            
            # Send completion event
            completion_data = {
                "type": "done",
                "conversation_id": request.conversation_id or "new_session"
            }
            
            # Log interaction to database for learning
            if learning_ops and request.conversation_id:
                # Log user message
                learning_ops.log_interaction(
                    conversation_id=request.conversation_id,
                    role="user",
                    content=request.message,
                    prompt_type=request.prompt_type,
                    prompt_id=request.prompt_id
                )
                
                # Log assistant response
                interaction_id = learning_ops.log_interaction(
                    conversation_id=request.conversation_id,
                    role="assistant",
                    content=full_response
                )
                
                completion_data["metadata"] = {"interaction_id": interaction_id}
            
            yield f"data: {json.dumps(completion_data)}\n\n"
            
        except Exception as e:
            # Set error state
            state_tracker = get_state_tracker()
            from tradingagents.bot.state_tracker import EddieState
            state_tracker.set_state(EddieState.ERROR, f"Error: {str(e)}")
            
            logger.error(f"Error in streaming chat endpoint: {e}", exc_info=True)
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Full traceback: {error_trace}")
            error_data = {
                "type": "error",
                "message": str(e),
                "details": error_trace if logger.level <= logging.DEBUG else None
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest):
    """
    Direct analysis endpoint (bypassing chat logic if needed).
    """
    # TODO: Implement direct analysis via agent
    raise HTTPException(status_code=501, detail="Not implemented yet")

@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    """
    Endpoint to receive user feedback for learning.
    """
    if not learning_ops:
        raise HTTPException(status_code=503, detail="Learning ops not initialized")

    try:
        # Track feedback
        trading_metrics.track_user_feedback(request.rating)
        logger.info(f"Received feedback: {request}")
        
        # If we have a message_id (which maps to interaction_id), update the record
        if request.message_id:
            try:
                interaction_id = int(request.message_id)
                learning_ops.add_feedback(
                    interaction_id=interaction_id,
                    rating=request.rating,
                    comment=request.comment,
                    correction=request.correction
                )
                
                # Score the trace in Langfuse using the global tracer
                tracer = get_langfuse_tracer()
                if tracer and tracer.enabled:
                    # Note: We need the trace_id to score it. 
                    # Since we don't have it easily here (it was generated in the graph),
                    # we might need to pass it back in metadata.
                    # For now, we'll try to score by session if possible, or just skip if no trace_id.
                    # But score_trace needs a trace_id.
                    # If we can't link it, we can't score it in Langfuse easily without the trace ID.
                    # We'll log a warning for now.
                    pass
                
                return {"status": "success", "message": "Feedback recorded"}
            except ValueError:
                logger.warning(f"Invalid message_id format: {request.message_id}")
        
        # Fallback if no message_id or invalid
        return {"status": "received", "message": "Feedback received (no interaction linked)"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/synthesize")
async def synthesize_speech(
    text: str,
    tone: Optional[str] = "professional",
    return_base64: bool = False
):
    """
    Synthesize speech from text with emotional tone (v2.0).
    
    Args:
        text: Text to synthesize
        tone: Emotional tone (calm, professional, energetic, technical, reassuring)
        return_base64: If True, return audio as base64 string
    
    Returns:
        Audio file (WAV) or base64 string
    """
    try:
        from tradingagents.voice import get_tts_engine, EmotionalTone, TTSEngineFallback
        import base64
        import tempfile
        import os
        
        # Map tone string to enum
        tone_map = {
            "calm": EmotionalTone.CALM,
            "professional": EmotionalTone.PROFESSIONAL,
            "energetic": EmotionalTone.ENERGETIC,
            "technical": EmotionalTone.TECHNICAL,
            "reassuring": EmotionalTone.REASSURING
        }
        
        tone_enum = tone_map.get(tone.lower(), EmotionalTone.PROFESSIONAL)
        
        # Try to get TTS engine, fallback if Coqui not available
        try:
            tts_engine = get_tts_engine()
            audio_bytes = tts_engine.synthesize(text, tone=tone_enum, return_bytes=True)
        except (ImportError, Exception) as e:
            logger.warning(f"Primary TTS not available ({e}), trying fallback...")
            # Use fallback engine
            tts_engine = get_tts_engine(use_fallback=True)
            audio_bytes = tts_engine.synthesize(text, tone=tone_enum, return_bytes=True)
        
        if audio_bytes:
            if return_base64:
                import base64
                audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                return {"audio_base64": audio_b64, "format": "wav"}
            else:
                from fastapi.responses import Response
                return Response(content=audio_bytes, media_type="audio/wav")
        else:
            raise HTTPException(status_code=500, detail="Failed to synthesize speech")
            
    except ImportError as e:
        logger.warning(f"TTS not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="TTS engine not available. Install TTS library: pip install TTS"
        )
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe")
async def transcribe_speech(
    audio: UploadFile = File(...),
    audio_format: str = "wav",
    sample_rate: int = 16000
):
    """
    Transcribe speech to text (v2.0 STT).
    
    Args:
        audio: Audio file upload (WAV format)
        audio_format: Audio format (wav, mp3, etc.)
        sample_rate: Sample rate in Hz
    
    Returns:
        Transcription result with text and metadata
    """
    try:
        from tradingagents.voice import get_stt_engine
        
        # Read audio file
        audio_data = await audio.read()
        
        # Transcribe
        stt_engine = get_stt_engine()
        result = stt_engine.transcribe(
            audio_data=audio_data,
            audio_format=audio_format,
            sample_rate=sample_rate
        )
        
        return result
        
    except ImportError as e:
        logger.warning(f"STT not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="STT engine not available. Install faster-whisper: pip install faster-whisper"
        )
    except Exception as e:
        logger.error(f"Error transcribing speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe-stream")
async def transcribe_speech_stream(
    audio: UploadFile = File(...)
):
    """
    Transcribe speech stream in real-time (v2.0 STT streaming).
    
    Args:
        audio: Audio file upload
    
    Returns:
        Streaming transcription results
    """
    try:
        from tradingagents.voice import get_stt_engine
        import json
        
        stt_engine = get_stt_engine()
        
        async def generate():
            audio_data = await audio.read()
            
            # Stream transcription
            for result in stt_engine.transcribe_streaming([audio_data]):
                yield f"data: {json.dumps(result)}\n\n"
            
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except ImportError as e:
        logger.warning(f"STT not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="STT engine not available. Install faster-whisper: pip install faster-whisper"
        )
    except Exception as e:
        logger.error(f"Error in streaming transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/voice/ws")
async def websocket_audio_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming and transcription (v2.0).
    
    Supports:
    - Real-time audio streaming from browser
    - Continuous transcription
    - Barge-in detection
    - Two-way communication (audio -> text, text -> audio)
    """
    await websocket.accept()
    logger.info("WebSocket connection established for audio streaming")
    
    try:
        from tradingagents.voice import get_stt_engine, get_tts_engine, EmotionalTone
        import base64
        
        stt_engine = get_stt_engine()
        tts_engine = get_tts_engine()
        
        audio_buffer = b""
        is_listening = False
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "audio_chunk":
                # Accumulate audio chunks
                audio_chunk_b64 = data.get("audio")
                if audio_chunk_b64:
                    audio_chunk = base64.b64decode(audio_chunk_b64)
                    audio_buffer += audio_chunk
                    is_listening = True
                    
            elif message_type == "audio_end":
                # Transcribe accumulated audio
                if audio_buffer and is_listening:
                    try:
                        result = stt_engine.transcribe(audio_buffer)
                        
                        # Send transcription back
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result["text"],
                            "confidence": result.get("segments", [{}])[0].get("confidence", 0.0) if result.get("segments") else 0.0,
                            "language": result.get("language", "en")
                        })
                        
                        audio_buffer = b""
                        is_listening = False
                    except Exception as e:
                        logger.error(f"Error transcribing audio: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e)
                        })
                        
            elif message_type == "synthesize":
                # Synthesize text to speech
                text = data.get("text", "")
                tone = data.get("tone", "professional")
                
                if text:
                    try:
                        tone_map = {
                            "calm": EmotionalTone.CALM,
                            "professional": EmotionalTone.PROFESSIONAL,
                            "energetic": EmotionalTone.ENERGETIC,
                            "technical": EmotionalTone.TECHNICAL,
                            "reassuring": EmotionalTone.REASSURING
                        }
                        tone_enum = tone_map.get(tone.lower(), EmotionalTone.PROFESSIONAL)
                        
                        audio_bytes = tts_engine.synthesize(text, tone=tone_enum, return_bytes=True)
                        
                        if audio_bytes:
                            # Send audio as base64
                            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                            await websocket.send_json({
                                "type": "audio",
                                "audio_base64": audio_b64,
                                "format": "wav"
                            })
                    except Exception as e:
                        logger.error(f"Error synthesizing speech: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": str(e)
                        })
                        
            elif message_type == "barge_in":
                # User interrupted audio playback
                logger.info("Barge-in signal received from client")
                await websocket.send_json({
                    "type": "barge_in_ack",
                    "message": "Audio playback stopped"
                })
                        
            elif message_type == "stop":
                # Stop current operation
                audio_buffer = b""
                is_listening = False
                await websocket.send_json({"type": "stopped"})
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket audio stream: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

@app.get("/analytics/prompts")
async def get_prompt_analytics(days: int = 30):
    """
    Get analytics on prompt usage and performance.
    
    Args:
        days: Number of days to look back (default: 30, max: 365)
    """
    if not learning_ops:
        raise HTTPException(status_code=503, detail="Learning ops not initialized")
    
    try:
        # Limit days to reasonable range
        days = max(1, min(days, 365))
        
        analytics = learning_ops.get_prompt_analytics(days=days)
        return analytics
        
    except Exception as e:
        logger.error(f"Error fetching prompt analytics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/state")
async def get_eddie_state():
    """
    Get Eddie's current state for UI visualization (v2.0).
    
    Returns:
        Current state including:
        - state: idle, listening, processing, speaking, error, validating
        - confidence: Multi-factor confidence metrics
        - current_ticker: Currently analyzed ticker
        - active_tools: List of active tools
        - system_health: HEALTHY, WARNING, CRITICAL
    """
    try:
        state_tracker = get_state_tracker()
        return state_tracker.get_state_dict()
    except Exception as e:
        logger.error(f"Error getting Eddie state: {e}")
        # Return default state on error
        return {
            "state": "idle",
            "confidence": {
                "data_freshness": 0,
                "math_verification": 0,
                "ai_confidence": 0,
                "overall": 0
            },
            "current_ticker": None,
            "active_tools": [],
            "system_health": "HEALTHY",
            "timestamp": None,
            "message": ""
        }

@app.get("/system/status")
async def get_system_status():
    """
    Get system status and database statistics.
    """
    if not system_ops:
        raise HTTPException(status_code=503, detail="System ops not initialized")
    
    try:
        stats = system_ops.get_database_stats()
        services = system_ops.get_service_status()
        missing_data = system_ops.get_missing_data_report()
        
        return {
            "status": "online",
            "services": services,
            "stats": stats,
            "missing_data": missing_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/tickers")
async def get_tickers(active_only: bool = True):
    """
    Get all tickers.
    """
    if not ticker_ops:
        raise HTTPException(status_code=503, detail="Ticker ops not initialized")
    
    try:
        return ticker_ops.get_all_tickers(active_only=active_only)
    except Exception as e:
        logger.error(f"Error fetching tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/tickers")
async def add_ticker(ticker: TickerCreate):
    """
    Add a new ticker.
    """
    if not ticker_ops:
        raise HTTPException(status_code=503, detail="Ticker ops not initialized")
    
    try:
        ticker_id = ticker_ops.add_ticker(
            symbol=ticker.symbol,
            company_name=ticker.company_name,
            sector=ticker.sector,
            industry=ticker.industry,
            market_cap=ticker.market_cap,
            priority_tier=ticker.priority_tier,
            tags=ticker.tags,
            notes=ticker.notes
        )
        return {"status": "success", "ticker_id": ticker_id, "symbol": ticker.symbol}
    except Exception as e:
        logger.error(f"Error adding ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/data/tickers/{symbol}")
async def update_ticker(symbol: str, ticker: TickerUpdate):
    """
    Update an existing ticker.
    """
    if not ticker_ops:
        raise HTTPException(status_code=503, detail="Ticker ops not initialized")
    
    try:
        # Convert pydantic model to dict, excluding None values
        update_data = ticker.dict(exclude_unset=True)
        
        success = ticker_ops.update_ticker(symbol, **update_data)
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
            
        return {"status": "success", "symbol": symbol, "updated_fields": list(update_data.keys())}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data/tickers/{symbol}")
async def remove_ticker(symbol: str, soft_delete: bool = True):
    """
    Remove a ticker (soft delete by default).
    """
    if not ticker_ops:
        raise HTTPException(status_code=503, detail="Ticker ops not initialized")
    
    try:
        success = ticker_ops.remove_ticker(symbol, soft_delete=soft_delete)
        if not success:
            raise HTTPException(status_code=404, detail=f"Ticker {symbol} not found")
            
        return {"status": "success", "symbol": symbol, "action": "soft_delete" if soft_delete else "hard_delete"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/refresh/{type}")
async def refresh_data(type: str, background_tasks: BackgroundTasks):
    """
    Trigger a data refresh task.
    """
    if type not in ["scan", "analysis", "rag"]:
        raise HTTPException(status_code=400, detail="Invalid refresh type. Must be 'scan', 'analysis', or 'rag'")
    
    # In a real implementation, we would trigger background tasks here
    # For now, we'll just simulate it or call a placeholder
    
    logger.info(f"Triggering data refresh for {type}")
    
    return {"status": "accepted", "message": f"Refresh task for {type} started"}

@app.post("/debug/execute_tool")
async def execute_tool(tool_name: str, args: Dict[str, Any]):
    """
    Execute a specific tool by name (Debug only).
    """
    if not agent or not agent.trading_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Find the tool
        tool = next((t for t in agent.trading_agent.tools if t.name == tool_name), None)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
        # Execute tool
        logger.info(f"Executing debug tool: {tool_name} with args: {args}")
        
        # Handle different tool types (some might need specific invocation)
        if hasattr(tool, 'invoke'):
            result = tool.invoke(args)
        else:
            result = tool(**args)
            
        return {"status": "success", "tool": tool_name, "result": str(result)}
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {"status": "error", "tool": tool_name, "error": str(e)}

@app.post("/debug/rag_search")
async def rag_search(query: str, limit: int = 5, similarity_threshold: float = 0.5):
    """
    Query the RAG vector database directly (Debug only).
    
    Searches for similar past analyses using vector similarity search.
    The query text is converted to an embedding and matched against
    stored analysis embeddings in the database.
    
    Args:
        query: Natural language query (e.g., "AAPL showing strong momentum")
        limit: Maximum number of results to return (default: 5)
        similarity_threshold: Minimum similarity score 0-1 (default: 0.5)
    
    Returns:
        List of similar analyses with similarity scores and metadata
    """
    try:
        # Initialize embedding generator and RAG operations
        embedding_gen = EmbeddingGenerator()
        rag_ops = RAGOperations()
        
        # Test embedding service connection
        if not embedding_gen.test_connection():
            logger.warning("Embedding service not available, returning empty results")
            return {
                "status": "error",
                "query": query,
                "error": "Embedding service (Ollama) not available. Make sure Ollama is running with nomic-embed-text model.",
                "results": []
            }
        
        # Generate embedding for the query
        query_embedding = embedding_gen.generate(query)
        if not query_embedding:
            return {
                "status": "error",
                "query": query,
                "error": "Failed to generate embedding for query",
                "results": []
            }
        
        # Search for similar analyses
        similar_analyses = rag_ops.find_similar_analyses(
            query_embedding=query_embedding,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        # Format results with ticker information
        formatted_results = []
        for analysis in similar_analyses:
            # Get ticker symbol
            symbol = f"Ticker_{analysis.get('ticker_id')}"
            if ticker_ops:
                ticker_info = ticker_ops.get_ticker(ticker_id=analysis.get('ticker_id'))
                if ticker_info:
                    symbol = ticker_info['symbol']
            
            # Build content from analysis
            content_parts = []
            if analysis.get('executive_summary'):
                content_parts.append(f"Summary: {analysis['executive_summary']}")
            if analysis.get('final_decision'):
                content_parts.append(f"Decision: {analysis['final_decision']}")
            if analysis.get('confidence_score'):
                content_parts.append(f"Confidence: {analysis['confidence_score']}/100")
            
            content = " | ".join(content_parts) if content_parts else "Analysis available"
            
            formatted_results.append({
                "content": content,
                "metadata": {
                    "source": "analysis",
                    "analysis_id": analysis.get('analysis_id'),
                    "ticker": symbol,
                    "ticker_id": analysis.get('ticker_id'),
                    "analysis_date": str(analysis.get('analysis_date')) if analysis.get('analysis_date') else None,
                    "final_decision": analysis.get('final_decision'),
                    "confidence_score": analysis.get('confidence_score'),
                    "similarity": round(analysis.get('similarity', 0), 3) if analysis.get('similarity') else None
                }
            })
        
        logger.info(f"RAG search for '{query}' returned {len(formatted_results)} results")
        
        return {
            "status": "success",
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Error in RAG search: {e}", exc_info=True)
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "results": []
        }

if __name__ == "__main__":
    uvicorn.run("tradingagents.api.main:app", host="0.0.0.0", port=8005, reload=True, loop="asyncio")
