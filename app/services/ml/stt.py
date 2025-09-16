import base64
import io
import logging
import numpy as np
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available")

try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    logger.warning("Faster Whisper not available")


class STTService:
    def __init__(self, model_name: Optional[str] = None, use_faster_whisper: bool = True):
        self.model_name = model_name or settings.stt_model
        self.use_faster_whisper = use_faster_whisper
        self.model = None
        self.whisper_model = None
        
    async def load_model(self):
        """Load the Whisper model"""
        try:
            if self.use_faster_whisper and FASTER_WHISPER_AVAILABLE:
                logger.info(f"Loading Faster Whisper model: {self.model_name}")
                self.whisper_model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
                logger.info("Faster Whisper model loaded successfully")
            elif WHISPER_AVAILABLE:
                logger.info(f"Loading Whisper model: {self.model_name}")
                self.model = whisper.load_model(self.model_name)
                logger.info("Whisper model loaded successfully")
            else:
                raise ImportError("Neither Whisper nor Faster Whisper is available")
        except Exception as e:
            logger.error(f"Failed to load STT model: {e}")
            raise
    
    async def transcribe_audio(self, audio_data: bytes, format: str = "wav") -> Dict[str, Any]:
        """Transcribe audio data"""
        if not self.model and not self.whisper_model:
            await self.load_model()
        
        try:
            if self.whisper_model:
                return await self._transcribe_faster_whisper(audio_data, format)
            else:
                return await self._transcribe_whisper(audio_data, format)
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    async def transcribe_base64(self, audio_base64: str, format: str = "wav") -> Dict[str, Any]:
        """Transcribe base64 encoded audio"""
        try:
            audio_data = base64.b64decode(audio_base64)
            return await self.transcribe_audio(audio_data, format)
        except Exception as e:
            logger.error(f"Error decoding base64 audio: {e}")
            raise
    
    async def _transcribe_faster_whisper(self, audio_data: bytes, format: str) -> Dict[str, Any]:
        """Transcribe using Faster Whisper"""
        try:
            # Convert audio data to numpy array
            audio_array = self._bytes_to_numpy(audio_data, format)
            
            # Transcribe
            segments, info = self.whisper_model.transcribe(
                audio_array,
                beam_size=5,
                language="en"
            )
            
            # Collect segments
            transcript_segments = []
            full_text = ""
            
            for segment in segments:
                transcript_segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip(),
                    "avg_logprob": segment.avg_logprob,
                    "no_speech_prob": segment.no_speech_prob
                })
                full_text += segment.text + " "
            
            return {
                "text": full_text.strip(),
                "segments": transcript_segments,
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration
            }
        except Exception as e:
            logger.error(f"Error in Faster Whisper transcription: {e}")
            raise
    
    async def _transcribe_whisper(self, audio_data: bytes, format: str) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper"""
        try:
            # Save audio data to temporary file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe
                result = self.model.transcribe(temp_file_path)
                
                return {
                    "text": result["text"].strip(),
                    "segments": result.get("segments", []),
                    "language": result.get("language", "en"),
                    "duration": result.get("duration", 0)
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {e}")
            raise
    
    def _bytes_to_numpy(self, audio_data: bytes, format: str) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        try:
            import wave
            
            if format.lower() == "wav":
                # Read WAV file
                with io.BytesIO(audio_data) as audio_io:
                    with wave.open(audio_io, 'rb') as wav_file:
                        # Get audio parameters
                        frames = wav_file.readframes(wav_file.getnframes())
                        audio_array = np.frombuffer(frames, dtype=np.int16)
                        
                        # Convert to float32 and normalize
                        audio_array = audio_array.astype(np.float32) / 32768.0
                        
                        return audio_array
            else:
                raise ValueError(f"Unsupported audio format: {format}")
        except Exception as e:
            logger.error(f"Error converting audio to numpy: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "use_faster_whisper": self.use_faster_whisper,
            "loaded": self.model is not None or self.whisper_model is not None
        }


# Global instance
stt_service = STTService()
