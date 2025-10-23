import React, { useState, useEffect, useRef } from 'react';

interface LiveAnalysisProps {
  clips: string[];
  onClose: () => void;
  onComplete: (storyNarrative: any) => void;
}

interface AnalysisProgress {
  type: string;
  data: {
    type: string;
    message: string;
    clip_index?: number;
    total_clips?: number;
    clip_name?: string;
    quality_score?: number;
    scene_type?: string;
    emotional_tone?: string;
    error?: string;
    selected_count?: number;
    rejected_count?: number;
    story_title?: string;
  };
}

export const LiveAnalysis: React.FC<LiveAnalysisProps> = ({
  clips,
  onClose,
  onComplete
}) => {
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('Connecting...');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [storyResult, setStoryResult] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = () => {
      const websocket = new WebSocket('ws://127.0.0.1:8123/ws/live-analysis');
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
        setWs(websocket);
        setCurrentStep('Connected to analysis server');
      };
      
      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'story_progress') {
            handleProgressUpdate(data.data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected');
        setWs(null);
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setCurrentStep('Connection error - please try again');
      };
      
      wsRef.current = websocket;
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const startAnalysis = async () => {
    try {
      setIsAnalyzing(true);
      setCurrentStep('Starting analysis...');
      
      const response = await fetch('http://127.0.0.1:8123/generate_story_narrative_live', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clips,
          narrative_style: 'modern',
          target_duration: 60
        })
      });

      const result = await response.json();
      
      if (result.ok) {
        setStoryResult(result.story_narrative);
        setAnalysisComplete(true);
        setCurrentStep('Analysis complete!');
      } else {
        setCurrentStep(`Analysis failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setCurrentStep(`Analysis error: ${error}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleProgressUpdate = (data: any) => {
    setProgress(prev => [...prev, { type: 'progress', data }]);
    
    switch (data.type) {
      case 'clip_analysis_started':
        setCurrentStep(`Analyzing ${data.clip_name} (${data.clip_index}/${data.total_clips})`);
        break;
      case 'clip_analysis_complete':
        setCurrentStep(`Completed ${data.clip_name} - Score: ${data.quality_score?.toFixed(2)}`);
        break;
      case 'clip_analysis_failed':
        setCurrentStep(`Failed to analyze ${data.clip_name}: ${data.error}`);
        break;
      case 'analysis_started':
        setCurrentStep('Starting story generation...');
        break;
      case 'analysis_complete':
        setCurrentStep('Building story structure...');
        break;
      case 'structure_built':
        setCurrentStep('Selecting clips for story...');
        break;
      case 'clips_selected':
        setCurrentStep(`Selected ${data.selected_count} clips for the story`);
        break;
      case 'story_complete':
        setCurrentStep(`Story "${data.story_title}" completed!`);
        break;
      case 'story_error':
        setCurrentStep(`Story generation failed: ${data.error}`);
        break;
      default:
        setCurrentStep(data.message || 'Processing...');
    }
  };

  const getProgressIcon = (type: string) => {
    switch (type) {
      case 'clip_analysis_started':
        return '🔍';
      case 'clip_analysis_complete':
        return '✅';
      case 'clip_analysis_failed':
        return '❌';
      case 'clip_selected':
        return '🎯';
      case 'clip_rejected':
        return '🚫';
      case 'story_complete':
        return '🎉';
      default:
        return '📝';
    }
  };

  const getProgressColor = (type: string) => {
    switch (type) {
      case 'clip_analysis_complete':
      case 'clip_selected':
      case 'story_complete':
        return 'text-green-400';
      case 'clip_analysis_failed':
      case 'story_error':
        return 'text-red-400';
      case 'clip_rejected':
        return 'text-yellow-400';
      default:
        return 'text-blue-400';
    }
  };

  if (analysisComplete && storyResult) {
    return (
      <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="bg-[#0d0d0d] border border-[#1a1a1a] rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-[#1a1a1a]">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg flex items-center justify-center mr-4">
                <span className="text-2xl">🎉</span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">Analysis Complete!</h2>
                <p className="text-[#888888]">{storyResult.story_title}</p>
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

          {/* Results Summary */}
          <div className="p-6 space-y-4">
            <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3">Story Summary</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-[#888888]">Selected Clips:</span>
                  <span className="text-white ml-2">{storyResult.selected_clips?.length || 0}</span>
                </div>
                <div>
                  <span className="text-[#888888]">Rejected Clips:</span>
                  <span className="text-white ml-2">{storyResult.rejected_clips?.length || 0}</span>
                </div>
                <div>
                  <span className="text-[#888888]">Story Theme:</span>
                  <span className="text-white ml-2 capitalize">{storyResult.story_theme}</span>
                </div>
                <div>
                  <span className="text-[#888888]">Duration:</span>
                  <span className="text-white ml-2">{Math.round(storyResult.story_duration)}s</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[#1a1a1a]">
              <button
                onClick={onClose}
                className="px-4 py-2 border border-[#1a1a1a] text-[#888888] hover:border-[#333333] hover:text-white transition-colors rounded-lg"
              >
                Close
              </button>
              <button
                onClick={() => onComplete(storyResult)}
                className="px-6 py-2 bg-[#007acc] text-white hover:bg-[#005a9e] transition-colors rounded-lg"
              >
                View Full Results
              </button>
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
              <span className="text-2xl">🔍</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Live Analysis</h2>
              <p className="text-[#888888]">Analyzing your clips in real-time</p>
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
          {/* Current Status */}
          <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-3">Current Status</h3>
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-[#007acc]"></div>
              <span className="text-white">{currentStep}</span>
            </div>
          </div>

          {/* Progress Log */}
          <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-3">Analysis Progress</h3>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {progress.map((item, index) => (
                <div key={index} className="flex items-start space-x-3 text-sm">
                  <span className="text-lg">{getProgressIcon(item.data.type)}</span>
                  <div className="flex-1">
                    <p className={`${getProgressColor(item.data.type)} font-medium`}>
                      {item.data.message}
                    </p>
                    {item.data.clip_name && (
                      <p className="text-[#888888] text-xs mt-1">
                        {item.data.clip_name}
                        {item.data.quality_score && ` (Score: ${item.data.quality_score.toFixed(2)})`}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Start Analysis Button */}
          {!isAnalyzing && (
            <div className="flex justify-center">
              <button
                onClick={startAnalysis}
                disabled={!ws}
                className="px-8 py-3 bg-[#007acc] text-white hover:bg-[#005a9e] disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-lg font-medium"
              >
                {ws ? 'Start Live Analysis' : 'Connecting...'}
              </button>
            </div>
          )}

          {/* Connection Status */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${ws ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-[#888888]">
                {ws ? 'Connected to analysis server' : 'Disconnected'}
              </span>
            </div>
            <span className="text-[#888888]">
              {clips.length} clips to analyze
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
