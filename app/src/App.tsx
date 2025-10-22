import { useState, useEffect } from 'react';
import { FilePicker } from './components/FilePicker';
import { ProcessingStatus } from './components/ProcessingStatus';
import { ResultDisplay } from './components/ResultDisplay';
import { ToastContainer, ToastData } from './components/ToastContainer';
import { ApiService } from './services/api';
import StoryboardPreview from './components/StoryboardPreview';
import { FileSelection, ProcessingState } from './types';
import { invoke } from '@tauri-apps/api/tauri';
import config from './config';

function App() {
  const [fileSelection, setFileSelection] = useState<FileSelection>({
    clips: [],
    music: null
  });
  
  const [processingState, setProcessingState] = useState<ProcessingState>({
    isProcessing: false,
    progress: 0,
    currentStep: '',
    error: null
  });
  
  const [outputPath, setOutputPath] = useState<string | null>(null);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [toasts, setToasts] = useState<ToastData[]>([]);
  const [processingMetrics, setProcessingMetrics] = useState<{
    proxy_time?: number;
    render_time?: number;
    total_time?: number;
    selected_clips?: any[];
    story_breakdown?: any;
    quality_metrics?: any;
  }>({});
  const [showPreview, setShowPreview] = useState(false);

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const addToast = (message: string, type: 'success' | 'error' | 'warning' | 'info', duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type, duration }]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const checkBackendConnection = async () => {
    try {
      // First try ping for quick connection test
      await ApiService.ping();
      
      // Then get detailed health info
      const health = await ApiService.healthCheck();
      
      if (health.ffmpeg_available) {
        setBackendStatus('connected');
        addToast('Backend connected and FFmpeg ready!', 'success');
      } else {
        setBackendStatus('error');
        addToast('Backend connected but FFmpeg not found', 'error', 10000);
      }
      
      if (config.get('enableDebugLogs')) {
        console.log('Backend health:', health);
      }
    } catch (error) {
      setBackendStatus('error');
      console.error('Backend connection failed:', error);
      addToast('Cannot connect to backend. Make sure the worker is running.', 'error', 10000);
    }
  };

  const handleAutoCut = async () => {
    if (fileSelection.clips.length === 0 || !fileSelection.music) {
      const errorMsg = 'Please select at least one video clip and one music track';
      setProcessingState(prev => ({
        ...prev,
        error: errorMsg
      }));
      addToast(errorMsg, 'warning');
      return;
    }

    if (backendStatus !== 'connected') {
      addToast('Backend not ready. Please wait for connection.', 'error');
      return;
    }

    setProcessingState({
      isProcessing: true,
      progress: 0,
      currentStep: 'Starting processing...',
      error: null
    });

    setOutputPath(null);
    setProcessingMetrics({});
    addToast('Starting video processing...', 'info');

    let progressInterval: ReturnType<typeof setInterval> | undefined;
    try {
      // Simulate progress updates
      progressInterval = setInterval(() => {
        setProcessingState(prev => {
          const newProgress = Math.min(prev.progress + 10, 90);
          let step = '';
          
          if (newProgress < 30) step = 'Creating video proxies...';
          else if (newProgress < 60) step = 'Trimming segments...';
          else if (newProgress < 80) step = 'Concatenating clips...';
          else step = 'Overlaying music and finalizing...';
          
          return {
            ...prev,
            progress: newProgress,
            currentStep: step
          };
        });
      }, 1000);

      const response = await ApiService.autoCut({
        clips: fileSelection.clips,
        music: fileSelection.music,
        target_seconds: 60,
        use_ai_selection: false  // Use regular processing for now
      });

      if (progressInterval) clearInterval(progressInterval);

      if (response.ok && response.output) {
        setProcessingState({
          isProcessing: false,
          progress: 100,
          currentStep: 'Complete!',
          error: null
        });
        setOutputPath(response.output);
        setProcessingMetrics({
          proxy_time: response.proxy_time,
          render_time: response.render_time,
          total_time: response.total_time
        });
        addToast('Video processing completed successfully!', 'success');
      } else {
        const errorMsg = response.error || 'Unknown error occurred';
        setProcessingState({
          isProcessing: false,
          progress: 0,
          currentStep: '',
          error: errorMsg
        });
        addToast(`Processing failed: ${errorMsg}`, 'error', 10000);
      }
    } catch (error) {
      if (progressInterval) clearInterval(progressInterval);
      const errorMsg = error instanceof Error ? error.message : 'Processing failed';
      setProcessingState({
        isProcessing: false,
        progress: 0,
        currentStep: '',
        error: errorMsg
      });
      addToast(`Processing failed: ${errorMsg}`, 'error', 10000);
    }
  };

  const handleOpenFile = async (path: string) => {
    try {
      // Use Tauri's shell API to open the file location
      await invoke('shell_open', { path });
    } catch (error) {
      console.error('Failed to open file location:', error);
      // Fallback: copy path to clipboard or show in alert
      navigator.clipboard.writeText(path);
      alert(`File saved to: ${path}`);
    }
  };

  const canProcess = fileSelection.clips.length > 0 && 
                    fileSelection.music && 
                    !processingState.isProcessing &&
                    backendStatus === 'connected';

  return (
    <div className="min-h-screen bg-[#1e1e1e] p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">ClipSense</h1>
          <p className="text-gray-400">Create highlight videos with music overlay</p>
          
          {/* Backend Status */}
          <div className="mt-4">
            {backendStatus === 'checking' && (
              <div className="inline-flex items-center space-x-2 text-yellow-400">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-400"></div>
                <span className="text-sm">Checking backend...</span>
              </div>
            )}
            {backendStatus === 'connected' && (
              <div className="inline-flex items-center space-x-2 text-green-400">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Backend connected</span>
              </div>
            )}
            {backendStatus === 'error' && (
              <div className="inline-flex items-center space-x-2 text-red-400">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">Backend not available</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* File Selection */}
          <div>
            <FilePicker
              fileSelection={fileSelection}
              onFileSelectionChange={setFileSelection}
              disabled={processingState.isProcessing}
            />
          </div>

          {/* Processing Controls */}
          <div className="space-y-6">
            {/* Auto-Cut Button */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-3">Generate Highlight</h3>
              <button
                onClick={handleAutoCut}
                disabled={!canProcess}
                className="btn-primary w-full text-lg py-3"
              >
                {processingState.isProcessing ? 'Processing...' : 'Auto-Cut'}
              </button>
              <p className="text-sm text-gray-400 mt-2">
                Creates a 60-second highlight video with music overlay
              </p>
              <button
                onClick={() => setShowPreview(true)}
                disabled={!canProcess}
                className="btn-secondary w-full text-lg py-3 mt-3"
              >
                Preview Storyboard
              </button>
            </div>

            {/* Processing Status */}
            <ProcessingStatus processingState={processingState} />

            {/* Result Display */}
            <ResultDisplay 
              outputPath={outputPath} 
              onOpenFile={handleOpenFile}
              metrics={processingMetrics}
            />
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 card">
          <h3 className="text-lg font-semibold mb-3">How to use</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-gray-300">
            <li>Click "Pick Clips" to select multiple video files</li>
            <li>Click "Pick Music" to select one audio file</li>
            <li>Click "Auto-Cut" to generate your highlight video</li>
            <li>Wait for processing to complete (usually 1-2 minutes)</li>
            <li>Click "Open File Location" to view your result</li>
          </ol>
        </div>
      </div>
      
      {/* Preview Modal */}
      {showPreview && (
        <StoryboardPreview
          fileSelection={fileSelection}
          qualitySettings={{}}
          onClose={() => setShowPreview(false)}
          onGenerate={async (request) => {
            console.log('Generated with request:', request);
            setShowPreview(false);
            
            // Start AI processing
            setProcessingState({
              isProcessing: true,
              progress: 0,
              currentStep: 'Starting AI processing...',
              error: null
            });

            setOutputPath(null);
            setProcessingMetrics({});
            addToast('Starting AI-powered video processing...', 'info');

            let progressInterval: ReturnType<typeof setInterval> | undefined;
            try {
              // Simulate progress updates
              progressInterval = setInterval(() => {
                setProcessingState(prev => {
                  const newProgress = Math.min(prev.progress + 8, 90);
                  let step = '';
                  if (newProgress < 30) step = 'Analyzing content with AI...';
                  else if (newProgress < 60) step = 'Selecting best clips...';
                  else if (newProgress < 90) step = 'Generating storyboard...';
                  else step = 'Finalizing output...';
                  
                  return {
                    ...prev,
                    progress: newProgress,
                    currentStep: step
                  };
                });
              }, 1000);

              const response = await ApiService.aiAutoCut({
                clips: request.clips,
                music_path: request.music,
                target_duration: request.target_seconds,
                story_style: request.story_style || 'traditional',
                style_preset: request.style_preset || 'balanced',
                use_ai_selection: request.use_ai_selection === true
              });

              if (progressInterval) clearInterval(progressInterval);

              if (response.ok && response.proxy_output) {
                setProcessingState({
                  isProcessing: false,
                  progress: 100,
                  currentStep: 'Complete!',
                  error: null
                });
                setOutputPath(response.proxy_output);
                setProcessingMetrics({
                  proxy_time: response.proxy_time,
                  render_time: response.render_time,
                  total_time: response.total_time,
                  selected_clips: response.selected_clips,
                  story_breakdown: response.story_breakdown,
                  quality_metrics: response.quality_metrics
                });
                addToast('AI-powered video processing completed successfully!', 'success');
              } else {
                const errorMsg = response.error || 'Unknown error occurred';
                setProcessingState({
                  isProcessing: false,
                  progress: 0,
                  currentStep: '',
                  error: errorMsg
                });
                addToast(`AI processing failed: ${errorMsg}`, 'error', 10000);
              }
            } catch (error) {
              if (progressInterval) clearInterval(progressInterval);
              const errorMsg = error instanceof Error ? error.message : 'AI processing failed';
              setProcessingState({
                isProcessing: false,
                progress: 0,
                currentStep: '',
                error: errorMsg
              });
              addToast(`AI processing failed: ${errorMsg}`, 'error', 10000);
            }
          }}
        />
      )}

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onRemoveToast={removeToast} />
    </div>
  );
}

export default App;
