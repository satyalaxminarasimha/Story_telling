"""
Story Router for story generation and management.
Handles story creation, retrieval, and quiz generation.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError

from models.schemas import (
    InputType,
    StoryRequest,
    StoryResponse,
    QuizResponse,
    ImageAnalysisResult,
    ErrorResponse
)
from services.ai_processor import get_ai_processor
from services.story_engine import get_story_engine
from services.quiz_generator import get_quiz_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/story", tags=["Story Engine"])

# In-memory story cache (use Redis in production)
_story_cache: dict[str, StoryResponse] = {}


@router.post(
    "/generate",
    response_model=StoryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_story(request: StoryRequest) -> StoryResponse:
    """
    Generate an interactive story from multimodal input.
    
    This endpoint processes the input, identifies educational concepts,
    and generates a curriculum-aligned story with optional quiz.
    """
    try:
        # Step 1: Analyze input
        processor = get_ai_processor()
        
        if request.input_type in [InputType.SKETCH, InputType.DIAGRAM]:
            if not request.image_data:
                raise HTTPException(
                    status_code=400,
                    detail="Image data is required for sketch/diagram input"
                )
            analysis = await processor.analyze_image(
                request.image_data,
                request.input_type
            )
        else:
            if not request.keywords:
                raise HTTPException(
                    status_code=400,
                    detail="Keywords are required for keyword input"
                )
            analysis = await processor.process_keywords(request.keywords)
        
        # Step 2: Generate story
        story_engine = get_story_engine()
        story = await story_engine.generate_story(
            analysis,
            age_group=request.age_group,
            language=request.language
        )
        
        # Step 3: Generate quiz
        quiz_generator = get_quiz_generator()
        quiz = await quiz_generator.generate_quiz(story, num_questions=3)
        
        # Update story with quiz
        story.quiz = quiz
        
        # Cache the story
        _story_cache[story.story_id] = story
        
        return story
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


@router.post(
    "/from-analysis",
    response_model=StoryResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_story_from_analysis(
    analysis: ImageAnalysisResult,
    age_group: str = Query(default="8-10", description="Target age group"),
    language: str = Query(default="en", description="Story language"),
    include_quiz: bool = Query(default=True, description="Include quiz questions")
) -> StoryResponse:
    """
    Generate a story from a pre-analyzed input.
    
    Use this endpoint when you've already analyzed the input
    and want to generate a story from the analysis results.
    """
    try:
        # Generate story
        story_engine = get_story_engine()
        story = await story_engine.generate_story(
            analysis,
            age_group=age_group,
            language=language
        )
        
        # Generate quiz if requested
        if include_quiz:
            quiz_generator = get_quiz_generator()
            quiz = await quiz_generator.generate_quiz(story, num_questions=3)
            story.quiz = quiz
        
        # Cache the story
        _story_cache[story.story_id] = story
        
        return story
        
    except Exception as e:
        logger.error(f"Story generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Story generation failed: {str(e)}")


@router.get(
    "/{story_id}",
    response_model=StoryResponse,
    responses={
        404: {"model": ErrorResponse}
    }
)
async def get_story(story_id: str) -> StoryResponse:
    """
    Retrieve a previously generated story by ID.
    """
    story = _story_cache.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story


@router.post(
    "/{story_id}/quiz",
    response_model=QuizResponse,
    responses={
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def regenerate_quiz(
    story_id: str,
    num_questions: int = Query(default=3, ge=1, le=5)
) -> QuizResponse:
    """
    Regenerate quiz questions for an existing story.
    """
    story = _story_cache.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    try:
        quiz_generator = get_quiz_generator()
        quiz = await quiz_generator.generate_quiz(story, num_questions=num_questions)
        
        # Update cached story
        story.quiz = quiz
        _story_cache[story_id] = story
        
        return quiz
        
    except Exception as e:
        logger.error(f"Quiz regeneration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.get(
    "/",
    response_model=list[StoryResponse]
)
async def list_stories(
    limit: int = Query(default=10, ge=1, le=50)
) -> list[StoryResponse]:
    """
    List recently generated stories.
    """
    stories = list(_story_cache.values())
    return stories[:limit]
