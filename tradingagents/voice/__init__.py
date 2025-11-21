"""
Voice Module - Eddie v2.0

Text-to-Speech capabilities with emotional tone injection.
"""

from .tts_engine import (
    TTSEngine,
    TTSEngineFallback,
    EmotionalTone,
    TTSConfig,
    get_tts_engine
)

from .tone_detector import (
    ToneDetector,
    get_tone_detector
)

from .stt_engine import (
    STTEngine,
    STTEngineFallback,
    STTConfig,
    get_stt_engine
)

from .bargein_detector import (
    BargeInDetector,
    BargeInManager,
    BargeInConfig,
    get_bargein_manager
)

__all__ = [
    # TTS
    'TTSEngine',
    'TTSEngineFallback',
    'EmotionalTone',
    'TTSConfig',
    'get_tts_engine',
    'ToneDetector',
    'get_tone_detector',
    
    # STT
    'STTEngine',
    'STTEngineFallback',
    'STTConfig',
    'get_stt_engine',
    
    # Barge-in
    'BargeInDetector',
    'BargeInManager',
    'BargeInConfig',
    'get_bargein_manager',
]

