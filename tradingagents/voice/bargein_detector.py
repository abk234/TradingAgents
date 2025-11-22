# Copyright (c) 2024. All rights reserved.
# Licensed under the Apache License, Version 2.0. See LICENSE file in the project root for license information.

"""
Barge-in Detection - Interrupt Eddie While Speaking

Eddie v2.0's barge-in system detects when the user speaks while Eddie is speaking,
allowing natural conversation flow with interruptions.
"""

import logging
from typing import Optional, Callable
from dataclasses import dataclass
import numpy as np
import io

logger = logging.getLogger(__name__)


@dataclass
class BargeInConfig:
    """Configuration for barge-in detection."""
    energy_threshold: float = 0.01  # Minimum audio energy to detect speech
    silence_duration: float = 0.3  # Seconds of silence before considering speech ended
    min_speech_duration: float = 0.1  # Minimum duration to consider as speech
    sample_rate: int = 16000
    chunk_size: int = 1024  # Audio chunk size in samples


class BargeInDetector:
    """
    Detects when user speaks while audio is playing (barge-in).
    
    Uses simple energy-based voice activity detection to detect
    when user starts speaking during TTS playback.
    """
    
    def __init__(self, config: Optional[BargeInConfig] = None):
        """
        Initialize barge-in detector.
        
        Args:
            config: Barge-in configuration
        """
        self.config = config or BargeInConfig()
        self.is_monitoring = False
        self.on_barge_in: Optional[Callable[[], None]] = None
        self.audio_buffer = []
        self.silence_samples = 0
    
    def start_monitoring(
        self,
        audio_stream: Optional[io.BytesIO] = None,
        on_barge_in: Optional[Callable[[], None]] = None
    ):
        """
        Start monitoring for barge-in.
        
        Args:
            audio_stream: Optional audio stream to monitor
            on_barge_in: Callback when barge-in is detected
        """
        self.is_monitoring = True
        self.on_barge_in = on_barge_in
        self.audio_buffer = []
        self.silence_samples = 0
        logger.info("Barge-in monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for barge-in."""
        self.is_monitoring = False
        self.audio_buffer = []
        self.silence_samples = 0
        logger.info("Barge-in monitoring stopped")
    
    def process_audio_chunk(self, audio_chunk: bytes) -> bool:
        """
        Process an audio chunk and detect barge-in.
        
        Args:
            audio_chunk: Audio data bytes
        
        Returns:
            True if barge-in detected, False otherwise
        """
        if not self.is_monitoring:
            return False
        
        try:
            # Convert audio bytes to numpy array
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Calculate energy (RMS)
            energy = np.sqrt(np.mean(audio_array ** 2))
            
            # Check if energy exceeds threshold (user is speaking)
            if energy > self.config.energy_threshold:
                self.silence_samples = 0
                
                # Check if we have enough consecutive speech samples
                self.audio_buffer.append(energy)
                
                # Keep buffer size manageable
                if len(self.audio_buffer) > 100:
                    self.audio_buffer.pop(0)
                
                # Detect barge-in if we have sustained speech
                if len(self.audio_buffer) >= int(self.config.min_speech_duration * self.config.sample_rate / self.config.chunk_size):
                    logger.info("Barge-in detected!")
                    if self.on_barge_in:
                        self.on_barge_in()
                    return True
            else:
                # Silence detected
                self.silence_samples += 1
                
                # Reset if too much silence
                if self.silence_samples > int(self.config.silence_duration * self.config.sample_rate / self.config.chunk_size):
                    self.audio_buffer = []
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing audio chunk for barge-in: {e}")
            return False
    
    def detect_from_microphone(self, audio_data: bytes) -> bool:
        """
        Detect barge-in from microphone audio data.
        
        Args:
            audio_data: Raw audio bytes from microphone
        
        Returns:
            True if barge-in detected
        """
        return self.process_audio_chunk(audio_data)


class BargeInManager:
    """
    Manages barge-in state and coordinates between TTS playback and STT monitoring.
    """
    
    def __init__(self):
        """Initialize barge-in manager."""
        self.detector = BargeInDetector()
        self.is_playing_audio = False
        self.current_audio: Optional[any] = None  # HTMLAudioElement or similar
        self.monitoring_stream: Optional[any] = None
    
    def start_audio_playback(self, audio_element: any):
        """
        Start audio playback and begin monitoring for barge-in.
        
        Args:
            audio_element: Audio element that's playing
        """
        self.is_playing_audio = True
        self.current_audio = audio_element
        
        # Start monitoring
        self.detector.start_monitoring(
            on_barge_in=self.handle_barge_in
        )
        
        logger.info("Audio playback started, barge-in monitoring active")
    
    def stop_audio_playback(self):
        """Stop audio playback and monitoring."""
        if self.current_audio:
            try:
                self.current_audio.pause()
                self.current_audio.currentTime = 0
            except:
                pass
        
        self.is_playing_audio = False
        self.current_audio = None
        self.detector.stop_monitoring()
        
        logger.info("Audio playback stopped")
    
    def handle_barge_in(self):
        """Handle barge-in detection."""
        logger.info("Barge-in detected - stopping audio playback")
        self.stop_audio_playback()
    
    def process_microphone_audio(self, audio_data: bytes) -> bool:
        """
        Process microphone audio for barge-in detection.
        
        Args:
            audio_data: Audio bytes from microphone
        
        Returns:
            True if barge-in detected
        """
        if self.is_playing_audio:
            return self.detector.detect_from_microphone(audio_data)
        return False


# Global instance
_bargein_manager: Optional[BargeInManager] = None


def get_bargein_manager() -> BargeInManager:
    """Get the global barge-in manager instance."""
    global _bargein_manager
    if _bargein_manager is None:
        _bargein_manager = BargeInManager()
    return _bargein_manager

