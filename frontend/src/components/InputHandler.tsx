/**
 * Input Handler Component
 * Main component for multimodal input selection and processing
 */

import React, { useState } from 'react';
import { Pencil, Image, Type, Settings, Loader2 } from 'lucide-react';
import type { InputHandlerProps, InputType, AgeGroup, StoryRequest } from '../types';
import { DrawingCanvas } from './DrawingCanvas';
import { FileUpload } from './FileUpload';
import { KeywordInput } from './KeywordInput';

const INPUT_TABS = [
  { id: 'sketch' as InputType, icon: Pencil, label: 'Draw', description: 'Create a sketch' },
  { id: 'diagram' as InputType, icon: Image, label: 'Upload', description: 'Upload an image' },
  { id: 'keyword' as InputType, icon: Type, label: 'Keywords', description: 'Type keywords' },
];

const AGE_GROUPS: { value: AgeGroup; label: string; emoji: string }[] = [
  { value: '5-7', label: '5-7 years', emoji: '🧒' },
  { value: '8-10', label: '8-10 years', emoji: '👧' },
  { value: '11-13', label: '11-13 years', emoji: '🧑' },
];

interface InputHandlerState {
  activeTab: InputType;
  ageGroup: AgeGroup;
  language: string;
  keywords: string;
  showSettings: boolean;
}

interface ExtendedInputHandlerProps extends InputHandlerProps {
  isLoading: boolean;
  onSubmit: (request: StoryRequest) => void;
}

export const InputHandler: React.FC<ExtendedInputHandlerProps> = ({
  onError,
  isLoading,
  onSubmit,
  // Note: onStoryGenerated is inherited from InputHandlerProps but not used
  // as story generation is handled externally via onSubmit
}) => {
  const [state, setState] = useState<InputHandlerState>({
    activeTab: 'sketch',
    ageGroup: '8-10',
    language: 'en',
    keywords: '',
    showSettings: false,
  });

  const handleImageCapture = (imageData: string) => {
    const request: StoryRequest = {
      input_type: state.activeTab,
      image_data: imageData,
      age_group: state.ageGroup,
      language: state.language,
    };
    onSubmit(request);
  };

  const handleKeywordSubmit = () => {
    if (state.keywords.trim().length < 2) {
      onError('Please enter at least 2 characters');
      return;
    }

    const request: StoryRequest = {
      input_type: 'keyword',
      keywords: state.keywords,
      age_group: state.ageGroup,
      language: state.language,
    };
    onSubmit(request);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header with settings */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-display text-gray-800">
          Choose how you want to create your story
        </h2>
        <button
          onClick={() => setState(prev => ({ ...prev, showSettings: !prev.showSettings }))}
          className={`p-3 rounded-xl transition-all ${
            state.showSettings
              ? 'bg-primary-500 text-white'
              : 'bg-white text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Settings size={24} />
        </button>
      </div>

      {/* Settings panel */}
      {state.showSettings && (
        <div className="mb-6 p-6 bg-white rounded-2xl shadow-lg animate-in slide-in-from-top">
          <h3 className="font-bold text-gray-800 mb-4">Story Settings</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* Age group */}
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Age Group
              </label>
              <div className="flex gap-2">
                {AGE_GROUPS.map(({ value, label, emoji }) => (
                  <button
                    key={value}
                    onClick={() => setState(prev => ({ ...prev, ageGroup: value }))}
                    className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                      state.ageGroup === value
                        ? 'bg-primary-500 text-white shadow-lg'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    <span className="text-xl">{emoji}</span>
                    <div className="text-sm mt-1">{label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Language */}
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-2">
                Language
              </label>
              <select
                value={state.language}
                onChange={(e) => setState(prev => ({ ...prev, language: e.target.value }))}
                className="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:border-primary-400 focus:outline-none"
              >
                <option value="en">🇺🇸 English</option>
                <option value="es">🇪🇸 Spanish</option>
                <option value="fr">🇫🇷 French</option>
                <option value="de">🇩🇪 German</option>
                <option value="hi">🇮🇳 Hindi</option>
                <option value="zh">🇨🇳 Chinese</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Input type tabs */}
      <div className="flex gap-3 mb-6">
        {INPUT_TABS.map(({ id, icon: Icon, label, description }) => (
          <button
            key={id}
            onClick={() => setState(prev => ({ ...prev, activeTab: id }))}
            disabled={isLoading}
            className={`
              flex-1 p-4 rounded-2xl transition-all
              ${state.activeTab === id
                ? 'bg-gradient-to-br from-primary-500 to-secondary-500 text-white shadow-lg scale-[1.02]'
                : 'bg-white text-gray-700 hover:bg-gray-50 shadow'
              }
              ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
            `}
          >
            <Icon size={32} className="mx-auto mb-2" />
            <div className="font-bold">{label}</div>
            <div className={`text-sm ${state.activeTab === id ? 'text-white/80' : 'text-gray-500'}`}>
              {description}
            </div>
          </button>
        ))}
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="relative">
          <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-2xl z-10 flex flex-col items-center justify-center min-h-[400px]">
            <Loader2 size={64} className="text-primary-500 animate-spin mb-4" />
            <h3 className="text-2xl font-display text-primary-600 mb-2">
              Creating Your Story...
            </h3>
            <p className="text-gray-500">Our AI is working its magic! ✨</p>
            <div className="flex gap-2 mt-4">
              <div className="w-3 h-3 rounded-full bg-primary-500 animate-bounce" />
              <div className="w-3 h-3 rounded-full bg-secondary-500 animate-bounce delay-100" />
              <div className="w-3 h-3 rounded-full bg-primary-500 animate-bounce delay-200" />
            </div>
          </div>
        </div>
      )}

      {/* Input content */}
      {!isLoading && (
        <div className="bg-gray-50 rounded-2xl p-6">
          {state.activeTab === 'sketch' && (
            <DrawingCanvas onImageCapture={handleImageCapture} />
          )}
          {state.activeTab === 'diagram' && (
            <FileUpload onFileSelect={handleImageCapture} />
          )}
          {state.activeTab === 'keyword' && (
            <KeywordInput
              value={state.keywords}
              onChange={(value) => setState(prev => ({ ...prev, keywords: value }))}
              onSubmit={handleKeywordSubmit}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default InputHandler;
