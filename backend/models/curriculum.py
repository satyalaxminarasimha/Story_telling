"""
Curriculum Knowledge Base for mapping concepts to educational standards.
Simulates a vector DB / knowledge graph for curriculum alignment.
"""

import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class CurriculumTopic(BaseModel):
    """Model for a curriculum topic."""
    
    id: str
    name: str
    subject: str
    grade_range: str
    description: str
    keywords: list[str]
    learning_objectives: list[str]
    related_topics: list[str]
    story_themes: list[str]


class CurriculumKnowledgeBase:
    """
    Simulated curriculum knowledge base for mapping 
    detected concepts to educational content.
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the knowledge base."""
        self.topics: dict[str, CurriculumTopic] = {}
        self._load_data(data_path)
    
    def _load_data(self, data_path: Optional[Path] = None) -> None:
        """Load curriculum data from JSON file."""
        if data_path is None:
            data_path = Path(__file__).parent.parent / "data" / "curriculum_kb.json"
        
        if data_path.exists():
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for topic_data in data.get("topics", []):
                    topic = CurriculumTopic(**topic_data)
                    self.topics[topic.id] = topic
        else:
            # Initialize with default topics if file doesn't exist
            self._initialize_defaults()
    
    def _initialize_defaults(self) -> None:
        """Initialize with default curriculum topics."""
        default_topics = [
            CurriculumTopic(
                id="science_photosynthesis",
                name="Photosynthesis",
                subject="Science",
                grade_range="3-5",
                description="How plants make food using sunlight",
                keywords=["plant", "sun", "leaf", "green", "tree", "flower", "garden"],
                learning_objectives=[
                    "Understand how plants produce food",
                    "Learn about the role of sunlight in plant growth",
                    "Identify parts of a plant"
                ],
                related_topics=["plant_parts", "ecosystems", "food_chain"],
                story_themes=["magical garden", "talking plants", "sun adventure"]
            ),
            CurriculumTopic(
                id="science_water_cycle",
                name="Water Cycle",
                subject="Science",
                grade_range="2-4",
                description="The journey of water through evaporation, condensation, and precipitation",
                keywords=["water", "rain", "cloud", "river", "ocean", "drop", "wet"],
                learning_objectives=[
                    "Understand evaporation and condensation",
                    "Learn about precipitation",
                    "Trace water's journey"
                ],
                related_topics=["weather", "states_of_matter", "ecosystems"],
                story_themes=["raindrop journey", "cloud adventures", "river tales"]
            ),
            CurriculumTopic(
                id="math_shapes",
                name="Geometric Shapes",
                subject="Mathematics",
                grade_range="K-2",
                description="Basic 2D and 3D shapes and their properties",
                keywords=["circle", "square", "triangle", "rectangle", "shape", "round", "corner"],
                learning_objectives=[
                    "Identify basic shapes",
                    "Count sides and corners",
                    "Recognize shapes in everyday objects"
                ],
                related_topics=["measurement", "symmetry", "patterns"],
                story_themes=["shape kingdom", "geometry adventure", "pattern magic"]
            ),
            CurriculumTopic(
                id="science_animals",
                name="Animal Classification",
                subject="Science",
                grade_range="2-4",
                description="Grouping animals by their characteristics",
                keywords=["animal", "mammal", "bird", "fish", "reptile", "insect", "pet", "wild"],
                learning_objectives=[
                    "Classify animals into groups",
                    "Identify animal characteristics",
                    "Understand habitats"
                ],
                related_topics=["habitats", "food_chain", "life_cycles"],
                story_themes=["animal friends", "forest adventure", "ocean journey"]
            ),
            CurriculumTopic(
                id="science_space",
                name="Solar System",
                subject="Science",
                grade_range="3-5",
                description="Planets, stars, and space exploration",
                keywords=["planet", "star", "moon", "sun", "rocket", "space", "earth", "sky"],
                learning_objectives=[
                    "Name the planets in order",
                    "Understand day and night",
                    "Learn about the moon phases"
                ],
                related_topics=["gravity", "seasons", "earth_science"],
                story_themes=["space adventure", "planet exploration", "starlight journey"]
            ),
            CurriculumTopic(
                id="science_human_body",
                name="Human Body",
                subject="Science",
                grade_range="2-5",
                description="Body parts and their functions",
                keywords=["body", "heart", "brain", "bone", "muscle", "hand", "eye", "ear"],
                learning_objectives=[
                    "Identify major body parts",
                    "Understand organ functions",
                    "Learn about staying healthy"
                ],
                related_topics=["nutrition", "exercise", "senses"],
                story_themes=["body adventure", "health heroes", "sense exploration"]
            ),
            CurriculumTopic(
                id="social_community",
                name="Community Helpers",
                subject="Social Studies",
                grade_range="K-2",
                description="People who help in our community",
                keywords=["doctor", "teacher", "firefighter", "police", "nurse", "helper", "work"],
                learning_objectives=[
                    "Identify community helpers",
                    "Understand different jobs",
                    "Appreciate community service"
                ],
                related_topics=["citizenship", "safety", "family"],
                story_themes=["helper heroes", "community adventure", "job day"]
            ),
            CurriculumTopic(
                id="language_storytelling",
                name="Story Elements",
                subject="Language Arts",
                grade_range="1-3",
                description="Characters, setting, and plot in stories",
                keywords=["story", "book", "character", "hero", "adventure", "beginning", "end"],
                learning_objectives=[
                    "Identify story characters",
                    "Describe settings",
                    "Understand plot structure"
                ],
                related_topics=["reading", "writing", "vocabulary"],
                story_themes=["story within story", "character journey", "tale telling"]
            ),
        ]
        
        for topic in default_topics:
            self.topics[topic.id] = topic
    
    def find_matching_topics(
        self, 
        keywords: list[str], 
        max_results: int = 3
    ) -> list[CurriculumTopic]:
        """
        Find curriculum topics that match the given keywords.
        Simulates semantic search / vector similarity.
        """
        scores: dict[str, int] = {}
        
        # Normalize keywords
        normalized_keywords = [kw.lower().strip() for kw in keywords]
        
        for topic_id, topic in self.topics.items():
            score = 0
            topic_keywords = [kw.lower() for kw in topic.keywords]
            
            for kw in normalized_keywords:
                # Direct match
                if kw in topic_keywords:
                    score += 10
                # Partial match
                for topic_kw in topic_keywords:
                    if kw in topic_kw or topic_kw in kw:
                        score += 5
                # Name/description match
                if kw in topic.name.lower():
                    score += 8
                if kw in topic.description.lower():
                    score += 3
            
            if score > 0:
                scores[topic_id] = score
        
        # Sort by score and return top results
        sorted_topics = sorted(
            scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:max_results]
        
        return [self.topics[topic_id] for topic_id, _ in sorted_topics]
    
    def get_topic_by_id(self, topic_id: str) -> Optional[CurriculumTopic]:
        """Get a specific topic by ID."""
        return self.topics.get(topic_id)
    
    def get_all_topics(self) -> list[CurriculumTopic]:
        """Get all curriculum topics."""
        return list(self.topics.values())
    
    def get_story_themes(self, topic_ids: list[str]) -> list[str]:
        """Get story themes for given topics."""
        themes = []
        for topic_id in topic_ids:
            topic = self.topics.get(topic_id)
            if topic:
                themes.extend(topic.story_themes)
        return list(set(themes))


# Singleton instance
_kb_instance: Optional[CurriculumKnowledgeBase] = None


def get_curriculum_kb() -> CurriculumKnowledgeBase:
    """Get the singleton curriculum knowledge base instance."""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = CurriculumKnowledgeBase()
    return _kb_instance
