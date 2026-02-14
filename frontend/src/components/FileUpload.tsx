/**
 * File Upload Component
 * For uploading textbook diagrams and images
 */

import React, { useRef, useState, useCallback } from 'react';
import { Upload, Image, X, FileImage } from 'lucide-react';
import type { FileUploadProps } from '../types';

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  accept = 'image/png,image/jpeg,image/jpg',
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processFile = useCallback((file: File) => {
    setError(null);

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a PNG or JPEG image');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Image must be less than 10MB');
      return;
    }

    // Read and convert to base64
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setPreview(result);
    };
    reader.onerror = () => {
      setError('Failed to read file');
    };
    reader.readAsDataURL(file);
  }, []);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      processFile(file);
    }
  }, [processFile]);

  const handleDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
  }, []);

  const clearPreview = () => {
    setPreview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = () => {
    if (preview) {
      onFileSelect(preview);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        onChange={handleFileChange}
        className="hidden"
      />

      {!preview ? (
        /* Drop zone */
        <div
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            relative p-12 border-4 border-dashed rounded-2xl cursor-pointer
            transition-all duration-300 text-center
            ${isDragging
              ? 'border-primary-500 bg-primary-50 scale-[1.02]'
              : 'border-gray-300 bg-white hover:border-primary-400 hover:bg-primary-50'
            }
          `}
        >
          <div className="flex flex-col items-center gap-4">
            <div className={`
              p-6 rounded-full transition-all
              ${isDragging ? 'bg-primary-200 animate-bounce' : 'bg-primary-100'}
            `}>
              <Upload size={48} className="text-primary-600" />
            </div>
            <div>
              <p className="text-xl font-bold text-gray-700">
                Drop your image here
              </p>
              <p className="text-gray-500 mt-2">
                or click to browse files
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <FileImage size={16} />
              <span>PNG, JPG up to 10MB</span>
            </div>
          </div>
        </div>
      ) : (
        /* Preview */
        <div className="relative bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Clear button */}
          <button
            onClick={clearPreview}
            className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full shadow-lg hover:bg-red-600 transition-colors z-10"
            title="Remove image"
          >
            <X size={24} />
          </button>

          {/* Image preview */}
          <div className="p-4">
            <img
              src={preview}
              alt="Upload preview"
              className="w-full max-h-96 object-contain rounded-xl"
            />
          </div>

          {/* Image info */}
          <div className="px-4 pb-4 flex items-center gap-2 text-sm text-gray-500">
            <Image size={16} />
            <span>Image ready for story creation</span>
          </div>
        </div>
      )}

      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-600 flex items-center gap-2">
          <span className="text-xl">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Submit button */}
      {preview && (
        <button
          onClick={handleSubmit}
          className="w-full py-4 px-6 bg-gradient-to-r from-primary-500 to-secondary-500 text-white font-bold text-xl rounded-xl shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all btn-glow"
        >
          📚 Create Story from Image! 📚
        </button>
      )}
    </div>
  );
};

export default FileUpload;
