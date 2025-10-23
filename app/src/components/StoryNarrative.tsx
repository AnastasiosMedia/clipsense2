import React, { useState } from 'react';
import { ApiService } from '../services/api';
import { LiveAnalysis } from './LiveAnalysis';

interface StoryNarrativeProps {
  clips: string[];
  onClose: () => void;
  onGenerateVideo: (selectedClips: any[]) => void;
}

interface StoryNarrativeData {
  story_title: string;
  story_theme: string;
  narrative_structure: string;
  story_arc: any[];
  selected_clips: any[];
  rejected_clips: any[];
  narrative_flow: string;
  emotional_journey: string[];
  story_duration: number;
  story_notes: string;
}

export const StoryNarrative: React.FC<StoryNarrativeProps> = ({
  clips,
  onClose,
  onGenerateVideo
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [storyNarrative, setStoryNarrative] = useState<StoryNarrativeData | null>(null);
  const [narrativeStyle, setNarrativeStyle] = useState('modern');
  const [targetDuration, setTargetDuration] = useState(60);
  const [showLiveAnalysis, setShowLiveAnalysis] = useState(false);

  const narrativeStyles = [
    { value: 'traditional', label: 'Traditional', description: 'Classic wedding story structure' },
    { value: 'modern', label: 'Modern', description: 'Contemporary narrative flow' },
    { value: 'cinematic', label: 'Cinematic', description: 'Dramatic storytelling approach' },
    { value: 'documentary', label: 'Documentary', description: 'Authentic, real-life storytelling' }
  ];

  const handleGenerateStory = async () => {
    setIsGenerating(true);
    try {
      const response = await ApiService.generateStoryNarrative({
        clips,
        narrative_style: narrativeStyle,
        target_duration: targetDuration
      });

      if (response.ok && response.story_narrative) {
        setStoryNarrative(response.story_narrative);
      } else {
        console.error('Failed to generate story narrative:', response.error);
        alert('Failed to generate story narrative. Please try again.');
      }
    } catch (error) {
      console.error('Error generating story narrative:', error);
      alert('Error generating story narrative. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStartLiveAnalysis = () => {
    setShowLiveAnalysis(true);
  };

  const handleLiveAnalysisComplete = (storyData: any) => {
    setStoryNarrative(storyData);
    setShowLiveAnalysis(false);
  };

  const handleLiveAnalysisClose = () => {
    setShowLiveAnalysis(false);
  };

  const handleGenerateVideo = () => {
    if (storyNarrative?.selected_clips) {
      onGenerateVideo(storyNarrative.selected_clips);
    }
  };

  const getEmotionColor = (emotion: string) => {
    const colors: { [key: string]: string } = {
      'romantic': 'text-pink-400',
      'joyful': 'text-yellow-400',
      'intimate': 'text-purple-400',
      'dramatic': 'text-red-400',
      'celebratory': 'text-green-400'
    };
    return colors[emotion] || 'text-gray-400';
  };

  const getSceneIcon = (scene: string) => {
    const icons: { [key: string]: string } = {
      'preparation': '💄',
      'ceremony': '💒',
      'reception': '🍽️',
      'party': '🎉',
      'intimate_moments': '💕',
      'scenic_moments': '🌅'
    };
    return icons[scene] || '🎬';
  };

  if (showLiveAnalysis) {
    return (
      <LiveAnalysis
        clips={clips}
        onClose={handleLiveAnalysisClose}
        onComplete={handleLiveAnalysisComplete}
      />
    );
  }

  if (storyNarrative) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-[#0d0d0d] border border-[#1a1a1a] rounded-lg max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#1a1a1a]">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">📖</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{storyNarrative.story_title}</h2>
                <p className="text-[#888888]">{storyNarrative.story_theme} • {storyNarrative.narrative_structure}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-[#888888] hover:text-white transition-colors p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Story Content */}
          <div className="p-6 space-y-6">
            {/* Narrative Flow */}
            <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Story Flow</h3>
              <p className="text-[#aaaaaa]">{storyNarrative.narrative_flow}</p>
            </div>

            {/* Emotional Journey */}
            <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Emotional Journey</h3>
              <div className="flex flex-wrap gap-2">
                {storyNarrative.emotional_journey.map((emotion, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-[#1a1a1a] text-[#aaaaaa] rounded-full text-sm"
                  >
                    {emotion}
                  </span>
                ))}
              </div>
            </div>

            {/* Selected Clips */}
            <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Selected Clips ({storyNarrative.selected_clips.length})</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {storyNarrative.selected_clips.map((clip, index) => (
                  <div key={index} className="bg-[#1a1a1a] border border-[#333333] rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center">
                        <span className="text-2xl mr-2">{getSceneIcon(clip.scene_type)}</span>
                        <div>
                          <h4 className="text-white font-medium">{Path(clip.clip_path).name}</h4>
                          <p className="text-[#888888] text-sm capitalize">{clip.scene_type}</p>
                        </div>
                      </div>
                      <span className="text-[#888888] text-sm">#{index + 1}</span>
                    </div>
                    
                    <p className="text-[#aaaaaa] text-sm mb-3">{clip.description}</p>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className={`${getEmotionColor(clip.emotional_tone)} capitalize`}>
                        {clip.emotional_tone}
                      </span>
                      <span className="text-[#888888]">
                        Quality: {Math.round(clip.quality_score * 10)}/10
                      </span>
                    </div>
                    
                    {clip.key_moments.length > 0 && (
                      <div className="mt-2">
                        <div className="flex flex-wrap gap-1">
                          {clip.key_moments.slice(0, 3).map((moment, momentIndex) => (
                            <span
                              key={momentIndex}
                              className="px-2 py-1 bg-[#333333] text-[#aaaaaa] rounded text-xs"
                            >
                              {moment}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Rejected Clips */}
            {storyNarrative.rejected_clips && storyNarrative.rejected_clips.length > 0 && (
              <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">Clips Not Selected ({storyNarrative.rejected_clips.length})</h3>
                <div className="space-y-3">
                  {storyNarrative.rejected_clips.map((rejected, index) => (
                    <div key={index} className="bg-[#1a1a1a] border border-[#333333] rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                          <span className="text-2xl mr-2">{getSceneIcon(rejected.clip.scene_type)}</span>
                          <div>
                            <h4 className="text-white font-medium">{Path(rejected.clip.clip_path).name}</h4>
                            <p className="text-[#888888] text-sm capitalize">{rejected.clip.scene_type}</p>
                          </div>
                        </div>
                        <span className="text-[#888888] text-sm">Not Selected</span>
                      </div>
                      
                      <p className="text-[#aaaaaa] text-sm mb-3">{rejected.clip.description}</p>
                      
                      <div className="bg-[#2a1a1a] border border-[#4a3333] rounded p-3">
                        <div className="flex items-center mb-1">
                          <span className="text-red-400 text-sm font-medium">Reason:</span>
                        </div>
                        <p className="text-[#cc8888] text-sm">{rejected.reason}</p>
                        {rejected.scene_attempted && rejected.scene_attempted !== 'none' && (
                          <p className="text-[#888888] text-xs mt-1">
                            Attempted for scene: {rejected.scene_attempted}
                          </p>
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between text-sm mt-2">
                        <span className={`${getEmotionColor(rejected.clip.emotional_tone)} capitalize`}>
                          {rejected.clip.emotional_tone}
                        </span>
                        <span className="text-[#888888]">
                          Quality: {Math.round(rejected.clip.quality_score * 10)}/10
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Story Notes */}
            <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Story Notes</h3>
              <p className="text-[#aaaaaa]">{storyNarrative.story_notes}</p>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[#1a1a1a]">
              <div className="text-[#888888] text-sm">
                Estimated duration: {Math.round(storyNarrative.story_duration)}s
              </div>
              <div className="flex space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 border border-[#1a1a1a] text-[#888888] hover:border-[#333333] hover:text-white transition-colors rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerateVideo}
                  className="px-6 py-2 bg-[#007acc] text-white hover:bg-[#005a9e] transition-colors rounded-lg"
                >
                  Generate Video
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-[#0d0d0d] border border-[#1a1a1a] rounded-lg max-w-2xl w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#1a1a1a]">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg flex items-center justify-center mr-4">
              <span className="text-2xl">📖</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">AI Story Builder</h2>
              <p className="text-[#888888]">Create a flowing narrative from your clips</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-[#888888] hover:text-white transition-colors p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Narrative Style Selection */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Narrative Style</h3>
            <div className="grid grid-cols-2 gap-3">
              {narrativeStyles.map((style) => (
                <button
                  key={style.value}
                  onClick={() => setNarrativeStyle(style.value)}
                  className={`p-3 rounded-lg border transition-colors text-left ${
                    narrativeStyle === style.value
                      ? 'border-[#007acc] bg-[#0f0f0f] text-white'
                      : 'border-[#1a1a1a] bg-[#0f0f0f] text-[#aaaaaa] hover:border-[#333333]'
                  }`}
                >
                  <div className="font-medium">{style.label}</div>
                  <div className="text-sm text-[#888888]">{style.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Target Duration */}
          <div>
            <h3 className="text-lg font-semibold text-white mb-3">Target Duration</h3>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="30"
                max="120"
                value={targetDuration}
                onChange={(e) => setTargetDuration(Number(e.target.value))}
                className="flex-1"
              />
              <span className="text-white font-medium">{targetDuration}s</span>
            </div>
          </div>

          {/* Clip Summary */}
          <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-3">Your Clips</h3>
            <p className="text-[#aaaaaa] mb-2">{clips.length} video clips ready for analysis</p>
            <div className="text-sm text-[#888888]">
              AI will analyze each clip to understand content, emotions, and key moments, then create a coherent story flow.
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-[#1a1a1a]">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-[#1a1a1a] text-[#888888] hover:border-[#333333] hover:text-white transition-colors rounded-lg"
            >
              Cancel
            </button>
            <div className="flex space-x-3">
              <button
                onClick={handleStartLiveAnalysis}
                className="px-6 py-2 bg-[#28a745] text-white hover:bg-[#218838] transition-colors rounded-lg"
              >
                🔍 Live Analysis
              </button>
              <button
                onClick={handleGenerateStory}
                disabled={isGenerating}
                className="px-6 py-2 bg-[#007acc] text-white hover:bg-[#005a9e] disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-lg"
              >
                {isGenerating ? 'Generating Story...' : 'Generate Story'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function to get filename from path
function Path(path: string) {
  return {
    name: path.split('/').pop() || path
  };
}
