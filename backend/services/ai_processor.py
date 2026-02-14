"""
AI Processing Pipeline for multimodal input analysis.
Supports both OpenAI GPT-4o and Google Gemini for vision/text processing.
"""

import base64
import logging
from typing import Optional
from functools import lru_cache

from config import get_settings, Settings
from models.schemas import ImageAnalysisResult, InputType
from models.curriculum import get_curriculum_kb, CurriculumKnowledgeBase
from utils.retry import with_retry, APICallError, RateLimitError

logger = logging.getLogger(__name__)


class AIProcessor:
    """
    Multimodal AI processor for analyzing images and text.
    Supports OpenAI GPT-4o and Google Gemini APIs.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.ai_provider
        self.curriculum_kb = get_curriculum_kb()
        
        # Initialize the appropriate client
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "groq":
            self._init_groq()
        else:
            self._init_gemini()
    
    def _init_openai(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self.model = "gpt-4o"
            logger.info("Initialized OpenAI client with GPT-4o")
        except ImportError:
            logger.error("OpenAI package not installed")
            raise ImportError("openai package is required for OpenAI provider")
    
    def _init_gemini(self) -> None:
        """Initialize Google Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.google_api_key)
            self.client = genai.GenerativeModel("gemini-2.0-flash")
            self.model = "gemini-2.0-flash"
            logger.info("Initialized Google Gemini client")
        except ImportError:
            logger.error("Google GenerativeAI package not installed")
            raise ImportError("google-generativeai package is required for Gemini provider")
    
    def _init_groq(self) -> None:
        """Initialize Groq client."""
        try:
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.settings.groq_api_key)
            self.model = "llama-3.3-70b-versatile"
            self.vision_model = "llama-3.2-90b-vision-preview"
            logger.info("Initialized Groq client")
        except ImportError:
            logger.error("Groq package not installed")
            raise ImportError("groq package is required for Groq provider")
    
    @with_retry(max_attempts=3, min_wait=1.0, max_wait=10.0)
    async def analyze_image(
        self, 
        image_data: str, 
        input_type: InputType
    ) -> ImageAnalysisResult:
        """
        Analyze an image (sketch or diagram) using vision AI.
        
        Args:
            image_data: Base64-encoded image data
            input_type: Type of input (sketch or diagram)
        
        Returns:
            ImageAnalysisResult with detected objects and educational concepts
        """
        try:
            prompt = self._build_image_analysis_prompt(input_type)
            
            if self.provider == "openai":
                result = await self._analyze_with_openai(image_data, prompt)
            elif self.provider == "groq":
                result = await self._analyze_with_groq(image_data, prompt)
            else:
                result = await self._analyze_with_gemini(image_data, prompt)
            
            # Map to curriculum concepts
            enriched_result = self._enrich_with_curriculum(result)
            
            return enriched_result
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise APICallError(f"Image analysis failed: {str(e)}", provider=self.provider)
    
    def _build_image_analysis_prompt(self, input_type: InputType) -> str:
        """Build the prompt for image analysis."""
        base_prompt = """Analyze this image and provide educational insights for children.

Please identify:
1. Objects and elements visible in the image
2. The main scene or concept being depicted
3. Educational topics that could be taught using this image
4. Suggested curriculum topics (science, math, language arts, social studies)

Respond in JSON format:
{
    "detected_objects": ["list", "of", "objects"],
    "scene_description": "Brief description of the scene",
    "educational_concepts": ["concept1", "concept2"],
    "suggested_topics": ["topic1", "topic2"],
    "confidence": 0.0 to 1.0
}"""
        
        if input_type == InputType.SKETCH:
            return f"This is a child's sketch drawing.\n\n{base_prompt}"
        else:
            return f"This is a textbook diagram or educational image.\n\n{base_prompt}"
    
    async def _analyze_with_openai(
        self, 
        image_data: str, 
        prompt: str
    ) -> ImageAnalysisResult:
        """Analyze image using OpenAI GPT-4o Vision."""
        try:
            # Ensure proper base64 format
            if not image_data.startswith("data:"):
                image_data = f"data:image/png;base64,{image_data}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data}
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
            raise
    
    async def _analyze_with_gemini(
        self, 
        image_data: str, 
        prompt: str
    ) -> ImageAnalysisResult:
        """Analyze image using Google Gemini Vision."""
        import google.generativeai as genai
        
        try:
            # Decode base64 image
            if image_data.startswith("data:"):
                image_data = image_data.split(",", 1)[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Create image part
            image_part = {
                "mime_type": "image/png",
                "data": image_bytes
            }
            
            response = await self.client.generate_content_async(
                [prompt, image_part]
            )
            
            return self._parse_analysis_result(response.text)
            
        except Exception as e:
            if "quota" in str(e).lower():
                raise RateLimitError(f"Gemini rate limit exceeded: {e}")
            raise
    
    async def _analyze_with_groq(
        self, 
        image_data: str, 
        prompt: str
    ) -> ImageAnalysisResult:
        """Analyze image using Groq Vision (Llama 3.2 Vision)."""
        try:
            # Ensure proper base64 format
            if not image_data.startswith("data:"):
                image_data = f"data:image/png;base64,{image_data}"
            
            response = await self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data}
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            if "rate_limit" in str(e).lower():
                raise RateLimitError(f"Groq rate limit exceeded: {e}")
            raise
    
    def _parse_analysis_result(self, result_text: str) -> ImageAnalysisResult:
        """Parse the AI response into ImageAnalysisResult."""
        import json
        
        try:
            # Clean up the response if needed
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            data = json.loads(result_text)
            
            return ImageAnalysisResult(
                detected_objects=data.get("detected_objects", []),
                scene_description=data.get("scene_description", ""),
                educational_concepts=data.get("educational_concepts", []),
                suggested_topics=data.get("suggested_topics", []),
                confidence=float(data.get("confidence", 0.8))
            )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
            # Return a basic result
            return ImageAnalysisResult(
                detected_objects=["drawing"],
                scene_description=result_text[:200] if result_text else "Image analyzed",
                educational_concepts=["general learning"],
                suggested_topics=["creative expression"],
                confidence=0.5
            )
    
    def _enrich_with_curriculum(
        self, 
        result: ImageAnalysisResult
    ) -> ImageAnalysisResult:
        """Enrich the analysis result with curriculum mappings."""
        # Combine all keywords for curriculum matching
        keywords = (
            result.detected_objects + 
            result.educational_concepts + 
            result.suggested_topics
        )
        
        # Find matching curriculum topics
        matching_topics = self.curriculum_kb.find_matching_topics(keywords, max_results=3)
        
        if matching_topics:
            # Add curriculum-aligned topics
            curriculum_topics = [topic.name for topic in matching_topics]
            result.suggested_topics = list(set(result.suggested_topics + curriculum_topics))
            
            # Add learning objectives as educational concepts
            for topic in matching_topics:
                result.educational_concepts.extend(topic.learning_objectives[:2])
            
            result.educational_concepts = list(set(result.educational_concepts))
        
        return result
    
    @with_retry(max_attempts=3)
    async def process_keywords(
        self, 
        keywords: str
    ) -> ImageAnalysisResult:
        """
        Process keyword input to identify educational concepts.
        
        Args:
            keywords: User-provided keywords or topic description
        
        Returns:
            ImageAnalysisResult with identified concepts
        """
        # Split keywords
        keyword_list = [kw.strip() for kw in keywords.replace(",", " ").split()]
        
        # Find matching curriculum topics
        matching_topics = self.curriculum_kb.find_matching_topics(
            keyword_list, 
            max_results=3
        )
        
        if matching_topics:
            return ImageAnalysisResult(
                detected_objects=[],
                scene_description=f"Keywords: {keywords}",
                educational_concepts=[
                    obj for topic in matching_topics 
                    for obj in topic.learning_objectives[:2]
                ],
                suggested_topics=[topic.name for topic in matching_topics],
                confidence=0.9
            )
        
        # If no direct matches, use AI to interpret keywords
        return await self._interpret_keywords_with_ai(keywords)
    
    async def _interpret_keywords_with_ai(
        self, 
        keywords: str
    ) -> ImageAnalysisResult:
        """Use AI to interpret keywords and find educational concepts."""
        prompt = f"""Given these keywords or topic description: "{keywords}"

Identify educational concepts suitable for children (ages 5-13).

Respond in JSON format:
{{
    "detected_objects": [],
    "scene_description": "Brief description based on keywords",
    "educational_concepts": ["concept1", "concept2"],
    "suggested_topics": ["Math", "Science", "Language Arts", etc.],
    "confidence": 0.0 to 1.0
}}"""
        
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                result_text = response.choices[0].message.content
            elif self.provider == "groq":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500
                )
                result_text = response.choices[0].message.content
            else:
                response = await self.client.generate_content_async(
                    prompt
                )
                result_text = response.text
            
            return self._parse_analysis_result(result_text)
            
        except Exception as e:
            logger.error(f"Keyword interpretation failed: {e}")
            # Fallback response
            return ImageAnalysisResult(
                detected_objects=[],
                scene_description=f"Topic: {keywords}",
                educational_concepts=[keywords],
                suggested_topics=["General Learning"],
                confidence=0.5
            )


# Singleton instance
_processor_instance: Optional[AIProcessor] = None


def get_ai_processor() -> AIProcessor:
    """Get the singleton AI processor instance."""
    global _processor_instance
    if _processor_instance is None:
        settings = get_settings()
        _processor_instance = AIProcessor(settings)
    return _processor_instance
