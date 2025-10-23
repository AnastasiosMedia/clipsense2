import React, { useState, useEffect } from 'react';
import { AutoCutRequest, StoryStyle, StylePreset } from '../types';
import { StoryboardGallery } from './StoryboardGallery';

interface StoryboardPreviewProps {
  fileSelection: {
    clips: string[];
    music: string | null;
  };
  qualitySettings: any;
  onClose: () => void;
  onGenerate: (request: AutoCutRequest) => void;
}

interface PreviewData {
  selected_clips: any[];
  timeline: any[];
  music_analysis: {
    tempo: number;
    beat_times: number[];
    bar_times: number[];
    time_signature: string;
  };
  story_arc: {
    total_clips: number;
    story_flow: string[];
    emotional_journey: string[];
    key_moments: number[];
  };
  total_duration: number;
  target_duration: number;
}

const StoryboardPreview: React.FC<StoryboardPreviewProps> = ({
  fileSelection,
  qualitySettings,
  onClose,
  onGenerate
}) => {
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStoryStyle, setSelectedStoryStyle] = useState<string>('traditional');
  const [selectedStylePreset, setSelectedStylePreset] = useState<string>('romantic');
  const [useAISelection, setUseAISelection] = useState<boolean>(true);
  const [viewMode, setViewMode] = useState<'detailed' | 'gallery'>('detailed');
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false);
  const [showModalContent, setShowModalContent] = useState(true);
  const [progressStep, setProgressStep] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [hasStartedGeneration, setHasStartedGeneration] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);

  // Fade-in animation on mount
  useEffect(() => {
    // Trigger fade-in animation
    const timer = setTimeout(() => {
      setIsModalVisible(true);
    }, 10); // Small delay to ensure DOM is ready
    
    return () => clearTimeout(timer);
  }, []);

  // Prevent background scrolling when modal is open
  useEffect(() => {
    // Disable body scroll when modal opens
    document.body.style.overflow = 'hidden';
    
    // Cleanup: re-enable body scroll when modal closes
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, []);

  const storyStyles: StoryStyle[] = [
    { id: 'traditional', name: 'Traditional', description: 'Classic wedding story flow' },
    { id: 'modern', name: 'Modern', description: 'Contemporary and energetic' },
    { id: 'intimate', name: 'Intimate', description: 'Personal and emotional' },
    { id: 'destination', name: 'Destination', description: 'Adventure and travel focused' }
  ];

  const stylePresets: StylePreset[] = [
    { id: 'romantic', name: 'Romantic', description: 'Soft and dreamy', story_style: 'traditional' },
    { id: 'energetic', name: 'Energetic', description: 'Upbeat and dynamic', story_style: 'modern' },
    { id: 'cinematic', name: 'Cinematic', description: 'Dramatic and film-like', story_style: 'intimate' },
    { id: 'documentary', name: 'Documentary', description: 'Natural and authentic', story_style: 'destination' }
  ];

  const filteredPresets = stylePresets.filter(preset => preset.story_style === selectedStoryStyle);

  const handlePreview = async () => {
    if (!fileSelection.music) {
      setError('Please select music first');
      return;
    }

    // Mark that generation has started (permanently hide AI Selection Options)
    setHasStartedGeneration(true);
    
    setIsLoading(true);
    setIsGeneratingPreview(true);
    setProgressStep(0);
    setError(null);

    try {
      const { ApiService } = await import('../services/api');
      
      const request: AutoCutRequest = {
        clips: fileSelection.clips,
        music: fileSelection.music,
        target_seconds: fileSelection.clips.length > 20 ? 120 : 60,
        quality_settings: qualitySettings,
        story_style: selectedStoryStyle,
        style_preset: selectedStylePreset,
        use_ai_selection: useAISelection
      };

      console.log('🧪 Preview request →', {
        clipsCount: request.clips.length,
        music: request.music,
        target_seconds: request.target_seconds,
        quality_settings: request.quality_settings
      });

      // Update progress: Step 1 - Analyzing video clips
      setProgressStep(1);

      // Start async job
      const startT = Date.now();
      const startResp = await ApiService.previewStart(request);
      console.log('🧪 Preview start ←', { ok: startResp?.ok, job_id: startResp?.job_id, durationMs: Date.now() - startT });
      if (!startResp.ok || !startResp.job_id) {
        setError(startResp.error || 'Failed to start preview');
        return;
      }

      // Update progress: Step 2 - Detecting objects and scenes
      setProgressStep(2);
      
      // Add a small delay to show step 2
      await new Promise(resolve => setTimeout(resolve, 800));

      // Poll status until completed
      const jobId = startResp.job_id;
      const pollIntervalMs = 2000; // Increased interval
      const maxPolls = Math.ceil((request.target_seconds * 2000) / pollIntervalMs) + 40;
      let polls = 0;
      while (polls < maxPolls) {
        polls++;
        
        // Update progress based on polling stage - much slower progression
        if (polls === 1) {
          setProgressStep(3); // Analyzing emotional content
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else if (polls === 3) {
          setProgressStep(4); // Processing music and timing
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else if (polls === 6) {
          setProgressStep(5); // Creating story narrative
          await new Promise(resolve => setTimeout(resolve, 1000));
        } else if (polls === 10) {
          setProgressStep(6); // Generating final preview
        }
        
        const status = await ApiService.previewStatus(jobId);
        console.log('🧪 Preview status ←', status);
          if (status.status === 'completed') {
          try {
            const res = await ApiService.previewResult(jobId);
            console.log('🧪 Preview result ←', res);
          if (res && (res as any).ok) {
            const preview = (res as any).preview;
            const results = (res as any).results;
            if (preview) {
              setPreviewData(preview);
            } else if (Array.isArray(results)) {
              // Fallback: build minimal preview from results array
              setPreviewData({
                selected_clips: results,
                timeline: [],
                music_analysis: {},
                story_arc: {
                  total_clips: results.length,
                  story_flow: results.map((r:any)=>r?.story_arc?.scene_classification).filter(Boolean),
                  emotional_journey: results.map((r:any)=>r?.story_arc?.emotional_tone).filter(Boolean),
                  key_moments: []
                },
                total_duration: 0,
                target_duration: 0
              } as any);
            } else {
              setError('Preview result missing payload');
            }
          } else {
            setError('Failed to get preview result');
          }
          } catch (resultError) {
            console.error('❌ Preview result error:', resultError);
            setError(`Failed to load preview result: ${resultError instanceof Error ? resultError.message : 'Unknown error'}`);
          }
          return;
        }
        if (status.status === 'failed') {
          setError(status.error || 'Preview failed');
          return;
        }
        await new Promise(r => setTimeout(r, pollIntervalMs));
      }
      setError('Preview timed out while waiting for result');
    } catch (err) {
      console.error('❌ Preview error (exception):', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
      setIsGeneratingPreview(false);
    }
  };

  const handleClose = () => {
    // Start fade-out animation
    setIsModalVisible(false);
    
    // Wait for animation to complete before calling onClose
    setTimeout(() => {
      onClose();
    }, 500); // Match the transition duration
  };

  const handleGenerate = () => {
    if (!fileSelection.music) return;

    // Mark that generation has started (permanently hide AI Selection Options)
    setHasStartedGeneration(true);
    
    // Immediately start generating preview with progress updates
    setIsGeneratingPreview(true);
    setProgressStep(0);
    setProgressMessage('Initializing analysis...');
    
    // Progress simulation with realistic steps
    const progressSteps = [
      { step: 1, message: 'Analyzing video clips...', delay: 500 },
      { step: 2, message: 'Detecting objects and scenes...', delay: 800 },
      { step: 3, message: 'Analyzing emotional content...', delay: 600 },
      { step: 4, message: 'Processing music and timing...', delay: 700 },
      { step: 5, message: 'Creating story narrative...', delay: 600 },
      { step: 6, message: 'Generating final preview...', delay: 500 }
    ];

    let currentStep = 0;
    const updateProgress = () => {
      if (currentStep < progressSteps.length) {
        const { step, message, delay } = progressSteps[currentStep];
        setProgressStep(step);
        setProgressMessage(message);
        currentStep++;
        setTimeout(updateProgress, delay);
      } else {
        // Complete the generation
        setIsGeneratingPreview(false);
        setProgressStep(0);
        setProgressMessage('');
        
        const request: AutoCutRequest = {
          clips: fileSelection.clips,
          music: fileSelection.music,
          target_seconds: fileSelection.clips.length > 20 ? 120 : 60,
          quality_settings: qualitySettings,
          story_style: selectedStoryStyle,
          style_preset: selectedStylePreset,
          use_ai_selection: useAISelection
        };

        onGenerate(request);
      }
    };

    // Start progress updates
    setTimeout(updateProgress, 100);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // @ts-expect-error helper retained for future use
  const getEmotionColor = (emotion: string) => {
    const colors: { [key: string]: string } = {
      'joy': 'text-yellow-400',
      'love': 'text-pink-400',
      'excitement': 'text-red-400',
      'tenderness': 'text-[#aaaaaa]',
      'celebration': 'text-orange-400',
      'happiness': 'text-green-400',
      'romance': 'text-rose-400',
      'euphoria': 'text-[#aaaaaa]'
    };
    return colors[emotion] || 'text-[#888888]';
  };

  const getSceneTypeIcon = (sceneType: string) => {
    const icons: { [key: string]: string } = {
      'ceremony': '💒',
      'reception': '🎉',
      'preparation': '💄',
      'first_look': '👀',
      'vows': '💍',
      'dance': '💃',
      'toast': '🥂',
      'cake': '🎂',
      'bouquet': '💐',
      'exit': '🚗'
    };
    return icons[sceneType] || '🎬';
  };

  const findSelectedClipInfo = (clipName: string) => {
    try {
      if (!previewData || !previewData.selected_clips) return null;
      const match = previewData.selected_clips.find((c: any) => {
        const p = (c.path || c.clip_path || '').toString();
        return p.endsWith(clipName) || p.includes(clipName);
      });
      return match || null;
    } catch {
      return null;
    }
  };

  // @ts-expect-error helper retained for future use
  const getSceneFromSources = (clip: any) => {
    return (
      clip?.ai_analysis?.story_arc?.scene_classification ||
      clip?.ai_analysis?.object_analysis?.scene_classification ||
      findSelectedClipInfo(clip.clip_name)?.scene ||
      '—'
    );
  };

  // @ts-expect-error helper retained for future use
  const getEmotionFromSources = (clip: any) => {
    return (
      clip?.ai_analysis?.emotion_analysis?.overall_sentiment ||
      findSelectedClipInfo(clip.clip_name)?.tone ||
      '—'
    );
  };

  // @ts-expect-error helper retained for future use
  const getScoreFromSources = (clip: any) => {
    const s = clip?.ai_analysis?.overall_score ?? findSelectedClipInfo(clip.clip_name)?.score;
    return typeof s === 'number' ? `${Math.round(s * 100)}%` : '—';
  };

  // @ts-expect-error helper retained for future use
  const getObjectsFromSources = (clip: any) => {
    try {
      const objs = clip?.ai_analysis?.object_analysis?.objects_detected || {};
      const top = Object.entries(objs)
        .filter(([, v]) => (v as number) > 0)
        .sort((a, b) => (b[1] as number) - (a[1] as number))
        .slice(0, 3)
        .map(([k, v]) => `${(k as string).replace(/_/g, ' ')}(${v as number})`);
      if (top.length) return top.join(', ');
    } catch {}
    return '—';
  };

  return (
    <div 
      className={`fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6 transition-all duration-500 ease-in-out ${
        isModalVisible ? 'opacity-100' : 'opacity-0'
      }`}
      onClick={(e) => {
        // Close modal when clicking on backdrop
        if (e.target === e.currentTarget) {
          handleClose();
        }
      }}
      onWheel={(e) => {
        // Prevent scroll propagation to background
        e.stopPropagation();
      }}
    >
      <div 
        className={`bg-[#0d0d0d] border border-[#1a1a1a] rounded-2xl w-[95vw] h-[90vh] max-w-7xl overflow-hidden transition-all duration-500 ease-in-out ${
          isModalVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'
        }`}
        onClick={(e) => {
          // Prevent modal from closing when clicking inside
          e.stopPropagation();
        }}
      >
        {/* Generating Preview Animation - Always visible when generating */}
        {isGeneratingPreview && (
          <div className="absolute inset-0 flex items-center justify-center p-6 z-10">
            <div className="max-w-2xl mx-auto space-y-6 h-[calc(90vh-200px)] flex flex-col justify-center transition-all duration-500 ease-in-out">
              <div className="text-center transition-all duration-500 ease-in-out">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-[#007acc] mx-auto mb-6 transition-all duration-300"></div>
                <h2 className="text-2xl font-bold text-white mb-4 transition-all duration-300">Generating Preview...</h2>
                
                {/* Progress Steps */}
                <div className="space-y-3 mb-6 w-full max-w-sm mx-auto transition-all duration-500 ease-in-out">
                  {[1, 2, 3, 4, 5, 6].map((step) => (
                    <div key={step} className={`flex items-center justify-center space-x-3 transition-all duration-300 ease-in-out ${
                      step <= progressStep ? 'text-white' : 'text-[#666666]'
                    }`}>
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ease-in-out ${
                        step <= progressStep 
                          ? 'bg-[#007acc] text-white' 
                          : 'bg-[#333333] text-[#666666]'
                      }`}>
                        {step < progressStep ? '✓' : step}
                      </div>
                      <span className="text-sm font-medium transition-all duration-300 ease-in-out">
                        {step === 1 && 'Analyzing video clips...'}
                        {step === 2 && 'Detecting objects and scenes...'}
                        {step === 3 && 'Analyzing emotional content...'}
                        {step === 4 && 'Processing music and timing...'}
                        {step === 5 && 'Creating story narrative...'}
                        {step === 6 && 'Generating final preview...'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modal Content with Fade Animation */}
        <div className={`transition-opacity duration-300 ${showModalContent ? 'opacity-100' : 'opacity-0'}`}>
          {/* Header */}
          <div className="relative p-6 border-b border-[#1a1a1a]">
            {/* Close button - top right */}
            <button 
              onClick={handleClose} 
              className="absolute top-4 right-4 p-3 rounded-xl border border-transparent hover:border-[#333333] hover:text-white text-[#888888] text-2xl font-bold"
            >
              ×
            </button>
            
            {/* Centered header content */}
            <div className="flex flex-col items-center text-center">
              <div className="w-20 h-20 rounded-xl flex items-center justify-center overflow-hidden">
                <img 
                  src="/cs01.png" 
                  alt="ClipSense Logo" 
                  className="w-full h-full object-cover rounded-lg"
                />
              </div>
              <h2 className="text-2xl font-bold text-white">Storyboard Preview</h2>
              <p className="text-[#888888]">AI-powered clip selection and timeline</p>
            </div>
          </div>

          <div className="p-6 overflow-y-auto h-[calc(90vh-120px)] scrollable">
            {/* Ensure a single root inside scroll area to avoid adjacent JSX parse issues */}
            <div>
            {/* AI Selection Options - Hide permanently after generation starts */}
            {!hasStartedGeneration && (
          <div className="max-w-2xl mx-auto mb-8 space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-xl font-semibold text-white mb-2">AI-Powered Content Selection</h3>
              <p className="text-[#888888]">
                Configure how the AI will select and arrange your clips
              </p>
            </div>
                {/* AI Toggle */}
                <div className="flex items-center justify-center space-x-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={useAISelection}
                      onChange={(e) => setUseAISelection(e.target.checked)}
                      className="w-4 h-4 text-[#007acc] bg-[#0f0f0f] border-[#1a1a1a] rounded focus:ring-[#007acc] focus:ring-2"
                    />
                    <span className="text-white">Use AI-powered content selection</span>
                  </label>
                </div>

                {useAISelection && (
                  <>
                    {/* Story Style Selection */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">Story Style</label>
                      <div className="grid grid-cols-2 gap-3">
                        {storyStyles.map((style) => (
                          <button
                            key={style.id}
                            onClick={() => {
                              setSelectedStoryStyle(style.id);
                              // Reset preset when story style changes
                              const newPresets = stylePresets.filter(p => p.story_style === style.id);
                              if (newPresets.length > 0) {
                                setSelectedStylePreset(newPresets[0].id);
                              }
                            }}
                            className={`p-3 rounded-lg border text-left transition-all ${
                              selectedStoryStyle === style.id
                                ? 'border-[#007acc] text-[#007acc]'
                                : 'border-[#1a1a1a] text-[#888888] hover:border-[#0099ff] hover:text-white'
                            }`}
                          >
                            <div className="font-medium">{style.name}</div>
                            <div className="text-xs text-[#888888] mt-1">{style.description}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Style Preset Selection */}
                    <div>
                      <label className="block text-sm font-medium text-white mb-3">Style Preset</label>
                      <div className="grid grid-cols-2 gap-3">
                        {filteredPresets.map((preset) => (
                          <button
                            key={preset.id}
                            onClick={() => setSelectedStylePreset(preset.id)}
                            className={`p-3 rounded-lg border text-left transition-all ${
                              selectedStylePreset === preset.id
                                ? 'border-[#007acc] text-[#007acc]'
                                : 'border-[#1a1a1a] text-[#888888] hover:border-[#0099ff] hover:text-white'
                            }`}
                          >
                            <div className="font-medium">{preset.name}</div>
                            <div className="text-xs text-[#888888] mt-1">{preset.description}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </>
                )}

              {error && (
                <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-4 mb-6 max-w-md mx-auto">
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}

              <div className="text-center">
                <button onClick={handlePreview} disabled={isLoading || !fileSelection.music} className="btn-primary text-lg px-8 py-4">
                  {isLoading ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                      Analyzing...
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Generate Preview
                    </div>
                  )}
                </button>
              </div>
            </div>
            )}

            {/* Preview Data Display - Hide during generation */}
            {previewData && !isGeneratingPreview && (
            <div className="space-y-8">
              {/* Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-[#0f0f0f] rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-white">{previewData?.story_arc?.total_clips ?? (previewData?.selected_clips?.length ?? 0)}</div>
                  <div className="text-sm text-[#888888]">Selected Clips</div>
                </div>
                <div className="bg-[#0f0f0f] rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-white">{typeof previewData?.music_analysis?.tempo === 'number' ? previewData.music_analysis.tempo.toFixed(0) : '—'}</div>
                  <div className="text-sm text-[#888888]">BPM</div>
                </div>
                <div className="bg-[#0f0f0f] rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-white">{formatTime(previewData?.total_duration || 0)}</div>
                  <div className="text-sm text-[#888888]">Duration</div>
                </div>
                <div className="bg-[#0f0f0f] rounded-xl p-4 text-center">
                  <div className="text-2xl font-bold text-white">{previewData?.story_arc?.key_moments?.length ?? 0}</div>
                  <div className="text-sm text-[#888888]">Key Moments</div>
                </div>
              </div>

              {/* View Mode Toggle */}
              <div className="flex justify-center mb-8">
                <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-1 flex">
                  <button
                    onClick={() => setViewMode('detailed')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                      viewMode === 'detailed'
                        ? 'bg-[#007acc] text-white'
                        : 'text-[#888888] hover:text-white'
                    }`}
                  >
                    Detailed Analysis
                  </button>
                  <button
                    onClick={() => setViewMode('gallery')}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                      viewMode === 'gallery'
                        ? 'bg-[#007acc] text-white'
                        : 'text-[#888888] hover:text-white'
                    }`}
                  >
                    Storyboard Gallery
                  </button>
                </div>
              </div>

              {/* AI Analysis Summary */}
              {previewData.story_arc && viewMode === 'detailed' && (
                <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-6 mb-8">
                  <h3 className="text-xl font-medium text-white mb-4">
                    AI Analysis Summary
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <h4 className="text-[#aaaaaa] font-medium mb-2">Story Flow</h4>
                      <div className="flex flex-wrap gap-2">
                        {previewData.story_arc.story_flow?.map((scene, idx) => (
                          <span key={idx} className="bg-gray-800 text-[#aaaaaa] px-3 py-1 rounded text-sm border border-gray-700">
                            {scene}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-[#aaaaaa] font-medium mb-2">Emotional Journey</h4>
                      <div className="flex flex-wrap gap-2">
                        {previewData.story_arc.emotional_journey?.map((tone, idx) => (
                          <span key={idx} className="bg-gray-800 text-[#aaaaaa] px-3 py-1 rounded text-sm border border-gray-700">
                            {tone}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-[#aaaaaa] font-medium mb-2">Total Clips Analyzed</h4>
                      <div className="text-2xl font-bold text-white">
                        {previewData.story_arc.total_clips || 0}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Analysis Results */}
              {viewMode === 'detailed' && (
                <div>
                  <h3 className="text-xl font-medium text-white mb-6">
                    Detailed Clip Analysis
                  </h3>

                  <div className="space-y-6">
                  {(previewData.selected_clips || []).map((clip, index) => (
                    <div key={index} className="bg-[#0d0d0d] border border-[#1a1a1a] rounded-lg p-6">
                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Large Thumbnail with Video Aspect Ratio */}
                        <div className="lg:col-span-1">
                          <div className="w-full bg-[#0f0f0f] rounded-lg flex items-center justify-center">
                            {clip.thumbnail_path ? (
                              <div className="relative w-full" style={{ aspectRatio: '16/9' }}>
                                <img
                                  src={`http://127.0.0.1:8123${clip.thumbnail_path}`}
                                  alt={clip.path?.split('/').pop() || 'Clip'}
                                  className="w-full h-full object-cover rounded-lg"
                                />
                              </div>
                            ) : (
                              <div className="w-full text-[#777777] text-center" style={{ aspectRatio: '16/9' }}>
                                <div className="flex flex-col items-center justify-center h-full">
                                  <div className="text-4xl mb-2">📹</div>
                                  <div className="text-sm">No Preview</div>
                                </div>
                              </div>
                            )}
                          </div>
                          
                          {/* Quick Stats under thumbnail */}
                          <div className="mt-4 space-y-2">
                            <div className="flex items-center justify-between py-2 border-b border-[#1a1a1a]">
                              <span className="text-[#888888] text-sm">Score</span>
                              <span className="text-xl font-medium text-white">
                                {Math.round((clip.score || 0) * 100)}%
                              </span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-[#1a1a1a]">
                              <span className="text-[#888888] text-sm">Emotional Tone</span>
                              <span className="text-white text-sm font-medium">{clip.tone || 'Unknown'}</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-[#1a1a1a]">
                              <span className="text-[#888888] text-sm">Story Importance</span>
                              <span className="text-white text-sm font-medium">{Math.round((clip.importance || 0) * 100)}%</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-[#1a1a1a]">
                              <span className="text-[#888888] text-sm">Scene Type</span>
                              <span className="text-white text-sm font-medium">{clip.scene || 'Unknown'}</span>
                            </div>
                          </div>
                        </div>

                        {/* Clip Info - Now takes 2 columns */}
                        <div className="lg:col-span-2">
                          <div className="mb-6">
                            <h4 className="text-xl font-medium text-white truncate">
                              {clip.path?.split('/').pop() || `Clip ${index + 1}`}
                            </h4>
                          </div>

                          {/* AI Analysis - Primary Content */}
                          {clip.description && (
                            <div className="mb-6 p-6 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg">
                              <h5 className="text-white font-medium mb-3 text-lg">AI Analysis</h5>
                              <p className="text-white text-base leading-relaxed">
                                {clip.description}
                              </p>
                            </div>
                          )}

                        </div>
                      </div>
                    </div>
                  ))}
                  </div>
                </div>
              )}

              {/* Storyboard Gallery */}
              {viewMode === 'gallery' && previewData.selected_clips && (
                <StoryboardGallery 
                  clips={previewData.selected_clips}
                  onClipClick={(clip, index) => {
                    // Optional: Handle clip click (e.g., show detailed view)
                    console.log('Clicked clip:', clip, 'at index:', index);
                  }}
                />
              )}

              {/* Actions */}
              <div className="flex justify-center space-x-4 pt-6 border-t border-[#1a1a1a]">
                <button onClick={handleClose} className="btn-secondary px-8 py-3">Cancel</button>
                <button onClick={handleGenerate} className="btn-primary px-8 py-3">Generate Video</button>
              </div>
            </div>
            )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default StoryboardPreview;


