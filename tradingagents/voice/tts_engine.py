# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Text-to-Speech Engine - Eddie v2.0

Coqui XTTS v2 integration for voice output with emotional tone injection.
"""

import os
import logging
from typing import Optional, Dict, Any, BinaryIO
from enum import Enum
from dataclasses import dataclass
import tempfile
import io

logger = logging.getLogger(__name__)


class EmotionalTone(Enum):
    """Emotional tones for TTS."""
    CALM = "calm"              # Calm, reassuring (for stressed users, market crashes)
    PROFESSIONAL = "professional"  # Standard analytical tone
    ENERGETIC = "energetic"    # Energetic but cautionary (for all-time highs)
    TECHNICAL = "technical"    # Technical, precise (for system diagnostics)
    REASSURING = "reassuring"  # Reassuring, supportive


@dataclass
class TTSConfig:
    """TTS configuration."""
    model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    language: str = "en"
    speaker_wav: Optional[str] = None  # Path to reference speaker audio
    temperature: float = 0.7
    length_penalty: float = 1.0
    repetition_penalty: float = 5.0
    top_k: int = 50
    top_p: float = 0.85
    speed: float = 1.0  # Speech speed multiplier


class TTSEngine:
    """
    Text-to-Speech engine using Coqui XTTS v2.
    
    Features:
    - Emotional tone injection
    - Context-aware voice adaptation
    - Multiple output formats
    """
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """
        Initialize TTS engine.
        
        Args:
            config: TTS configuration (uses defaults if None)
        """
        self.config = config or TTSConfig()
        self._tts = None
        self._initialized = False
        
        # Tone-to-prompt mapping for emotional injection
        self.tone_prompts = {
            EmotionalTone.CALM: "Speak in a calm, reassuring, slow manner. Be gentle and supportive.",
            EmotionalTone.PROFESSIONAL: "Speak in a professional, analytical tone. Be clear and precise.",
            EmotionalTone.ENERGETIC: "Speak with energy and enthusiasm, but maintain caution. Be engaging.",
            EmotionalTone.TECHNICAL: "Speak in a technical, precise manner. Be clear and methodical.",
            EmotionalTone.REASSURING: "Speak in a reassuring, supportive manner. Be empathetic and calm."
        }
    
    def _initialize_tts(self):
        """Lazy initialization of TTS model."""
        if self._initialized:
            return
        
        try:
            from TTS.api import TTS
            
            logger.info(f"Initializing TTS model: {self.config.model_name}")
            self._tts = TTS(model_name=self.config.model_name, gpu=False)  # Use CPU for compatibility
            self._initialized = True
            logger.info("TTS engine initialized successfully")
            
        except ImportError:
            logger.error("TTS library not installed. Install with: pip install TTS")
            raise
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            raise
    
    def synthesize(
        self,
        text: str,
        tone: EmotionalTone = EmotionalTone.PROFESSIONAL,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Optional[bytes]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            tone: Emotional tone to use
            output_path: Path to save audio file (optional)
            return_bytes: If True, return audio as bytes instead of saving
        
        Returns:
            Audio bytes if return_bytes=True, else None
        """
        if not self._initialized:
            self._initialize_tts()
        
        try:
            # Inject emotional tone into text (prepend tone instruction)
            tone_instruction = self.tone_prompts.get(tone, "")
            if tone_instruction:
                # For XTTS, we can't directly inject tone, but we can adjust parameters
                # Tone is more about how we structure the text and use voice parameters
                pass
            
            # Determine output path
            if output_path is None and not return_bytes:
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
                output_path = temp_file.name
                temp_file.close()
            
            # Synthesize speech
            if output_path:
                self._tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    language=self.config.language,
                    speaker_wav=self.config.speaker_wav
                )
                
                if return_bytes:
                    with open(output_path, 'rb') as f:
                        audio_bytes = f.read()
                    os.unlink(output_path)  # Clean up temp file
                    return audio_bytes
                else:
                    return None
            else:
                # Generate to memory
                wav = self._tts.tts(
                    text=text,
                    language=self.config.language,
                    speaker_wav=self.config.speaker_wav
                )
                return wav
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def synthesize_streaming(
        self,
        text: str,
        tone: EmotionalTone = EmotionalTone.PROFESSIONAL,
        chunk_size: int = 100
    ):
        """
        Synthesize speech in chunks for streaming.
        
        Args:
            text: Text to synthesize
            tone: Emotional tone
            chunk_size: Number of characters per chunk
        
        Yields:
            Audio chunks as bytes
        """
        # Split text into chunks
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        for chunk in chunks:
            audio_bytes = self.synthesize(chunk, tone=tone, return_bytes=True)
            if audio_bytes:
                yield audio_bytes
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        if not self._initialized:
            self._initialize_tts()
        
        # XTTS v2 uses reference audio for voice cloning
        # Return empty list for now (would need to scan speaker_wav directory)
        return []
    
    def set_speaker(self, speaker_wav_path: str):
        """Set reference speaker audio for voice cloning."""
        if os.path.exists(speaker_wav_path):
            self.config.speaker_wav = speaker_wav_path
            logger.info(f"Speaker set to: {speaker_wav_path}")
        else:
            logger.warning(f"Speaker file not found: {speaker_wav_path}")


class TTSEngineFallback:
    """
    Fallback TTS engine using system TTS (pyttsx3) if Coqui XTTS is not available.
    """
    
    def __init__(self):
        """Initialize fallback TTS."""
        self._engine = None
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization."""
        if self._initialized:
            return
        
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._initialized = True
            logger.info("Fallback TTS (pyttsx3) initialized")
        except ImportError:
            logger.warning("pyttsx3 not available. TTS will be disabled.")
            self._engine = None
    
    def synthesize(
        self,
        text: str,
        tone: EmotionalTone = EmotionalTone.PROFESSIONAL,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Optional[bytes]:
        """Synthesize speech using fallback engine."""
        if not self._initialized:
            self._initialize()
        
        if not self._engine:
            logger.warning("TTS not available")
            return None
        
        try:
            # Adjust rate based on tone
            rate_map = {
                EmotionalTone.CALM: 120,  # Slower
                EmotionalTone.PROFESSIONAL: 150,  # Normal
                EmotionalTone.ENERGETIC: 180,  # Faster
                EmotionalTone.TECHNICAL: 140,  # Slightly slower
                EmotionalTone.REASSURING: 130  # Slower
            }
            
            self._engine.setProperty('rate', rate_map.get(tone, 150))
            
            if output_path:
                self._engine.save_to_file(text, output_path)
                self._engine.runAndWait()
                
                if return_bytes:
                    with open(output_path, 'rb') as f:
                        return f.read()
                return None
            else:
                # Can't return bytes directly with pyttsx3
                logger.warning("pyttsx3 doesn't support returning bytes. Use output_path.")
                return None
                
        except Exception as e:
            logger.error(f"Error in fallback TTS: {e}")
            return None


def get_tts_engine(use_fallback: bool = False) -> TTSEngine:
    """
    Get TTS engine instance.
    
    Args:
        use_fallback: If True, use fallback engine even if Coqui is available
    
    Returns:
        TTSEngine instance
    """
    if use_fallback:
        return TTSEngineFallback()
    
    try:
        return TTSEngine()
    except Exception as e:
        logger.warning(f"Coqui XTTS not available, using fallback: {e}")
        return TTSEngineFallback()

