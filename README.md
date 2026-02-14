# Multimodal Storytelling and Learning Platform

An AI-powered educational platform that generates interactive, curriculum-aligned stories from children's sketches, textbook diagrams, or keywords. The system uses advanced multimodal AI (GPT-4o or Google Gemini) to understand visual and text inputs, then creates engaging narratives with automated quizzes and text-to-speech narration.

![Platform Overview](https://img.shields.io/badge/Platform-Educational-blue)
![AI Powered](https://img.shields.io/badge/AI-GPT--4o%20%7C%20Gemini-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### Core Modules

1. **Multimodal Input Handler**
   - 🎨 **Drawing Canvas**: HTML5 canvas for children to create sketches
   - 📷 **Image Upload**: Support for textbook diagrams and photos
   - ⌨️ **Keyword Input**: Text-based topic selection

2. **AI Processing Pipeline**
   - Vision analysis using GPT-4o or Gemini
   - Automatic concept extraction and curriculum mapping
   - Educational content alignment

3. **Interactive Story Engine**
   - Age-appropriate story generation (5-7, 8-10, 11-13 years)
   - Curriculum-aligned narratives
   - Multiple language support

4. **Assessment Module**
   - Automatic MCQ generation based on story content
   - Difficulty levels matching age groups
   - Instant feedback and explanations

5. **Speech Synthesis**
   - Multilingual text-to-speech using Edge-TTS
   - Child-friendly voices
   - Audio playback controls

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React.js)                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐              │
│  │  Drawing  │  │   File    │  │  Keyword  │              │
│  │  Canvas   │  │  Upload   │  │   Input   │              │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘              │
│        │              │              │                      │
│        └──────────────┴──────────────┘                      │
│                       │                                      │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Story Display + Quiz Module             │   │
│  │                   + Audio Player                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ API Calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   API Routers                        │   │
│  │  /input  │  /story  │  /audio                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Services                          │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ AI Processor │  │ Story Engine │                 │   │
│  │  │   (Vision)   │  │ (Generation) │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │    Quiz      │  │   Speech     │                 │   │
│  │  │  Generator   │  │   Service    │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │             Curriculum Knowledge Base                │   │
│  │              (JSON / Vector DB)                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ API Calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  External AI Services                        │
│        OpenAI GPT-4o  │  Google Gemini  │  Edge-TTS         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Story_telling/
├── README.md
├── .env.example
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── components/
│       │   ├── DrawingCanvas.tsx
│       │   ├── FileUpload.tsx
│       │   ├── KeywordInput.tsx
│       │   ├── StoryDisplay.tsx
│       │   ├── QuizModule.tsx
│       │   ├── AudioPlayer.tsx
│       │   └── InputHandler.tsx
│       ├── services/
│       │   └── api.ts
│       ├── types/
│       │   └── index.ts
│       └── hooks/
│           └── useStoryGeneration.ts
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── curriculum.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_processor.py
│   │   ├── story_engine.py
│   │   ├── quiz_generator.py
│   │   └── speech_service.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── input_handler.py
│   │   ├── story.py
│   │   └── audio.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── retry.py
│   └── data/
│       └── curriculum_kb.json
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **OpenAI API Key** or **Google Gemini API Key**

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (copy from `.env.example`):
   ```bash
   cp ../.env.example .env
   ```

5. Configure your API keys in `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   AI_PROVIDER=openai  # or "gemini"
   ```

6. Start the backend server:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 📖 API Documentation

### Endpoints

#### Input Handler

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/input/analyze` | Analyze multimodal input |
| POST | `/api/input/upload` | Upload and analyze image |
| POST | `/api/input/keywords` | Analyze keywords |

#### Story Engine

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/story/generate` | Generate story from input |
| POST | `/api/story/from-analysis` | Generate from analysis result |
| GET | `/api/story/{story_id}` | Get story by ID |
| POST | `/api/story/{story_id}/quiz` | Regenerate quiz |
| GET | `/api/story/` | List recent stories |

#### Audio Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/audio/generate` | Generate audio from text |
| GET | `/api/audio/{audio_id}` | Get audio file |
| POST | `/api/audio/stream` | Stream audio generation |
| GET | `/api/audio/voices/list` | List available voices |

### Request/Response Examples

#### Generate Story

**Request:**
```json
{
  "input_type": "keyword",
  "keywords": "dinosaurs, fossils, prehistoric",
  "age_group": "8-10",
  "language": "en"
}
```

**Response:**
```json
{
  "story_id": "uuid",
  "title": "The Fossil Hunter's Discovery",
  "content": "Once upon a time...",
  "summary": "A story about discovering dinosaur fossils...",
  "concepts_covered": ["paleontology", "fossils", "dinosaurs"],
  "age_group": "8-10",
  "word_count": 450,
  "quiz": {
    "questions": [...],
    "story_id": "uuid",
    "difficulty": "medium"
  },
  "audio_available": false
}
```

## 🎨 Features in Detail

### Drawing Canvas
- Multiple brush sizes and colors
- Eraser tool
- Undo/Redo functionality
- Download drawing as PNG
- Touch support for tablets

### Story Generation
- Age-appropriate vocabulary and complexity
- Curriculum-aligned educational content
- Multiple language support
- Interactive narrative elements

### Quiz System
- Automatic question generation
- Multiple choice format (4 options)
- Instant feedback with explanations
- Score tracking and summary

### Text-to-Speech
- 14+ language support
- Child-friendly voice options
- Adjustable playback speed
- Download audio option

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google Gemini API key | - |
| `AI_PROVIDER` | AI provider to use | `openai` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173` |
| `TTS_VOICE` | Default TTS voice | `en-US-AriaNeural` |

### Curriculum Knowledge Base

The curriculum knowledge base is stored in `backend/data/curriculum_kb.json`. You can customize it by adding new topics:

```json
{
  "id": "science_custom_topic",
  "name": "Custom Topic",
  "subject": "Science",
  "grade_range": "3-5",
  "description": "Description of the topic",
  "keywords": ["keyword1", "keyword2"],
  "learning_objectives": ["Objective 1", "Objective 2"],
  "related_topics": ["related_topic_id"],
  "story_themes": ["theme1", "theme2"]
}
```

## 🛡️ Error Handling

The platform implements robust error handling:

- **Validation**: Pydantic/Zod schemas for strict input validation
- **Retry Logic**: Automatic retries with exponential backoff for AI API calls
- **User Feedback**: Clear error messages displayed to users
- **Logging**: Comprehensive logging for debugging

## 🌐 Supported Languages

| Language | Code | TTS Support |
|----------|------|-------------|
| English (US) | en | ✅ |
| English (UK) | en-GB | ✅ |
| Spanish | es | ✅ |
| French | fr | ✅ |
| German | de | ✅ |
| Italian | it | ✅ |
| Portuguese | pt | ✅ |
| Chinese | zh | ✅ |
| Japanese | ja | ✅ |
| Korean | ko | ✅ |
| Hindi | hi | ✅ |
| Arabic | ar | ✅ |
| Russian | ru | ✅ |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o Vision API
- Google for Gemini API
- Microsoft Edge TTS for text-to-speech
- The React and FastAPI communities

---

Made with ❤️ for curious young minds
# Multimodel_Story_telling
