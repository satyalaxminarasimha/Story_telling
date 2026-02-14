"""Routers package for API endpoints."""

from .input_handler import router as input_router
from .story import router as story_router
from .audio import router as audio_router

__all__ = ["input_router", "story_router", "audio_router"]
