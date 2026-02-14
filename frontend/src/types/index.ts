/**
 * TypeScript type definitions for the Multimodal Storytelling Platform
 */

import { z } from 'zod';

// Input types
export type InputType = 'sketch' | 'diagram' | 'keyword';

// Age groups
export type AgeGroup = '5-7' | '8-10' | '11-13';

// Quiz difficulty
export type Difficulty = 'easy' | 'medium' | 'hard';

// Zod schemas for validation
export const StoryRequestSchema = z.object({
  input_type: z.enum(['sketch', 'diagram', 'keyword']),
  image_data: z.string().optional(),
  keywords: z.string().max(500).optional(),
  age_group: z.enum(['5-7', '8-10', '11-13']).default('8-10'),
  language: z.string().max(10).default('en'),
});

export type StoryRequest = z.infer<typeof StoryRequestSchema>;

// Image analysis result
export interface ImageAnalysisResult {
  detected_objects: string[];
  scene_description: string;
  educational_concepts: string[];
  suggested_topics: string[];
  confidence: number;
}

// Quiz question
export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

// Quiz response
export interface QuizResponse {
  questions: QuizQuestion[];
  story_id: string;
  difficulty: Difficulty;
}

// Story response
export interface StoryResponse {
  story_id: string;
  title: string;
  content: string;
  summary: string;
  concepts_covered: string[];
  age_group: string;
  word_count: number;
  quiz: QuizResponse | null;
  audio_available: boolean;
}

// Audio request
export interface AudioRequest {
  text: string;
  voice?: string;
  language: string;
  rate?: string;
}

// Audio response
export interface AudioResponse {
  audio_id: string;
  audio_url: string;
  duration_seconds: number | null;
  format: string;
}

// Error response
export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}

// Application state
export interface AppState {
  currentStep: 'input' | 'loading' | 'story' | 'quiz';
  inputType: InputType;
  imageData: string | null;
  keywords: string;
  ageGroup: AgeGroup;
  language: string;
  story: StoryResponse | null;
  analysis: ImageAnalysisResult | null;
  audioUrl: string | null;
  isLoading: boolean;
  error: string | null;
}

// Canvas state
export interface CanvasState {
  isDrawing: boolean;
  color: string;
  brushSize: number;
  history: ImageData[];
  historyIndex: number;
}

// Quiz state
export interface QuizState {
  currentQuestion: number;
  answers: (number | null)[];
  showResults: boolean;
  score: number;
}

// Event handlers
export type DrawingEventHandler = (
  event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
) => void;

// Component props
export interface DrawingCanvasProps {
  onImageCapture: (imageData: string) => void;
  width?: number;
  height?: number;
}

export interface FileUploadProps {
  onFileSelect: (imageData: string) => void;
  accept?: string;
}

export interface KeywordInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}

export interface StoryDisplayProps {
  story: StoryResponse;
  onQuizStart: () => void;
  onNewStory: () => void;
}

export interface QuizModuleProps {
  quiz: QuizResponse;
  onComplete: (score: number) => void;
  onRetry: () => void;
}

export interface AudioPlayerProps {
  audioUrl: string;
  title?: string;
}

export interface InputHandlerProps {
  onStoryGenerated: (story: StoryResponse) => void;
  onError: (error: string) => void;
}
