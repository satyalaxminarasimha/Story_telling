"""
Quiz Generator Module for creating educational assessments.
Automatically generates MCQs based on story content.
"""

import json
import logging
from typing import Optional
from functools import lru_cache

from config import get_settings, Settings
from models.schemas import QuizQuestion, QuizResponse, StoryResponse
from utils.retry import with_retry, APICallError

logger = logging.getLogger(__name__)


class QuizGenerator:
    """
    Generates curriculum-aligned multiple choice questions
    based on story content and educational concepts.
    """
    
    # Difficulty settings by age group
    DIFFICULTY_MAP = {
        "5-7": "easy",
        "8-10": "medium",
        "11-13": "hard"
    }
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = settings.ai_provider
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
    async def generate_quiz(
        self,
        story: StoryResponse,
        num_questions: int = 3
    ) -> QuizResponse:
        """
        Generate quiz questions based on story content.
        
        Args:
            story: The generated story
            num_questions: Number of questions to generate (1-5)
        
        Returns:
            QuizResponse with MCQ questions
        """
        num_questions = max(1, min(5, num_questions))
        difficulty = self.DIFFICULTY_MAP.get(story.age_group, "medium")
        
        prompt = self._build_quiz_prompt(story, num_questions, difficulty)
        
        try:
            if self.provider == "openai":
                quiz_data = await self._generate_with_openai(prompt)
            elif self.provider == "groq":
                quiz_data = await self._generate_with_groq(prompt)
            else:
                quiz_data = await self._generate_with_gemini(prompt)
            
            questions = self._parse_quiz_response(quiz_data)
            
            # Ensure we have the right number of questions
            if len(questions) < num_questions:
                logger.warning(
                    f"Generated {len(questions)} questions instead of {num_questions}"
                )
            
            return QuizResponse(
                questions=questions[:num_questions],
                story_id=story.story_id,
                difficulty=difficulty
            )
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            raise APICallError(f"Quiz generation failed: {str(e)}")
    
    def _build_quiz_prompt(
        self,
        story: StoryResponse,
        num_questions: int,
        difficulty: str
    ) -> str:
        """Build the prompt for quiz generation."""
        
        difficulty_guidelines = {
            "easy": "Use simple vocabulary, clear questions, and obvious correct answers.",
            "medium": "Use grade-appropriate vocabulary with some reasoning required.",
            "hard": "Include inference questions and require deeper understanding."
        }
        
        return f"""Create {num_questions} multiple-choice questions based on this story.

**Story Title:** {story.title}

**Story Content:**
{story.content}

**Concepts Covered:** {', '.join(story.concepts_covered)}

**Quiz Requirements:**
- Difficulty Level: {difficulty}
- {difficulty_guidelines.get(difficulty, '')}
- Each question must have exactly 4 options
- Only one correct answer per question
- Include an explanation for each correct answer
- Questions should test comprehension and learning

**Output Format (JSON):**
{{
    "questions": [
        {{
            "question": "The question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Why this answer is correct"
        }}
    ]
}}

Important: 
- correct_answer is the index (0-3) of the correct option
- Make questions engaging and educational
- Ensure all options are plausible but only one is correct
"""
    
    async def _generate_with_openai(self, prompt: str) -> str:
        """Generate quiz using OpenAI."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assessment expert who creates engaging, age-appropriate quiz questions for children."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Generate quiz using Google Gemini."""
        import google.generativeai as genai
        
        response = await self.client.generate_content_async(
            prompt
        )
        return response.text
    
    async def _generate_with_groq(self, prompt: str) -> str:
        """Generate quiz using Groq."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assessment expert who creates engaging, age-appropriate quiz questions for children."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _parse_quiz_response(self, response: str) -> list[QuizQuestion]:
        """Parse the AI response into QuizQuestion objects."""
        questions = []
        
        try:
            # Clean up response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            data = json.loads(response)
            
            for q_data in data.get("questions", []):
                # Validate question structure
                if not all(key in q_data for key in ["question", "options", "correct_answer"]):
                    continue
                
                options = q_data["options"]
                if len(options) != 4:
                    # Pad or trim options
                    while len(options) < 4:
                        options.append("Not applicable")
                    options = options[:4]
                
                correct_idx = int(q_data["correct_answer"])
                if correct_idx < 0 or correct_idx > 3:
                    correct_idx = 0
                
                questions.append(QuizQuestion(
                    question=q_data["question"],
                    options=options,
                    correct_answer=correct_idx,
                    explanation=q_data.get("explanation", "")
                ))
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quiz JSON: {e}")
            # Return fallback question
            questions.append(QuizQuestion(
                question="What did you learn from this story?",
                options=[
                    "Something new and interesting",
                    "I'm not sure",
                    "Nothing new",
                    "I need to read it again"
                ],
                correct_answer=0,
                explanation="Every story teaches us something new!"
            ))
        
        return questions
    
    async def validate_quiz(self, quiz: QuizResponse) -> bool:
        """
        Validate that the quiz questions are appropriate and correct.
        """
        for question in quiz.questions:
            # Check that correct_answer index is valid
            if question.correct_answer < 0 or question.correct_answer >= len(question.options):
                return False
            
            # Check that all options are non-empty
            if any(not opt.strip() for opt in question.options):
                return False
            
            # Check that question is non-empty
            if not question.question.strip():
                return False
        
        return True


# Singleton instance
_generator_instance: Optional[QuizGenerator] = None


def get_quiz_generator() -> QuizGenerator:
    """Get the singleton quiz generator instance."""
    global _generator_instance
    if _generator_instance is None:
        settings = get_settings()
        _generator_instance = QuizGenerator(settings)
    return _generator_instance
