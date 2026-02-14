/**
 * Keyword Input Component
 * For entering topic keywords or descriptions
 */

import React, { useState } from 'react';
import { Sparkles, Tag, Lightbulb } from 'lucide-react';
import type { KeywordInputProps } from '../types';

const SUGGESTED_TOPICS = [
  { icon: '🌱', label: 'Plants & Nature', keywords: 'plants, flowers, trees, nature' },
  { icon: '🚀', label: 'Space Adventure', keywords: 'space, planets, stars, astronaut' },
  { icon: '🦁', label: 'Animal Kingdom', keywords: 'animals, jungle, safari, wildlife' },
  { icon: '🌊', label: 'Ocean Life', keywords: 'ocean, fish, dolphins, underwater' },
  { icon: '🦕', label: 'Dinosaurs', keywords: 'dinosaurs, fossils, prehistoric' },
  { icon: '🔬', label: 'Science Fun', keywords: 'science, experiments, discovery' },
  { icon: '🏰', label: 'Fairy Tales', keywords: 'castle, princess, magic, adventure' },
  { icon: '🌈', label: 'Weather', keywords: 'weather, rain, sun, clouds, rainbow' },
];

export const KeywordInput: React.FC<KeywordInputProps> = ({
  value,
  onChange,
  onSubmit,
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      e.preventDefault();
      if (value.trim().length >= 2) {
        onSubmit();
      }
    }
  };

  const handleSuggestionClick = (keywords: string) => {
    onChange(keywords);
  };

  const isValid = value.trim().length >= 2;

  return (
    <div className="flex flex-col gap-6">
      {/* Input area */}
      <div className={`
        relative bg-white rounded-2xl shadow-lg overflow-hidden transition-all duration-300
        ${isFocused ? 'ring-4 ring-primary-400 ring-opacity-50' : ''}
      `}>
        {/* Header */}
        <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-primary-50 to-secondary-50 border-b">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Lightbulb className="text-primary-600" size={24} />
          </div>
          <div>
            <h3 className="font-bold text-gray-800">What do you want to learn about?</h3>
            <p className="text-sm text-gray-500">Enter keywords or describe a topic</p>
          </div>
        </div>

        {/* Text input */}
        <div className="relative p-4">
          <textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyPress={handleKeyPress}
            placeholder="e.g., dinosaurs, photosynthesis, solar system, water cycle..."
            className="w-full h-32 p-4 text-lg border-2 border-gray-200 rounded-xl focus:border-primary-400 focus:outline-none resize-none transition-colors"
            maxLength={500}
          />
          
          {/* Character count */}
          <div className="absolute bottom-6 right-6 text-sm text-gray-400">
            {value.length}/500
          </div>
        </div>

        {/* Tags */}
        {value.length > 0 && (
          <div className="px-4 pb-4 flex flex-wrap gap-2">
            {value.split(/[,\s]+/).filter(Boolean).map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
              >
                <Tag size={14} />
                {keyword}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Suggested topics */}
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="text-yellow-500" size={20} />
          <h3 className="font-bold text-gray-800">Quick Ideas</h3>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SUGGESTED_TOPICS.map((topic) => (
            <button
              key={topic.label}
              onClick={() => handleSuggestionClick(topic.keywords)}
              className={`
                p-4 rounded-xl text-left transition-all hover:scale-[1.02]
                ${value === topic.keywords
                  ? 'bg-primary-100 border-2 border-primary-400'
                  : 'bg-gray-50 border-2 border-transparent hover:bg-primary-50'
                }
              `}
            >
              <div className="text-2xl mb-2">{topic.icon}</div>
              <div className="font-semibold text-gray-800">{topic.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Submit button */}
      <button
        onClick={onSubmit}
        disabled={!isValid}
        className={`
          w-full py-4 px-6 font-bold text-xl rounded-xl shadow-lg transition-all btn-glow
          ${isValid
            ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white hover:shadow-xl transform hover:scale-[1.02]'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }
        `}
      >
        {isValid ? '🎯 Create Story from Keywords! 🎯' : 'Enter at least 2 characters'}
      </button>

      {/* Hint */}
      <p className="text-center text-sm text-gray-500">
        💡 Tip: Press <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Ctrl</kbd> + <kbd className="px-2 py-1 bg-gray-200 rounded text-xs">Enter</kbd> to submit quickly
      </p>
    </div>
  );
};

export default KeywordInput;
