/**
 * Story Display Component
 * Displays the generated story with animations
 */

import React, { useState, useEffect } from 'react';
import { BookOpen, Sparkles, Volume2, HelpCircle, RefreshCw, ChevronRight } from 'lucide-react';
import type { StoryDisplayProps } from '../types';

export const StoryDisplay: React.FC<StoryDisplayProps> = ({
  story,
  onQuizStart,
  onNewStory,
}) => {
  const [isRevealed, setIsRevealed] = useState(false);
  const [currentParagraph, setCurrentParagraph] = useState(0);

  // Split content into paragraphs
  const paragraphs = story.content
    .split('\n')
    .filter(p => p.trim().length > 0);

  // Reveal animation
  useEffect(() => {
    const timer = setTimeout(() => setIsRevealed(true), 300);
    return () => clearTimeout(timer);
  }, []);

  // Progressive paragraph reveal
  useEffect(() => {
    if (isRevealed && currentParagraph < paragraphs.length) {
      const timer = setTimeout(() => {
        setCurrentParagraph(prev => prev + 1);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isRevealed, currentParagraph, paragraphs.length]);

  const allRevealed = currentParagraph >= paragraphs.length;

  return (
    <div className={`
      bg-white rounded-3xl shadow-2xl overflow-hidden transition-all duration-500
      ${isRevealed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}
    `}>
      {/* Header */}
      <div className="relative bg-gradient-to-r from-primary-500 via-purple-500 to-secondary-500 p-6 text-white">
        {/* Decorative elements */}
        <div className="absolute top-4 left-4 opacity-30">
          <Sparkles size={32} className="animate-pulse" />
        </div>
        <div className="absolute top-4 right-4 opacity-30">
          <Sparkles size={24} className="animate-pulse delay-300" />
        </div>
        <div className="absolute bottom-2 left-1/4 opacity-20">
          <Sparkles size={20} className="animate-pulse delay-500" />
        </div>

        {/* Title */}
        <div className="relative z-10 text-center">
          <div className="flex justify-center mb-3">
            <div className="p-3 bg-white/20 rounded-full backdrop-blur-sm">
              <BookOpen size={32} />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-display drop-shadow-lg">
            {story.title}
          </h1>
          <p className="mt-2 text-white/80 text-sm">
            {story.word_count} words • For ages {story.age_group}
          </p>
        </div>
      </div>

      {/* Concepts tags */}
      <div className="px-6 py-4 bg-gradient-to-r from-primary-50 to-secondary-50 border-b">
        <div className="flex flex-wrap gap-2 justify-center">
          <span className="text-sm text-gray-500 mr-2">📚 Learning:</span>
          {story.concepts_covered.map((concept, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-white rounded-full text-sm font-medium text-primary-700 shadow-sm"
            >
              {concept}
            </span>
          ))}
        </div>
      </div>

      {/* Story content */}
      <div className="p-6 md:p-8 story-content">
        <div className="max-w-3xl mx-auto space-y-6 text-lg text-gray-700 leading-relaxed">
          {paragraphs.map((paragraph, index) => (
            <p
              key={index}
              className={`
                transition-all duration-500
                ${index < currentParagraph
                  ? 'opacity-100 translate-y-0'
                  : 'opacity-0 translate-y-4'
                }
              `}
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              {paragraph}
            </p>
          ))}
        </div>

        {/* Loading more paragraphs indicator */}
        {!allRevealed && (
          <div className="flex justify-center mt-8">
            <div className="flex items-center gap-2 text-primary-500">
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce" />
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce delay-100" />
              <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce delay-200" />
            </div>
          </div>
        )}
      </div>

      {/* Summary */}
      {allRevealed && (
        <div className="mx-6 mb-6 p-4 bg-yellow-50 border-2 border-yellow-200 rounded-xl">
          <h3 className="font-bold text-yellow-800 flex items-center gap-2">
            <span>💡</span> What We Learned
          </h3>
          <p className="mt-2 text-yellow-700">{story.summary}</p>
        </div>
      )}

      {/* Action buttons */}
      {allRevealed && (
        <div className="p-6 bg-gray-50 border-t flex flex-col sm:flex-row gap-4">
          {/* Take Quiz button */}
          {story.quiz && (
            <button
              onClick={onQuizStart}
              className="flex-1 flex items-center justify-center gap-3 py-4 px-6 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all"
            >
              <HelpCircle size={24} />
              Take the Quiz!
              <ChevronRight size={20} />
            </button>
          )}

          {/* New Story button */}
          <button
            onClick={onNewStory}
            className="flex-1 flex items-center justify-center gap-3 py-4 px-6 bg-white border-2 border-gray-300 text-gray-700 font-bold text-lg rounded-xl hover:bg-gray-50 hover:border-primary-400 transition-all"
          >
            <RefreshCw size={24} />
            Create New Story
          </button>
        </div>
      )}
    </div>
  );
};

export default StoryDisplay;
