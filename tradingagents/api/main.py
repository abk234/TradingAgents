import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from prometheus_client import make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator
import uvicorn
import os
import json

from tradingagents.api.models import (
    ChatRequest, ChatResponse,
    AnalysisRequest, AnalysisResponse,
    FeedbackRequest
)
from tradingagents.bot.conversational_agent import ConversationalAgent
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.database.learning_ops import LearningOperations
from tradingagents.monitoring.langfuse_integration import get_langfuse_tracer
from tradingagents.monitoring.metrics import TradingMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Global instances
agent = None
learning_ops = None
trading_metrics = TradingMetrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global agent, learning_ops
    logger.info("Initializing Conversational Agent...")
    try:
        # Ensure Langfuse is enabled in config if env vars are present
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            DEFAULT_CONFIG["enable_langfuse"] = True
            logger.info("Langfuse tracing enabled via environment variables")
            
        agent = ConversationalAgent(config=DEFAULT_CONFIG)
        learning_ops = LearningOperations()
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
            
            # Check agent has required attributes
            if not hasattr(agent, 'trading_agent') or not hasattr(agent, '_format_history'):
                error_data = {
                    "type": "error",
                    "message": "Agent not properly initialized"
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                return
            
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
            
            # Stream from the trading agent
            full_response = ""
            tool_calls = set()  # Use set to avoid duplicates
            active_tools = []
            
            async for chunk in agent.trading_agent.astream(
                request.message, 
                conversation_history=agent._format_history(history)
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
                    
                    # Send content chunk
                    content_data = {
                        "type": "content",
                        "chunk": chunk_str
                    }
                    yield f"data: {json.dumps(content_data)}\n\n"
                    full_response += chunk_str
            
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

if __name__ == "__main__":
    uvicorn.run("tradingagents.api.main:app", host="0.0.0.0", port=8005, reload=True)
