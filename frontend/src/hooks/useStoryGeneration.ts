/**
 * Custom hook for story generation workflow
 */

import { useState, useCallback } from 'react';
import {
  StoryResponse,
  ImageAnalysisResult,
  StoryRequest,
} from '../types';
import { storyApi, audioApi } from '../services/api';

interface UseStoryGenerationState {
  isLoading: boolean;
  error: string | null;
  story: StoryResponse | null;
  analysis: ImageAnalysisResult | null;
  audioUrl: string | null;
  currentStep: 'input' | 'analyzing' | 'generating' | 'complete';
}

interface UseStoryGenerationReturn extends UseStoryGenerationState {
  generateStory: (request: StoryRequest) => Promise<boolean>;
  generateAudio: () => Promise<void>;
  reset: () => void;
  clearError: () => void;
}

export function useStoryGeneration(): UseStoryGenerationReturn {
  const [state, setState] = useState<UseStoryGenerationState>({
    isLoading: false,
    error: null,
    story: null,
    analysis: null,
    audioUrl: null,
    currentStep: 'input',
  });

  const generateStory = useCallback(async (request: StoryRequest): Promise<boolean> => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
      currentStep: 'generating',
    }));

    try {
      // Generate story with quiz
      const story = await storyApi.generate(request);

      setState(prev => ({
        ...prev,
        isLoading: false,
        story,
        currentStep: 'complete',
      }));
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate story';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
        currentStep: 'input',
      }));
      return false;
    }
  }, []);

  const generateAudio = useCallback(async () => {
    if (!state.story) {
      setState(prev => ({
        ...prev,
        error: 'No story available for audio generation',
      }));
      return;
    }

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const audioResponse = await audioApi.generate({
        text: state.story.content,
        language: 'en',
      });

      const audioUrl = audioApi.getUrl(audioResponse.audio_id);

      setState(prev => ({
        ...prev,
        isLoading: false,
        audioUrl,
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate audio';
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, [state.story]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      story: null,
      analysis: null,
      audioUrl: null,
      currentStep: 'input',
    });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    ...state,
    generateStory,
    generateAudio,
    reset,
    clearError,
  };
}

export default useStoryGeneration;
