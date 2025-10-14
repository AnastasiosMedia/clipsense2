"""
Configuration management for ClipSense worker
Handles environment variables and default settings
"""

import os
from pathlib import Path
from typing import Optional
try:
    from dotenv import load_dotenv
    # Load .env from project root if present, then worker dir as fallback
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root.joinpath('.env'))
    load_dotenv(Path(__file__).resolve().parent.joinpath('.env'))
except Exception:
    # dotenv not installed or other non-fatal error; environment variables can still be provided by shell
    pass

class Config:
    """Configuration class for ClipSense worker"""
    
    # Server settings
    WORKER_HOST: str = os.getenv("WORKER_HOST", "127.0.0.1")
    WORKER_PORT: int = int(os.getenv("WORKER_PORT", "8123"))
    MAX_PORT_RETRIES: int = int(os.getenv("MAX_PORT_RETRIES", "3"))
    PORT_RETRY_DELAY: int = int(os.getenv("PORT_RETRY_DELAY", "2"))
    
    # FFmpeg settings
    FFMPEG_PRESET: str = os.getenv("FFMPEG_PRESET", "ultrafast")
    FFMPEG_CRF: str = os.getenv("FFMPEG_CRF", "28")
    FFMPEG_AUDIO_BITRATE: str = os.getenv("FFMPEG_AUDIO_BITRATE", "96k")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_TIMING_LOGS: bool = os.getenv("ENABLE_TIMING_LOGS", "true").lower() == "true"
    
    # Vision (OpenAI) integration
    USE_OPENAI_VISION: bool = os.getenv("USE_OPENAI_VISION", "false").lower() == "true"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
    
    @classmethod
    def get_ffmpeg_proxy_settings(cls) -> dict:
        """Get optimized FFmpeg settings for proxy creation"""
        return {
            "preset": cls.FFMPEG_PRESET,
            "crf": cls.FFMPEG_CRF,
            "audio_bitrate": cls.FFMPEG_AUDIO_BITRATE,
            "scale_filter": "scale='min(1280,iw)':-2"
        }
