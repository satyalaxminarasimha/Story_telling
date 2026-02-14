/**
 * Drawing Canvas Component
 * HTML5 Canvas for kids to draw sketches
 */

import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Pencil, Eraser, Undo, Redo, Trash2, Download } from 'lucide-react';
import type { DrawingCanvasProps, CanvasState } from '../types';

const COLORS = [
  '#1f2937', // Black
  '#ef4444', // Red
  '#f97316', // Orange
  '#eab308', // Yellow
  '#22c55e', // Green
  '#3b82f6', // Blue
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#06b6d4', // Cyan
  '#84cc16', // Lime
];

const BRUSH_SIZES = [
  { label: 'S', size: 3 },
  { label: 'M', size: 6 },
  { label: 'L', size: 12 },
  { label: 'XL', size: 20 },
];

export const DrawingCanvas: React.FC<DrawingCanvasProps> = ({
  onImageCapture,
  width = 600,
  height = 400,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [state, setState] = useState<CanvasState>({
    isDrawing: false,
    color: '#1f2937',
    brushSize: 6,
    history: [],
    historyIndex: -1,
  });
  const [tool, setTool] = useState<'pencil' | 'eraser'>('pencil');

  // Initialize canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    // Save initial state
    saveToHistory();
  }, [width, height]);

  const saveToHistory = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const imageData = ctx.getImageData(0, 0, width, height);
    
    setState(prev => {
      const newHistory = prev.history.slice(0, prev.historyIndex + 1);
      newHistory.push(imageData);
      return {
        ...prev,
        history: newHistory.slice(-50), // Keep last 50 states
        historyIndex: newHistory.length - 1,
      };
    });
  }, [width, height]);

  const getCoordinates = (
    event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ): { x: number; y: number } => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if ('touches' in event) {
      const touch = event.touches[0];
      return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY,
      };
    }

    return {
      x: (event.clientX - rect.left) * scaleX,
      y: (event.clientY - rect.top) * scaleY,
    };
  };

  const startDrawing = (
    event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    event.preventDefault();
    const coords = getCoordinates(event);
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.beginPath();
    ctx.moveTo(coords.x, coords.y);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.lineWidth = state.brushSize;
    ctx.strokeStyle = tool === 'eraser' ? '#ffffff' : state.color;

    setState(prev => ({ ...prev, isDrawing: true }));
  };

  const draw = (
    event: React.MouseEvent<HTMLCanvasElement> | React.TouchEvent<HTMLCanvasElement>
  ) => {
    event.preventDefault();
    if (!state.isDrawing) return;

    const coords = getCoordinates(event);
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.lineTo(coords.x, coords.y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    if (state.isDrawing) {
      saveToHistory();
    }
    setState(prev => ({ ...prev, isDrawing: false }));
  };

  const undo = () => {
    if (state.historyIndex <= 0) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const newIndex = state.historyIndex - 1;
    ctx.putImageData(state.history[newIndex], 0, 0);
    setState(prev => ({ ...prev, historyIndex: newIndex }));
  };

  const redo = () => {
    if (state.historyIndex >= state.history.length - 1) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const newIndex = state.historyIndex + 1;
    ctx.putImageData(state.history[newIndex], 0, 0);
    setState(prev => ({ ...prev, historyIndex: newIndex }));
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    saveToHistory();
  };

  const captureImage = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const imageData = canvas.toDataURL('image/png');
    onImageCapture(imageData);
  };

  const downloadImage = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const link = document.createElement('a');
    link.download = 'my-drawing.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-4 p-4 bg-white rounded-xl shadow-lg">
        {/* Tools */}
        <div className="flex gap-2">
          <button
            onClick={() => setTool('pencil')}
            className={`p-3 rounded-lg transition-all ${
              tool === 'pencil'
                ? 'bg-primary-500 text-white shadow-lg'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
            title="Pencil"
          >
            <Pencil size={24} />
          </button>
          <button
            onClick={() => setTool('eraser')}
            className={`p-3 rounded-lg transition-all ${
              tool === 'eraser'
                ? 'bg-primary-500 text-white shadow-lg'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
            title="Eraser"
          >
            <Eraser size={24} />
          </button>
        </div>

        {/* Divider */}
        <div className="w-px h-10 bg-gray-300" />

        {/* Colors */}
        <div className="flex flex-wrap gap-2">
          {COLORS.map((color) => (
            <button
              key={color}
              onClick={() => {
                setState(prev => ({ ...prev, color }));
                setTool('pencil');
              }}
              className={`w-8 h-8 rounded-full transition-transform hover:scale-110 ${
                state.color === color && tool === 'pencil' ? 'ring-4 ring-primary-400 ring-offset-2' : ''
              }`}
              style={{ backgroundColor: color }}
              title={color}
            />
          ))}
        </div>

        {/* Divider */}
        <div className="w-px h-10 bg-gray-300" />

        {/* Brush sizes */}
        <div className="flex gap-2">
          {BRUSH_SIZES.map(({ label, size }) => (
            <button
              key={size}
              onClick={() => setState(prev => ({ ...prev, brushSize: size }))}
              className={`w-10 h-10 rounded-lg font-bold transition-all ${
                state.brushSize === size
                  ? 'bg-primary-500 text-white shadow-lg'
                  : 'bg-gray-100 hover:bg-gray-200'
              }`}
              title={`Brush size ${label}`}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="w-px h-10 bg-gray-300" />

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={undo}
            disabled={state.historyIndex <= 0}
            className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Undo"
          >
            <Undo size={24} />
          </button>
          <button
            onClick={redo}
            disabled={state.historyIndex >= state.history.length - 1}
            className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Redo"
          >
            <Redo size={24} />
          </button>
          <button
            onClick={clearCanvas}
            className="p-3 rounded-lg bg-red-100 hover:bg-red-200 text-red-600"
            title="Clear canvas"
          >
            <Trash2 size={24} />
          </button>
          <button
            onClick={downloadImage}
            className="p-3 rounded-lg bg-gray-100 hover:bg-gray-200"
            title="Download drawing"
          >
            <Download size={24} />
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div className="relative rounded-xl overflow-hidden shadow-xl border-4 border-white">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className="canvas-container cursor-crosshair bg-white w-full"
          style={{ touchAction: 'none' }}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
      </div>

      {/* Submit button */}
      <button
        onClick={captureImage}
        className="w-full py-4 px-6 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-bold text-xl rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all btn-glow"
      >
        ✨ Create Story from Drawing! ✨
      </button>
    </div>
  );
};

export default DrawingCanvas;
