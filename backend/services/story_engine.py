"""
Interactive Story Engine for generating age-appropriate educational stories.
Uses AI to create engaging narratives aligned with curriculum concepts.
"""

import uuid
import logging
from typing import Optional
from functools import lru_cache

from config import get_settings, Settings
from models.schemas import (
    StoryResponse, 
    ImageAnalysisResult, 
    QuizResponse
)
from models.curriculum import get_curriculum_kb
from utils.retry import with_retry, APICallError

logger = logging.getLogger(__name__)


class StoryEngine:
    """
    Engine for generating interactive, curriculum-aligned stories.
    Creates age-appropriate narratives based on visual or keyword input.
    """
    
    # Age-appropriate settings
    AGE_SETTINGS = {
        "5-7": {
            "word_count": (150, 300),
            "vocabulary": "simple",
            "sentence_length": "short",
            "complexity": "basic",
            "themes": ["friendship", "family", "animals", "nature", "helping others"]
        },
        "8-10": {
            "word_count": (300, 500),
            "vocabulary": "intermediate",
            "sentence_length": "medium",
            "complexity": "moderate",
            "themes": ["adventure", "teamwork", "problem-solving", "curiosity", "courage"]
        },
        "11-13": {
            "word_count": (500, 800),
            "vocabulary": "advanced",
            "sentence_length": "varied",
            "complexity": "nuanced",
            "themes": ["discovery", "challenges", "identity", "innovation", "responsibility"]
        }
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.ai_provider
        self.curriculum_kb = get_curriculum_kb()
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the AI client."""
        if self.provider == "openai":
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            self.model = "gpt-4o"
        elif self.provider == "groq":
            from groq import AsyncGroq
            self.client = AsyncGroq(api_key=self.settings.groq_api_key)
            self.model = "llama-3.3-70b-versatile"
        else:
            import google.generativeai as genai
            genai.configure(api_key=self.settings.google_api_key)
            self.client = genai.GenerativeModel("gemini-2.0-flash")
            self.model = "gemini-2.0-flash"
    
    @with_retry(max_attempts=3)
    async def generate_story(
        self,
        analysis_result: ImageAnalysisResult,
        age_group: str = "8-10",
        language: str = "en"
    ) -> StoryResponse:
        """
        Generate an educational story based on the analysis result.
        
        Args:
            analysis_result: Result from image/keyword analysis
            age_group: Target age group
            language: Language code
        
        Returns:
            StoryResponse with generated story content
        """
        story_id = str(uuid.uuid4())
        age_settings = self.AGE_SETTINGS.get(age_group, self.AGE_SETTINGS["8-10"])
        
        # Build the story prompt
        prompt = self._build_story_prompt(analysis_result, age_settings, language)
        
        try:
            if self.provider == "openai":
                story_data = await self._generate_with_openai(prompt)
            elif self.provider == "groq":
                story_data = await self._generate_with_groq(prompt)
            else:
                story_data = await self._generate_with_gemini(prompt)
            
            # Parse the response
            title, content, summary = self._parse_story_response(story_data)
            
            # Count words
            word_count = len(content.split())
            
            return StoryResponse(
                story_id=story_id,
                title=title,
                content=content,
                summary=summary,
                concepts_covered=analysis_result.educational_concepts[:5],
                age_group=age_group,
                word_count=word_count,
                quiz=None,
                audio_available=False
            )
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            raise APICallError(f"Story generation failed: {str(e)}")
    
    def _build_story_prompt(
        self,
        analysis: ImageAnalysisResult,
        age_settings: dict,
        language: str
    ) -> str:
        """Build the prompt for story generation."""
        min_words, max_words = age_settings["word_count"]
        
        # Get story themes from curriculum
        topic_themes = []
        for topic_name in analysis.suggested_topics:
            matching = self.curriculum_kb.find_matching_topics([topic_name], max_results=1)
            if matching:
                topic_themes.extend(matching[0].story_themes)
        
        themes = topic_themes[:3] if topic_themes else age_settings["themes"][:3]
        
        prompt = f"""Create an engaging educational story for children aged {age_settings['word_count']}.

**Input Context:**
- Scene/Topic: {analysis.scene_description}
- Objects/Elements: {', '.join(analysis.detected_objects) if analysis.detected_objects else 'Not specified'}
- Educational Concepts to Include: {', '.join(analysis.educational_concepts[:3])}
- Suggested Themes: {', '.join(themes)}

**Story Requirements:**
- Length: {min_words}-{max_words} words
- Vocabulary Level: {age_settings['vocabulary']}
- Sentence Complexity: {age_settings['sentence_length']}
- Language: {language}

**Guidelines:**
1. Create a fun, engaging narrative with relatable characters
2. Naturally weave in educational concepts from the list above
3. Include a clear beginning, middle, and end
4. Add age-appropriate dialogue and descriptions
5. End with a positive message or learning takeaway
6. Make it interactive by asking the reader questions occasionally

**Output Format:**
Provide your response in this exact format:

TITLE: [Creative, engaging title]

STORY:
[Full story content here]

SUMMARY:
[2-3 sentence summary of the story and its educational value]
"""
        
        return prompt
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate story using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative children's story writer who creates engaging, educational stories. Your stories are fun, imaginative, and teach valuable lessons."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        return response.choices[0].message.content
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate story using Google Gemini."""
        import google.generativeai as genai
        
        response = await self.client.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.8,
                max_output_tokens=2000
            )
        )
        return response.text
    
    async def _generate_with_groq(self, prompt: str) -> str:
        """Generate story using Groq."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative children's story writer who creates engaging, educational stories. Your stories are fun, imaginative, and teach valuable lessons."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.8
        )
        return response.choices[0].message.content
    
    def _parse_story_response(self, response: str) -> tuple[str, str, str]:
        """Parse the AI response into title, content, and summary."""
        title = "An Amazing Adventure"
        content = response
        summary = ""
        
        lines = response.strip().split("\n")
        
        # Find title
        for i, line in enumerate(lines):
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
                break
            elif line.upper().startswith("# "):
                title = line[2:].strip()
                break
        
        # Find story content
        story_start = -1
        story_end = len(lines)
        
        for i, line in enumerate(lines):
            if "STORY:" in line.upper():
                story_start = i + 1
            elif "SUMMARY:" in line.upper() and story_start >= 0:
                story_end = i
                break
        
        if story_start >= 0:
            content = "\n".join(lines[story_start:story_end]).strip()
        
        # Find summary
        for i, line in enumerate(lines):
            if "SUMMARY:" in line.upper():
                summary = "\n".join(lines[i+1:]).strip()
                break
        
        # If no summary found, generate one
        if not summary:
            words = content.split()[:50]
            summary = " ".join(words) + "..."
        
        return title, content, summary
    
    async def enhance_story_with_interactivity(
        self,
        story: StoryResponse
    ) -> StoryResponse:
        """
        Add interactive elements to the story.
        This can include questions, choices, or activities.
        """
        # For now, return the story as-is
        # Future enhancement: Add interactive breakpoints
        return story


# Singleton instance
_engine_instance: Optional[StoryEngine] = None


def get_story_engine() -> StoryEngine:
    """Get the singleton story engine instance."""
    global _engine_instance
    if _engine_instance is None:
        settings = get_settings()
        _engine_instance = StoryEngine(settings)
    return _engine_instance
