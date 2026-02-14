"""
Multimodal Storytelling and Learning Platform - FastAPI Backend

A production-ready AI-powered platform for generating interactive,
curriculum-aligned stories from sketches, diagrams, and keywords.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import get_settings
from routers import input_router, story_router, audio_router
from models.schemas import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Multimodal Storytelling Platform...")
    settings = get_settings()
    logger.info(f"AI Provider: {settings.ai_provider}")
    logger.info(f"Debug Mode: {settings.debug}")
    
    # Create audio output directory
    audio_dir = Path(__file__).parent / "audio_output"
    audio_dir.mkdir(exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multimodal Storytelling Platform...")


# Create FastAPI application
app = FastAPI(
    title="Multimodal Storytelling Platform",
    description="""
    An AI-powered platform for generating interactive, curriculum-aligned stories
    from children's sketches, textbook diagrams, or keywords.
    
    ## Features
    - **Multimodal Input**: Process sketches, diagrams, and text keywords
    - **AI-Powered Analysis**: GPT-4o/Gemini vision for understanding input
    - **Curriculum Alignment**: Maps concepts to educational standards
    - **Story Generation**: Creates age-appropriate interactive narratives
    - **Quiz Generation**: Automatic MCQ creation based on story content
    - **Text-to-Speech**: Multilingual audio narration
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"path": str(request.url)}
        ).model_dump()
    )


# Include routers
app.include_router(input_router, prefix="/api")
app.include_router(story_router, prefix="/api")
app.include_router(audio_router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the service is healthy."""
    return {
        "status": "healthy",
        "service": "Multimodal Storytelling Platform",
        "version": "1.0.0"
    }


# API info endpoint
@app.get("/api", tags=["Info"])
async def api_info():
    """Get API information."""
    return {
        "name": "Multimodal Storytelling Platform API",
        "version": "1.0.0",
        "endpoints": {
            "input": "/api/input",
            "story": "/api/story",
            "audio": "/api/audio"
        },
        "documentation": "/docs"
    }


# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to the Multimodal Storytelling Platform",
        "documentation": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
