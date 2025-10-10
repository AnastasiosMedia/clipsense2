import React from 'react';
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

  return (
    <div className="space-y-4">
      {/* Clips Selection */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-3">Video Clips</h3>
        <button
          onClick={handlePickClips}
          disabled={disabled}
          className="btn-primary w-full mb-3"
        >
          Pick Clips
        </button>
        <div className="text-sm text-gray-300">
          {fileSelection.clips.length > 0 ? (
            <div>
              <p className="font-medium text-green-400">
                {fileSelection.clips.length} clip{fileSelection.clips.length !== 1 ? 's' : ''} selected
              </p>
              <div className="mt-2 space-y-1 max-h-32 overflow-y-auto">
                {fileSelection.clips.map((clip, index) => (
                  <div key={index} className="text-xs text-gray-400 truncate">
                    {clip.split('/').pop()}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No clips selected</p>
          )}
        </div>
      </div>

      {/* Music Selection */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-3">Music Track</h3>
        <button
          onClick={handlePickMusic}
          disabled={disabled}
          className="btn-primary w-full mb-3"
        >
          Pick Music
        </button>
        <div className="text-sm text-gray-300">
          {fileSelection.music ? (
            <div>
              <p className="font-medium text-green-400">Music selected</p>
              <p className="text-xs text-gray-400 truncate mt-1">
                {fileSelection.music.split('/').pop()}
              </p>
            </div>
          ) : (
            <p className="text-gray-500">No music selected</p>
          )}
        </div>
      </div>
    </div>
  );
};
