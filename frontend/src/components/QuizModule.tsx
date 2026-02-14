/**
 * Quiz Module Component
 * Interactive MCQ quiz based on story content
 */

import React, { useState } from 'react';
import { CheckCircle, XCircle, HelpCircle, Trophy, RotateCcw, ArrowRight, Star } from 'lucide-react';
import type { QuizModuleProps, QuizState } from '../types';

export const QuizModule: React.FC<QuizModuleProps> = ({
  quiz,
  onComplete,
  onRetry,
}) => {
  const [state, setState] = useState<QuizState>({
    currentQuestion: 0,
    answers: Array(quiz.questions.length).fill(null),
    showResults: false,
    score: 0,
  });

  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const currentQ = quiz.questions[state.currentQuestion];
  const isLastQuestion = state.currentQuestion === quiz.questions.length - 1;

  const handleAnswerSelect = (answerIndex: number) => {
    if (showFeedback) return;
    setSelectedAnswer(answerIndex);
  };

  const handleSubmitAnswer = () => {
    if (selectedAnswer === null) return;

    // Show feedback
    setShowFeedback(true);

    // Update answers
    const newAnswers = [...state.answers];
    newAnswers[state.currentQuestion] = selectedAnswer;

    setState(prev => ({
      ...prev,
      answers: newAnswers,
    }));
  };

  const handleNextQuestion = () => {
    if (isLastQuestion) {
      // Calculate final score
      const correctCount = state.answers.reduce<number>((count, answer, index) => {
        if (answer === quiz.questions[index].correct_answer) {
          return count + 1;
        }
        return count;
      }, selectedAnswer === currentQ.correct_answer ? 1 : 0);

      setState(prev => ({
        ...prev,
        showResults: true,
        score: correctCount,
      }));

      onComplete(correctCount);
    } else {
      // Move to next question
      setState(prev => ({
        ...prev,
        currentQuestion: prev.currentQuestion + 1,
      }));
      setSelectedAnswer(null);
      setShowFeedback(false);
    }
  };

  const handleRetry = () => {
    setState({
      currentQuestion: 0,
      answers: Array(quiz.questions.length).fill(null),
      showResults: false,
      score: 0,
    });
    setSelectedAnswer(null);
    setShowFeedback(false);
    onRetry();
  };

  const getOptionClassName = (index: number): string => {
    const baseClass = 'quiz-option w-full p-4 text-left rounded-xl border-2 transition-all flex items-start gap-3';
    
    if (!showFeedback) {
      if (selectedAnswer === index) {
        return `${baseClass} border-primary-500 bg-primary-50 selected`;
      }
      return `${baseClass} border-gray-200 hover:border-primary-300 hover:bg-primary-50`;
    }

    // Show feedback
    if (index === currentQ.correct_answer) {
      return `${baseClass} correct border-green-500 bg-green-50`;
    }
    if (selectedAnswer === index && index !== currentQ.correct_answer) {
      return `${baseClass} incorrect border-red-500 bg-red-50`;
    }
    return `${baseClass} border-gray-200 bg-gray-50 opacity-60 disabled`;
  };

  const getScoreMessage = (score: number, total: number): { emoji: string; message: string } => {
    const percentage = (score / total) * 100;
    if (percentage === 100) {
      return { emoji: '🌟', message: 'Perfect Score! You\'re a superstar!' };
    } else if (percentage >= 80) {
      return { emoji: '🎉', message: 'Excellent work! You\'re doing great!' };
    } else if (percentage >= 60) {
      return { emoji: '👍', message: 'Good job! Keep practicing!' };
    } else if (percentage >= 40) {
      return { emoji: '💪', message: 'Nice try! Let\'s learn more!' };
    }
    return { emoji: '📚', message: 'Let\'s read the story again!' };
  };

  // Results screen
  if (state.showResults) {
    const { emoji, message } = getScoreMessage(state.score, quiz.questions.length);
    const percentage = Math.round((state.score / quiz.questions.length) * 100);

    return (
      <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-400 p-8 text-white text-center">
          <Trophy size={64} className="mx-auto mb-4 animate-bounce" />
          <h2 className="text-3xl font-display">Quiz Complete!</h2>
        </div>

        {/* Score */}
        <div className="p-8 text-center">
          <div className="text-8xl mb-4">{emoji}</div>
          <div className="text-5xl font-bold text-primary-600 mb-2">
            {state.score} / {quiz.questions.length}
          </div>
          <div className="text-2xl text-gray-600 mb-4">{percentage}% Correct</div>
          <p className="text-xl text-gray-700">{message}</p>

          {/* Stars */}
          <div className="flex justify-center gap-2 mt-6">
            {[...Array(quiz.questions.length)].map((_, index) => (
              <Star
                key={index}
                size={32}
                className={`transition-all ${
                  index < state.score
                    ? 'text-yellow-400 fill-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Question summary */}
        <div className="px-8 pb-8">
          <h3 className="font-bold text-gray-700 mb-4">Question Summary:</h3>
          <div className="space-y-3">
            {quiz.questions.map((q, index) => (
              <div
                key={index}
                className={`p-4 rounded-xl flex items-start gap-3 ${
                  state.answers[index] === q.correct_answer
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-red-50 border border-red-200'
                }`}
              >
                {state.answers[index] === q.correct_answer ? (
                  <CheckCircle className="text-green-500 flex-shrink-0 mt-1" size={20} />
                ) : (
                  <XCircle className="text-red-500 flex-shrink-0 mt-1" size={20} />
                )}
                <div>
                  <p className="font-medium text-gray-800">{q.question}</p>
                  {state.answers[index] !== q.correct_answer && (
                    <p className="text-sm text-green-600 mt-1">
                      Correct answer: {q.options[q.correct_answer]}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 bg-gray-50 border-t flex gap-4">
          <button
            onClick={handleRetry}
            className="flex-1 flex items-center justify-center gap-2 py-4 px-6 bg-white border-2 border-gray-300 text-gray-700 font-bold rounded-xl hover:bg-gray-50 transition-all"
          >
            <RotateCcw size={20} />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Question screen
  return (
    <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <HelpCircle size={28} />
            <span className="text-lg font-medium">Quiz Time!</span>
          </div>
          <div className="flex items-center gap-2 bg-white/20 px-4 py-2 rounded-full backdrop-blur-sm">
            <span className="font-bold">
              {state.currentQuestion + 1} / {quiz.questions.length}
            </span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4 h-2 bg-white/30 rounded-full overflow-hidden">
          <div
            className="h-full bg-white rounded-full transition-all duration-500"
            style={{
              width: `${((state.currentQuestion + 1) / quiz.questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="p-6 md:p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">
          {currentQ.question}
        </h2>

        {/* Options */}
        <div className="space-y-3">
          {currentQ.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              disabled={showFeedback}
              className={getOptionClassName(index)}
            >
              <span className={`
                w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0
                ${selectedAnswer === index
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-600'
                }
                ${showFeedback && index === currentQ.correct_answer
                  ? 'bg-green-500 text-white'
                  : ''
                }
                ${showFeedback && selectedAnswer === index && index !== currentQ.correct_answer
                  ? 'bg-red-500 text-white'
                  : ''
                }
              `}>
                {String.fromCharCode(65 + index)}
              </span>
              <span className="text-lg">{option}</span>
              {showFeedback && index === currentQ.correct_answer && (
                <CheckCircle className="text-green-500 ml-auto" size={24} />
              )}
              {showFeedback && selectedAnswer === index && index !== currentQ.correct_answer && (
                <XCircle className="text-red-500 ml-auto" size={24} />
              )}
            </button>
          ))}
        </div>

        {/* Explanation */}
        {showFeedback && currentQ.explanation && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <p className="text-blue-800">
              <span className="font-bold">💡 Explanation: </span>
              {currentQ.explanation}
            </p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-6 bg-gray-50 border-t">
        {!showFeedback ? (
          <button
            onClick={handleSubmitAnswer}
            disabled={selectedAnswer === null}
            className={`
              w-full py-4 px-6 font-bold text-lg rounded-xl transition-all
              ${selectedAnswer !== null
                ? 'bg-gradient-to-r from-primary-500 to-secondary-500 text-white shadow-lg hover:shadow-xl'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
          >
            Check Answer
          </button>
        ) : (
          <button
            onClick={handleNextQuestion}
            className="w-full flex items-center justify-center gap-2 py-4 px-6 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl transition-all"
          >
            {isLastQuestion ? 'See Results' : 'Next Question'}
            <ArrowRight size={20} />
          </button>
        )}
      </div>
    </div>
  );
};

export default QuizModule;
