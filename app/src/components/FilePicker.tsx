import React, { useState, useCallback } from 'react';
import { open } from '@tauri-apps/api/dialog';
import { FileSelection } from '../types';

interface FilePickerProps {
  fileSelection: FileSelection;
  onFileSelectionChange: (selection: FileSelection) => void;
  disabled?: boolean;
}

export const FilePicker: React.FC<FilePickerProps> = ({
  fileSelection,
  onFileSelectionChange,
  disabled = false
}) => {
  const [dragOverClips, setDragOverClips] = useState(false);
  const [dragOverMusic, setDragOverMusic] = useState(false);
  const handlePickClips = async () => {
    try {
      const selected = await open({
        multiple: true,
        filters: [
          {
            name: 'Video Files',
            extensions: ['mp4', 'mov', 'avi', 'mkv', 'webm']
          }
        ]
      });

      if (selected && Array.isArray(selected)) {
        onFileSelectionChange({
          ...fileSelection,
          clips: selected
        });
      }
    } catch (error) {
      console.error('Error picking clips:', error);
    }
  };

  const handlePickMusic = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [
          {
            name: 'Audio Files',
            extensions: ['mp3', 'wav', 'm4a', 'aac', 'flac']
          }
        ]
      });

      if (selected && typeof selected === 'string') {
        onFileSelectionChange({
          ...fileSelection,
          music: selected
        });
      }
    } catch (error) {
      console.error('Error picking music:', error);
    }
  };

  // Drag and drop handlers for video clips
  const handleDragOverClips = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setDragOverClips(true);
    }
  }, [disabled]);

  const handleDragLeaveClips = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverClips(false);
  }, []);

  const handleDropClips = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverClips(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    const videoFiles = files.filter(file => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      return ['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(extension || '');
    });

    if (videoFiles.length > 0) {
      const filePaths = videoFiles.map(file => file.path);
      onFileSelectionChange({
        ...fileSelection,
        clips: [...fileSelection.clips, ...filePaths]
      });
    }
  }, [disabled, fileSelection, onFileSelectionChange]);

  // Drag and drop handlers for music
  const handleDragOverMusic = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setDragOverMusic(true);
    }
  }, [disabled]);

  const handleDragLeaveMusic = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverMusic(false);
  }, []);

  const handleDropMusic = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverMusic(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files);
    const audioFiles = files.filter(file => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      return ['mp3', 'wav', 'm4a', 'aac', 'flac'].includes(extension || '');
    });

    if (audioFiles.length > 0) {
      // Take the first audio file
      onFileSelectionChange({
        ...fileSelection,
        music: audioFiles[0].path
      });
    }
  }, [disabled, fileSelection, onFileSelectionChange]);

  return (
    <div className="space-y-4">
      {/* Clips Selection */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-3">Video Clips</h3>
        
        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOverClips}
          onDragLeave={handleDragLeaveClips}
          onDrop={handleDropClips}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors duration-200 mb-3 ${
            dragOverClips
              ? 'border-[#007acc] bg-[#007acc]/10'
              : 'border-[#1a1a1a] hover:border-[#333333]'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <div className="text-[#888888] mb-2">
            <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-sm font-medium">Drop video files here</p>
            <p className="text-xs text-[#666666] mt-1">or click the button below</p>
          </div>
        </div>

        <button
          onClick={handlePickClips}
          disabled={disabled}
          className="btn-primary w-full mb-3"
        >
          Pick Clips
        </button>
        <div className="text-sm text-[#aaaaaa]">
          {fileSelection.clips.length > 0 ? (
            <div>
              <p className="font-medium text-green-400">
                {fileSelection.clips.length} clip{fileSelection.clips.length !== 1 ? 's' : ''} selected
              </p>
              <div className="mt-2 space-y-1 max-h-32 overflow-y-auto scrollable">
                {fileSelection.clips.map((clip, index) => (
                  <div key={index} className="text-xs text-[#888888] truncate">
                    {clip.split('/').pop()}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-[#777777]">No clips selected</p>
          )}
        </div>
      </div>

      {/* Music Selection */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-3">Music Track</h3>
        
        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOverMusic}
          onDragLeave={handleDragLeaveMusic}
          onDrop={handleDropMusic}
          className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors duration-200 mb-3 ${
            dragOverMusic
              ? 'border-[#007acc] bg-[#007acc]/10'
              : 'border-[#1a1a1a] hover:border-[#333333]'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        >
          <div className="text-[#888888] mb-2">
            <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            <p className="text-sm font-medium">Drop audio file here</p>
            <p className="text-xs text-[#666666] mt-1">or click the button below</p>
          </div>
        </div>

        <button
          onClick={handlePickMusic}
          disabled={disabled}
          className="btn-primary w-full mb-3"
        >
          Pick Music
        </button>
        <div className="text-sm text-[#aaaaaa]">
          {fileSelection.music ? (
            <div>
              <p className="font-medium text-green-400">Music selected</p>
              <p className="text-xs text-[#888888] truncate mt-1">
                {fileSelection.music.split('/').pop()}
              </p>
            </div>
          ) : (
            <p className="text-[#777777]">No music selected</p>
          )}
        </div>
      </div>
    </div>
  );
};
