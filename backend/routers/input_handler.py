"""
Input Handler Router for multimodal input processing.
Handles sketches, diagrams, and keyword inputs.
"""

import base64
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import ValidationError

from models.schemas import (
    InputType,
    StoryRequest,
    ImageAnalysisResult,
    ErrorResponse
)
from services.ai_processor import get_ai_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/input", tags=["Input Handler"])


@router.post(
    "/analyze",
    response_model=ImageAnalysisResult,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_input(request: StoryRequest) -> ImageAnalysisResult:
    """
    Analyze multimodal input (sketch, diagram, or keywords).
    
    This endpoint processes the input and identifies educational concepts
    that can be used for story generation.
    """
    try:
        processor = get_ai_processor()
        
        if request.input_type in [InputType.SKETCH, InputType.DIAGRAM]:
            if not request.image_data:
                raise HTTPException(
                    status_code=400,
                    detail="Image data is required for sketch/diagram input"
                )
            result = await processor.analyze_image(
                request.image_data,
                request.input_type
            )
        else:
            if not request.keywords:
                raise HTTPException(
                    status_code=400,
                    detail="Keywords are required for keyword input"
                )
            result = await processor.process_keywords(request.keywords)
        
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Input analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post(
    "/upload",
    response_model=ImageAnalysisResult,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def upload_and_analyze(
    file: UploadFile = File(..., description="Image file (PNG, JPG, JPEG)"),
    input_type: str = Form(default="diagram", description="Type: sketch or diagram"),
    age_group: str = Form(default="8-10", description="Target age group")
) -> ImageAnalysisResult:
    """
    Upload an image file and analyze it.
    
    Supports PNG, JPG, and JPEG image formats.
    """
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate input_type
    try:
        input_type_enum = InputType(input_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input_type. Must be 'sketch' or 'diagram'"
        )
    
    # Read and encode file
    try:
        content = await file.read()
        image_data = base64.b64encode(content).decode("utf-8")
        
        # Get processor and analyze
        processor = get_ai_processor()
        result = await processor.analyze_image(image_data, input_type_enum)
        
        return result
        
    except Exception as e:
        logger.error(f"File upload analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post(
    "/keywords",
    response_model=ImageAnalysisResult,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_keywords(
    keywords: str = Form(..., description="Keywords or topic description"),
    age_group: str = Form(default="8-10", description="Target age group")
) -> ImageAnalysisResult:
    """
    Analyze keywords or topic description.
    
    Identifies educational concepts from text input.
    """
    if not keywords or len(keywords.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Keywords must be at least 2 characters"
        )
    
    try:
        processor = get_ai_processor()
        result = await processor.process_keywords(keywords.strip())
        return result
        
    except Exception as e:
        logger.error(f"Keyword analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
