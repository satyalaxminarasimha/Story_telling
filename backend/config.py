"""
Configuration management using Pydantic Settings.
Loads environment variables with validation and defaults.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # AI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    google_api_key: str = Field(default="", description="Google Gemini API Key")
    groq_api_key: str = Field(default="", description="Groq API Key")
    ai_provider: Literal["openai", "gemini", "groq"] = Field(
        default="openai", 
        description="AI provider to use"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated CORS origins"
    )
    
    # TTS Configuration
    tts_voice: str = Field(default="en-US-AriaNeural", description="TTS voice")
    tts_rate: str = Field(default="+0%", description="TTS speech rate")
    tts_volume: str = Field(default="+0%", description="TTS volume")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_api_key(self) -> str:
        """Get the appropriate API key based on provider."""
        if self.ai_provider == "openai":
            return self.openai_api_key
        elif self.ai_provider == "groq":
            return self.groq_api_key
        return self.google_api_key
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
