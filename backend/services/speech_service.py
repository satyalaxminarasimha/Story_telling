"""
Speech Synthesis Service for multilingual text-to-speech.
Uses Edge-TTS for high-quality, multilingual speech synthesis.
"""

import asyncio
import uuid
import os
import logging
from pathlib import Path
from typing import Optional
from functools import lru_cache

import edge_tts

from config import get_settings, Settings
from models.schemas import AudioResponse
from utils.retry import with_retry, APICallError

logger = logging.getLogger(__name__)


class SpeechService:
    """
    Text-to-speech service using Edge-TTS.
    Supports multiple languages and voices.
    """
    
    # Language to voice mapping
    VOICE_MAP = {
        "en": "en-US-AriaNeural",
        "en-US": "en-US-AriaNeural",
        "en-GB": "en-GB-SoniaNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "it": "it-IT-ElsaNeural",
        "pt": "pt-BR-FranciscaNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "hi": "hi-IN-SwaraNeural",
        "ar": "ar-SA-ZariyahNeural",
        "ru": "ru-RU-SvetlanaNeural",
    }
    
    # Child-friendly voices
    CHILD_VOICES = {
        "en": "en-US-AnaNeural",
        "es": "es-MX-DaliaNeural",
        "fr": "fr-FR-EloiseNeural",
        "de": "de-DE-GiselaNeural",
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.default_voice = settings.tts_voice
        self.default_rate = settings.tts_rate
        self.default_volume = settings.tts_volume
        
        # Create audio output directory
        self.audio_dir = Path(__file__).parent.parent / "audio_output"
        self.audio_dir.mkdir(exist_ok=True)
    
    async def generate_audio(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        rate: Optional[str] = None,
        use_child_voice: bool = True
    ) -> AudioResponse:
        """
        Generate audio from text using Edge-TTS.
        
        Args:
            text: Text to convert to speech
            language: Language code
            voice: Specific voice to use (optional)
            rate: Speech rate adjustment (e.g., "+10%", "-20%")
            use_child_voice: Whether to use child-friendly voices
        
        Returns:
            AudioResponse with audio file information
        """
        audio_id = str(uuid.uuid4())
        output_file = self.audio_dir / f"{audio_id}.mp3"
        
        # Determine voice to use
        if voice:
            selected_voice = voice
        elif use_child_voice and language in self.CHILD_VOICES:
            selected_voice = self.CHILD_VOICES[language]
        else:
            selected_voice = self.VOICE_MAP.get(language, self.default_voice)
        
        # Determine speech rate
        selected_rate = rate or self.default_rate
        
        try:
            # Create TTS communicate object
            communicate = edge_tts.Communicate(
                text,
                selected_voice,
                rate=selected_rate,
                volume=self.default_volume
            )
            
            # Generate audio file
            await communicate.save(str(output_file))
            
            # Get file info
            file_size = output_file.stat().st_size
            # Estimate duration (rough estimate: ~16KB per second for MP3)
            estimated_duration = file_size / 16000
            
            return AudioResponse(
                audio_id=audio_id,
                audio_url=f"/api/audio/{audio_id}",
                duration_seconds=round(estimated_duration, 2),
                format="mp3"
            )
            
        except Exception as e:
            logger.warning(f"Edge-TTS failed, trying gTTS fallback: {e}")
            # Try gTTS fallback
            return await self._generate_with_gtts(text, language, audio_id, output_file)
    
    async def _generate_with_gtts(
        self,
        text: str,
        language: str,
        audio_id: str,
        output_file: Path
    ) -> AudioResponse:
        """Fallback to gTTS when Edge-TTS fails."""
        try:
            from gtts import gTTS
            import asyncio
            
            # Map language codes
            lang_map = {
                "en-US": "en", "en-GB": "en", "es": "es", "fr": "fr",
                "de": "de", "it": "it", "pt": "pt", "zh": "zh-CN",
                "ja": "ja", "ko": "ko", "hi": "hi", "ar": "ar", "ru": "ru"
            }
            gtts_lang = lang_map.get(language, language.split("-")[0] if "-" in language else language)
            
            # Run gTTS in thread pool (it's synchronous)
            def generate():
                tts = gTTS(text=text, lang=gtts_lang, slow=False)
                tts.save(str(output_file))
            
            await asyncio.get_event_loop().run_in_executor(None, generate)
            
            # Get file info
            file_size = output_file.stat().st_size
            estimated_duration = file_size / 16000
            
            return AudioResponse(
                audio_id=audio_id,
                audio_url=f"/api/audio/{audio_id}",
                duration_seconds=round(estimated_duration, 2),
                format="mp3"
            )
            
        except Exception as e:
            logger.error(f"gTTS fallback also failed: {e}")
            if output_file.exists():
                output_file.unlink()
            raise APICallError(f"Audio generation failed: {str(e)}")
    
    async def generate_audio_stream(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ):
        """
        Generate audio as a stream (for real-time playback).
        
        Yields audio chunks as they are generated.
        """
        selected_voice = voice or self.VOICE_MAP.get(language, self.default_voice)
        
        communicate = edge_tts.Communicate(
            text,
            selected_voice,
            rate=self.default_rate
        )
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    
    def get_audio_file(self, audio_id: str) -> Optional[Path]:
        """
        Get the path to an audio file by ID.
        
        Args:
            audio_id: The audio file identifier
        
        Returns:
            Path to the audio file, or None if not found
        """
        audio_file = self.audio_dir / f"{audio_id}.mp3"
        if audio_file.exists():
            return audio_file
        return None
    
    def delete_audio(self, audio_id: str) -> bool:
        """
        Delete an audio file.
        
        Args:
            audio_id: The audio file identifier
        
        Returns:
            True if deleted, False if not found
        """
        audio_file = self.audio_dir / f"{audio_id}.mp3"
        if audio_file.exists():
            audio_file.unlink()
            return True
        return False
    
    async def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old audio files.
        
        Args:
            max_age_hours: Maximum age of files to keep
        
        Returns:
            Number of files deleted
        """
        import time
        
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for audio_file in self.audio_dir.glob("*.mp3"):
            file_age = current_time - audio_file.stat().st_mtime
            if file_age > max_age_seconds:
                audio_file.unlink()
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old audio files")
        return deleted_count
    
    @staticmethod
    async def list_available_voices() -> list[dict]:
        """
        List all available voices from Edge-TTS.
        
        Returns:
            List of voice information dictionaries
        """
        voices = await edge_tts.list_voices()
        return [
            {
                "name": v["Name"],
                "short_name": v["ShortName"],
                "gender": v["Gender"],
                "locale": v["Locale"],
                "language": v["Locale"].split("-")[0]
            }
            for v in voices
        ]


# Singleton instance
_service_instance: Optional[SpeechService] = None


def get_speech_service() -> SpeechService:
    """Get the singleton speech service instance."""
    global _service_instance
    if _service_instance is None:
        settings = get_settings()
        _service_instance = SpeechService(settings)
    return _service_instance
