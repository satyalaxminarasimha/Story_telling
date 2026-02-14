"""
Pydantic schemas for request/response validation.
Provides strict type safety for all API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from enum import Enum
import base64
import re


class InputType(str, Enum):
    """Supported input types for the multimodal handler."""
    SKETCH = "sketch"
    DIAGRAM = "diagram"
    KEYWORD = "keyword"


class StoryRequest(BaseModel):
    """Request model for story generation."""
    
    input_type: InputType = Field(
        ..., 
        description="Type of input: sketch, diagram, or keyword"
    )
    image_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded image data for sketches/diagrams"
    )
    keywords: Optional[str] = Field(
        default=None,
        description="Keywords for story generation",
        max_length=500
    )
    age_group: Literal["5-7", "8-10", "11-13"] = Field(
        default="8-10",
        description="Target age group for the story"
    )
    language: str = Field(
        default="en",
        description="Language code for the story",
        max_length=10
    )
    
    @field_validator("image_data")
    @classmethod
    def validate_image_data(cls, v: Optional[str]) -> Optional[str]:
        """Validate that image data is valid base64."""
        if v is None:
            return v
        
        # Remove data URI prefix if present
        if v.startswith("data:"):
            # Extract base64 part after the comma
            if "," in v:
                v = v.split(",", 1)[1]
        
        # Validate base64 format
        try:
            base64.b64decode(v, validate=True)
        except Exception:
            raise ValueError("Invalid base64 image data")
        
        return v
    
    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize and validate keywords."""
        if v is None:
            return v
        
        # Remove potentially dangerous characters
        v = re.sub(r'[<>{}[\]\\]', '', v)
        return v.strip()
    
    def model_post_init(self, __context) -> None:
        """Validate that either image or keywords is provided."""
        if self.input_type in [InputType.SKETCH, InputType.DIAGRAM]:
            if not self.image_data:
                raise ValueError(
                    f"image_data is required for input_type '{self.input_type.value}'"
                )
        elif self.input_type == InputType.KEYWORD:
            if not self.keywords:
                raise ValueError(
                    "keywords is required for input_type 'keyword'"
                )


class CurriculumConcept(BaseModel):
    """Model for curriculum-aligned concepts."""
    
    id: str = Field(..., description="Unique concept identifier")
    name: str = Field(..., description="Concept name")
    subject: str = Field(..., description="Subject area")
    grade_level: str = Field(..., description="Appropriate grade level")
    description: str = Field(..., description="Concept description")
    related_topics: list[str] = Field(
        default_factory=list,
        description="Related curriculum topics"
    )


class ImageAnalysisResult(BaseModel):
    """Result from AI image analysis."""
    
    detected_objects: list[str] = Field(
        default_factory=list,
        description="Objects detected in the image"
    )
    scene_description: str = Field(
        default="",
        description="Overall scene description"
    )
    educational_concepts: list[str] = Field(
        default_factory=list,
        description="Educational concepts identified"
    )
    suggested_topics: list[str] = Field(
        default_factory=list,
        description="Curriculum topics related to the image"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the analysis"
    )


class QuizQuestion(BaseModel):
    """Model for a single quiz question."""
    
    question: str = Field(..., description="The question text")
    options: list[str] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Four answer options"
    )
    correct_answer: int = Field(
        ...,
        ge=0,
        le=3,
        description="Index of the correct answer (0-3)"
    )
    explanation: str = Field(
        default="",
        description="Explanation of the correct answer"
    )


class QuizResponse(BaseModel):
    """Response model for quiz generation."""
    
    questions: list[QuizQuestion] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="List of quiz questions"
    )
    story_id: str = Field(..., description="Associated story ID")
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Quiz difficulty level"
    )


class StoryResponse(BaseModel):
    """Response model for generated stories."""
    
    story_id: str = Field(..., description="Unique story identifier")
    title: str = Field(..., description="Story title")
    content: str = Field(..., description="Full story content")
    summary: str = Field(..., description="Brief story summary")
    concepts_covered: list[str] = Field(
        default_factory=list,
        description="Educational concepts in the story"
    )
    age_group: str = Field(..., description="Target age group")
    word_count: int = Field(..., description="Story word count")
    quiz: Optional[QuizResponse] = Field(
        default=None,
        description="Generated quiz questions"
    )
    audio_available: bool = Field(
        default=False,
        description="Whether audio is available"
    )


class AudioRequest(BaseModel):
    """Request model for audio generation."""
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to convert to speech"
    )
    voice: Optional[str] = Field(
        default=None,
        description="Voice to use for TTS"
    )
    language: str = Field(
        default="en",
        description="Language code"
    )
    rate: Optional[str] = Field(
        default=None,
        description="Speech rate adjustment"
    )


class AudioResponse(BaseModel):
    """Response model for audio generation."""
    
    audio_id: str = Field(..., description="Unique audio identifier")
    audio_url: str = Field(..., description="URL to access the audio")
    duration_seconds: Optional[float] = Field(
        default=None,
        description="Audio duration in seconds"
    )
    format: str = Field(default="mp3", description="Audio format")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details"
    )
