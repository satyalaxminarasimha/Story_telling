"""
Audio Router for text-to-speech functionality.
Handles audio generation and streaming.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse

from models.schemas import AudioRequest, AudioResponse, ErrorResponse
from services.speech_service import get_speech_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audio", tags=["Speech Synthesis"])


@router.post(
    "/generate",
    response_model=AudioResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_audio(request: AudioRequest) -> AudioResponse:
    """
    Generate audio from text using text-to-speech.
    
    Supports multiple languages and voices.
    """
    if not request.text or len(request.text.strip()) < 1:
        raise HTTPException(
            status_code=400,
            detail="Text is required for audio generation"
        )
    
    try:
        speech_service = get_speech_service()
        response = await speech_service.generate_audio(
            text=request.text,
            language=request.language,
            voice=request.voice,
            rate=request.rate
        )
        return response
        
    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")


@router.get(
    "/{audio_id}",
    response_class=FileResponse,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_audio(audio_id: str):
    """
    Retrieve a generated audio file by ID.
    """
    speech_service = get_speech_service()
    audio_file = speech_service.get_audio_file(audio_id)
    
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return FileResponse(
        path=audio_file,
        media_type="audio/mpeg",
        filename=f"{audio_id}.mp3"
    )


@router.post(
    "/stream",
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def stream_audio(request: AudioRequest):
    """
    Stream audio generation in real-time.
    
    Returns audio chunks as they are generated.
    """
    if not request.text or len(request.text.strip()) < 1:
        raise HTTPException(
            status_code=400,
            detail="Text is required for audio streaming"
        )
    
    try:
        speech_service = get_speech_service()
        
        async def audio_generator():
            async for chunk in speech_service.generate_audio_stream(
                text=request.text,
                language=request.language,
                voice=request.voice
            ):
                yield chunk
        
        return StreamingResponse(
            audio_generator(),
            media_type="audio/mpeg"
        )
        
    except Exception as e:
        logger.error(f"Audio streaming failed: {e}")
        raise HTTPException(status_code=500, detail=f"Audio streaming failed: {str(e)}")


@router.delete(
    "/{audio_id}",
    responses={
        404: {"model": ErrorResponse}
    }
)
async def delete_audio(audio_id: str):
    """
    Delete a generated audio file.
    """
    speech_service = get_speech_service()
    deleted = speech_service.delete_audio(audio_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Audio not found")
    
    return {"message": "Audio deleted successfully"}


@router.get("/voices/list")
async def list_voices(
    language: str = Query(default=None, description="Filter by language code")
):
    """
    List available TTS voices.
    """
    try:
        from services.speech_service import SpeechService
        voices = await SpeechService.list_available_voices()
        
        if language:
            voices = [v for v in voices if v["language"] == language]
        
        return {"voices": voices}
        
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_audio(
    max_age_hours: int = Query(default=24, ge=1, le=168)
):
    """
    Clean up old audio files.
    
    Admin endpoint to remove audio files older than the specified hours.
    """
    try:
        speech_service = get_speech_service()
        deleted_count = await speech_service.cleanup_old_files(max_age_hours)
        
        return {
            "message": f"Cleaned up {deleted_count} old audio files",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
