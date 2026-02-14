/**
 * Multimodal Storytelling Platform - Main Application
 * 
 * An AI-powered platform for generating interactive, curriculum-aligned
 * stories from children's sketches, diagrams, or keywords.
 */

import { useState, useCallback } from 'react';
import { BookOpen, Sparkles, Volume2, ArrowLeft, RefreshCw } from 'lucide-react';
import { InputHandler } from './components/InputHandler';
import { StoryDisplay } from './components/StoryDisplay';
import { QuizModule } from './components/QuizModule';
import { AudioPlayer } from './components/AudioPlayer';
import { useStoryGeneration } from './hooks/useStoryGeneration';
import type { StoryRequest } from './types';

type AppView = 'input' | 'story' | 'quiz';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('input');
  const {
    isLoading,
    error,
    story,
    audioUrl,
    generateStory,
    generateAudio,
    reset,
    clearError,
  } = useStoryGeneration();

  const handleSubmit = useCallback(async (request: StoryRequest) => {
    await generateStory(request);
    setCurrentView('story');
  }, [generateStory]);

  const handleQuizStart = useCallback(() => {
    setCurrentView('quiz');
  }, []);

  const handleQuizComplete = useCallback((score: number) => {
    console.log(`Quiz completed with score: ${score}`);
  }, []);

  const handleNewStory = useCallback(() => {
    reset();
    setCurrentView('input');
  }, [reset]);

  const handleBackToStory = useCallback(() => {
    setCurrentView('story');
  }, []);

  const handleGenerateAudio = useCallback(async () => {
    await generateAudio();
  }, [generateAudio]);

  return (
    <div className="min-h-screen pb-12">
      {/* Header */}
      <header className="bg-gradient-to-r from-primary-600 via-purple-600 to-secondary-600 text-white py-6 px-4 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-2xl backdrop-blur-sm">
              <BookOpen size={32} />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-display">
                Storytelling Adventure
              </h1>
              <p className="text-white/80 text-sm md:text-base">
                Create magical stories from your imagination! ✨
              </p>
            </div>
          </div>
          
          {/* Navigation */}
          {currentView !== 'input' && (
            <button
              onClick={handleNewStory}
              className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-xl hover:bg-white/30 transition-colors backdrop-blur-sm"
            >
              <RefreshCw size={20} />
              <span className="hidden md:inline">New Story</span>
            </button>
          )}
        </div>
      </header>

      {/* Error toast */}
      {error && (
        <div className="fixed top-4 right-4 z-50 max-w-md animate-in slide-in-from-right">
          <div className="bg-red-500 text-white p-4 rounded-xl shadow-lg flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div className="flex-1">
              <p className="font-bold">Oops!</p>
              <p className="text-sm">{error}</p>
            </div>
            <button
              onClick={clearError}
              className="text-white/80 hover:text-white"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Input view */}
        {currentView === 'input' && (
          <div className="animate-in fade-in duration-500">
            {/* Hero section */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium mb-4">
                <Sparkles size={16} />
                AI-Powered Learning
              </div>
              <h2 className="text-4xl md:text-5xl font-display text-gray-800 mb-4">
                Turn Your Ideas Into
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-primary-500 to-secondary-500">
                  Amazing Stories!
                </span>
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Draw a picture, upload an image, or type some keywords.
                Our AI will create a fun educational story just for you!
              </p>
            </div>

            {/* Input handler */}
            <InputHandler
              onStoryGenerated={() => {}}
              onError={() => {}}
              isLoading={isLoading}
              onSubmit={handleSubmit}
            />

            {/* Features */}
            <div className="mt-16 grid md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
                <div className="w-16 h-16 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎨</span>
                </div>
                <h3 className="font-bold text-gray-800 mb-2">Draw & Create</h3>
                <p className="text-gray-600 text-sm">
                  Sketch your ideas and watch them come to life in a story
                </p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
                <div className="w-16 h-16 bg-secondary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">📚</span>
                </div>
                <h3 className="font-bold text-gray-800 mb-2">Learn & Grow</h3>
                <p className="text-gray-600 text-sm">
                  Stories aligned with your curriculum for fun learning
                </p>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-lg text-center">
                <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">🎯</span>
                </div>
                <h3 className="font-bold text-gray-800 mb-2">Quiz & Test</h3>
                <p className="text-gray-600 text-sm">
                  Challenge yourself with fun quizzes about your story
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Story view */}
        {currentView === 'story' && story && (
          <div className="animate-in fade-in duration-500">
            {/* Back button */}
            <button
              onClick={handleNewStory}
              className="flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6 transition-colors"
            >
              <ArrowLeft size={20} />
              <span>Create Another Story</span>
            </button>

            {/* Story display */}
            <StoryDisplay
              story={story}
              onQuizStart={handleQuizStart}
              onNewStory={handleNewStory}
            />

            {/* Audio section */}
            <div className="mt-8">
              {audioUrl ? (
                <AudioPlayer audioUrl={audioUrl} title={`Listen to "${story.title}"`} />
              ) : (
                <button
                  onClick={handleGenerateAudio}
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-3 py-4 px-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl transition-all disabled:opacity-50"
                >
                  <Volume2 size={24} />
                  {isLoading ? 'Generating Audio...' : 'Listen to Story 🎧'}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Quiz view */}
        {currentView === 'quiz' && story?.quiz && (
          <div className="animate-in fade-in duration-500">
            {/* Back button */}
            <button
              onClick={handleBackToStory}
              className="flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6 transition-colors"
            >
              <ArrowLeft size={20} />
              <span>Back to Story</span>
            </button>

            {/* Quiz module */}
            <QuizModule
              quiz={story.quiz}
              onComplete={handleQuizComplete}
              onRetry={() => {}}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t bg-white/50">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p>
            Made with ❤️ for curious young minds
          </p>
          <p className="mt-1">
            Multimodal Storytelling Platform © {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
