/**
 * API service for communicating with the FastAPI backend
 */

import axios, { AxiosError, AxiosInstance } from 'axios';
import {
  StoryRequest,
  StoryResponse,
  ImageAnalysisResult,
  AudioRequest,
  AudioResponse,
  ErrorResponse,
} from '../types';

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for AI processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handler
const handleApiError = (error: AxiosError<ErrorResponse>): never => {
  if (error.response) {
    const errorData = error.response.data;
    throw new Error(errorData.message || 'An error occurred');
  } else if (error.request) {
    throw new Error('Unable to connect to the server. Please check your connection.');
  } else {
    throw new Error(error.message || 'An unexpected error occurred');
  }
};

/**
 * Input Handler API
 */
export const inputApi = {
  /**
   * Analyze multimodal input (sketch, diagram, or keywords)
   */
  analyze: async (request: StoryRequest): Promise<ImageAnalysisResult> => {
    try {
      const response = await apiClient.post<ImageAnalysisResult>('/input/analyze', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Upload and analyze an image file
   */
  uploadAndAnalyze: async (
    file: File,
    inputType: 'sketch' | 'diagram' = 'diagram',
    ageGroup: string = '8-10'
  ): Promise<ImageAnalysisResult> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('input_type', inputType);
      formData.append('age_group', ageGroup);

      const response = await apiClient.post<ImageAnalysisResult>('/input/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Analyze keywords
   */
  analyzeKeywords: async (keywords: string, ageGroup: string = '8-10'): Promise<ImageAnalysisResult> => {
    try {
      const formData = new FormData();
      formData.append('keywords', keywords);
      formData.append('age_group', ageGroup);

      const response = await apiClient.post<ImageAnalysisResult>('/input/keywords', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },
};

/**
 * Story API
 */
export const storyApi = {
  /**
   * Generate a story from multimodal input
   */
  generate: async (request: StoryRequest): Promise<StoryResponse> => {
    try {
      const response = await apiClient.post<StoryResponse>('/story/generate', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Generate a story from analysis results
   */
  generateFromAnalysis: async (
    analysis: ImageAnalysisResult,
    ageGroup: string = '8-10',
    language: string = 'en',
    includeQuiz: boolean = true
  ): Promise<StoryResponse> => {
    try {
      const response = await apiClient.post<StoryResponse>(
        '/story/from-analysis',
        analysis,
        {
          params: {
            age_group: ageGroup,
            language: language,
            include_quiz: includeQuiz,
          },
        }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Get a story by ID
   */
  getById: async (storyId: string): Promise<StoryResponse> => {
    try {
      const response = await apiClient.get<StoryResponse>(`/story/${storyId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Regenerate quiz for a story
   */
  regenerateQuiz: async (storyId: string, numQuestions: number = 3): Promise<StoryResponse> => {
    try {
      const response = await apiClient.post<StoryResponse>(
        `/story/${storyId}/quiz`,
        null,
        {
          params: { num_questions: numQuestions },
        }
      );
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * List recent stories
   */
  list: async (limit: number = 10): Promise<StoryResponse[]> => {
    try {
      const response = await apiClient.get<StoryResponse[]>('/story/', {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },
};

/**
 * Audio API
 */
export const audioApi = {
  /**
   * Generate audio from text
   */
  generate: async (request: AudioRequest): Promise<AudioResponse> => {
    try {
      const response = await apiClient.post<AudioResponse>('/audio/generate', request);
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * Get audio URL by ID
   */
  getUrl: (audioId: string): string => {
    return `${API_BASE_URL}/audio/${audioId}`;
  },

  /**
   * Delete audio file
   */
  delete: async (audioId: string): Promise<void> => {
    try {
      await apiClient.delete(`/audio/${audioId}`);
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },

  /**
   * List available voices
   */
  listVoices: async (language?: string): Promise<{ voices: { name: string; short_name: string; gender: string; locale: string; language: string }[] }> => {
    try {
      const response = await apiClient.get('/audio/voices/list', {
        params: language ? { language } : undefined,
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error as AxiosError<ErrorResponse>);
    }
  },
};

/**
 * Health check
 */
export const healthCheck = async (): Promise<boolean> => {
  try {
    // Health check is at root level, not under /api
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const healthUrl = baseUrl.replace(/\/api$/, '') + '/health';
    const response = await axios.get(healthUrl);
    return response.data.status === 'healthy';
  } catch {
    return false;
  }
};

// Export all APIs
export default {
  input: inputApi,
  story: storyApi,
  audio: audioApi,
  healthCheck,
};
