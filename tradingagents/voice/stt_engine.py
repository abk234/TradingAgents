# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Speech-to-Text Engine - Eddie v2.0

Faster-Whisper integration for real-time speech recognition with low latency.
"""

import logging
from typing import Optional, Dict, Any, BinaryIO, Iterator
from dataclasses import dataclass
import io
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class STTConfig:
    """STT configuration."""
    model_size: str = "base"  # tiny, base, small, medium, large-v2
    device: str = "cpu"  # cpu, cuda
    compute_type: str = "int8"  # int8, float16, float32
    language: Optional[str] = "en"
    beam_size: int = 5
    vad_filter: bool = True  # Voice Activity Detection
    vad_threshold: float = 0.5


class STTEngine:
    """
    Speech-to-Text engine using Faster-Whisper.
    
    Features:
    - Low latency (<500ms target)
    - Real-time streaming
    - Voice Activity Detection (VAD)
    - Barge-in support
    """
    
    def __init__(self, config: Optional[STTConfig] = None):
        """
        Initialize STT engine.
        
        Args:
            config: STT configuration (uses defaults if None)
        """
        self.config = config or STTConfig()
        self._model = None
        self._vad_model = None
        self._initialized = False
    
    def _initialize_stt(self):
        """Lazy initialization of Faster-Whisper."""
        if self._initialized:
            return
        
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Initializing Faster-Whisper STT (model: {self.config.model_size})...")
            
            # Initialize Whisper model
            self._model = WhisperModel(
                self.config.model_size,
                device=self.config.device,
                compute_type=self.config.compute_type
            )
            
            # Initialize VAD if enabled
            if self.config.vad_filter:
                try:
                    from faster_whisper import VadOptions
                    self._vad_model = VadOptions()
                except ImportError:
                    logger.warning("VAD not available, continuing without VAD filter")
                    self.config.vad_filter = False
            
            self._initialized = True
            logger.info("STT engine initialized successfully")
            
        except ImportError:
            logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Error initializing STT: {e}")
            raise
    
    def transcribe(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        sample_rate: int = 16000
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio bytes (WAV format)
            audio_format: Audio format (wav, mp3, etc.)
            sample_rate: Sample rate in Hz
        
        Returns:
            Dictionary with transcription and metadata
        """
        if not self._initialized:
            self._initialize_stt()
        
        try:
            # Convert audio bytes to numpy array
            import wave
            import struct
            
            # Parse WAV file
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                audio_bytes = wav_file.readframes(frames)
                
                # Convert to numpy array
                if wav_file.getsampwidth() == 1:
                    dtype = np.uint8
                    audio_array = np.frombuffer(audio_bytes, dtype=dtype).astype(np.float32) / 128.0
                else:
                    dtype = np.int16
                    audio_array = np.frombuffer(audio_bytes, dtype=dtype).astype(np.float32) / 32768.0
            
            # Transcribe
            segments, info = self._model.transcribe(
                audio_array,
                language=self.config.language,
                beam_size=self.config.beam_size,
                vad_filter=self.config.vad_filter,
                vad_parameters=dict(threshold=self.config.vad_threshold) if self.config.vad_filter else None
            )
            
            # Collect segments
            text_segments = []
            full_text = ""
            
            for segment in segments:
                text_segments.append({
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                    "confidence": getattr(segment, 'avg_logprob', 0.0)
                })
                full_text += segment.text + " "
            
            return {
                "text": full_text.strip(),
                "segments": text_segments,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def transcribe_streaming(
        self,
        audio_stream: Iterator[bytes],
        chunk_size: int = 4096
    ) -> Iterator[Dict[str, Any]]:
        """
        Transcribe audio stream in real-time.
        
        Args:
            audio_stream: Iterator of audio chunks
            chunk_size: Size of each chunk
        
        Yields:
            Partial transcription results
        """
        if not self._initialized:
            self._initialize_stt()
        
        # For streaming, we accumulate chunks and transcribe periodically
        audio_buffer = b""
        
        for chunk in audio_stream:
            audio_buffer += chunk
            
            # Transcribe when buffer is large enough
            if len(audio_buffer) >= chunk_size * 4:  # ~1 second of audio
                try:
                    result = self.transcribe(audio_buffer)
                    yield result
                    audio_buffer = b""  # Clear buffer after transcription
                except Exception as e:
                    logger.error(f"Error in streaming transcription: {e}")
                    continue
        
        # Transcribe remaining buffer
        if audio_buffer:
            try:
                result = self.transcribe(audio_buffer)
                yield result
            except Exception as e:
                logger.error(f"Error transcribing final buffer: {e}")


class STTEngineFallback:
    """
    Fallback STT engine using speech_recognition library.
    """
    
    def __init__(self):
        """Initialize fallback STT."""
        self._recognizer = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization."""
        if self._initialized:
            return
        
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._initialized = True
            logger.info("Fallback STT (speech_recognition) initialized")
        except ImportError:
            logger.warning("speech_recognition not available. STT will be disabled.")
            self._recognizer = None
    
    def transcribe(self, audio_data: bytes, audio_format: str = "wav", sample_rate: int = 16000) -> Dict[str, Any]:
        """Transcribe using fallback engine."""
        if not self._initialized:
            self._initialize()
        
        if not self._recognizer:
            raise RuntimeError("STT not available")
        
        try:
            import speech_recognition as sr
            
            # Create AudioData object
            audio_io = io.BytesIO(audio_data)
            with sr.AudioFile(audio_io) as source:
                audio = self._recognizer.record(source)
            
            # Recognize using Google Speech Recognition
            text = self._recognizer.recognize_google(audio)
            
            return {
                "text": text,
                "segments": [{"text": text, "start": 0, "end": 0, "confidence": 0.8}],
                "language": "en",
                "language_probability": 1.0,
                "duration": 0
            }
        except Exception as e:
            logger.error(f"Error in fallback STT: {e}")
            raise


def get_stt_engine(use_fallback: bool = False) -> STTEngine:
    """
    Get STT engine instance.
    
    Args:
        use_fallback: If True, use fallback engine even if Faster-Whisper is available
    
    Returns:
        STTEngine instance
    """
    if use_fallback:
        return STTEngineFallback()
    
    try:
        return STTEngine()
    except Exception as e:
        logger.warning(f"Faster-Whisper not available, using fallback: {e}")
        return STTEngineFallback()

