import React, { useState, useRef, useEffect } from 'react';

interface VideoPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoPath: string;
  videoName?: string;
}

export const VideoPreviewModal: React.FC<VideoPreviewModalProps> = ({
  isOpen,
  onClose,
  videoPath,
  videoName = 'Highlight Video'
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [mouseTimeout, setMouseTimeout] = useState<NodeJS.Timeout | null>(null);
  const [showCover, setShowCover] = useState(true);
  const videoRef = useRef<HTMLVideoElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && videoRef.current) {
      const video = videoRef.current;
      
      // Reset states when modal opens
      setShowCover(true);
      setIsPlaying(false);
      
      // Show controls initially, then start auto-hide after a delay
      setShowControls(true);
      const initialTimeout = setTimeout(() => {
        setShowControls(false);
      }, 2000);
      
      const handleLoadedMetadata = () => {
        setDuration(video.duration);
        // Set to first frame and show cover after a small delay to ensure video is ready
        setTimeout(() => {
          if (video) {
            video.currentTime = 0;
            setShowCover(true);
          }
        }, 100);
      };

      const handleTimeUpdate = () => {
        setCurrentTime(video.currentTime);
      };

      const handlePlay = () => {
        setIsPlaying(true);
        setShowCover(false);
      };
      const handlePause = () => {
        setIsPlaying(false);
        setShowCover(true);
      };
      const handleEnded = () => {
        setIsPlaying(false);
        setShowCover(true);
      };
      const handleError = () => {
        setVideoError(true);
        console.error('Video failed to load:', videoPath);
      };

      const handleFullscreenChange = () => {
        setIsFullscreen(!!document.fullscreenElement);
      };

      video.addEventListener('loadedmetadata', handleLoadedMetadata);
      video.addEventListener('timeupdate', handleTimeUpdate);
      video.addEventListener('play', handlePlay);
      video.addEventListener('pause', handlePause);
      video.addEventListener('ended', handleEnded);
      video.addEventListener('error', handleError);
      document.addEventListener('fullscreenchange', handleFullscreenChange);

      return () => {
        clearTimeout(initialTimeout);
        video.removeEventListener('loadedmetadata', handleLoadedMetadata);
        video.removeEventListener('timeupdate', handleTimeUpdate);
        video.removeEventListener('play', handlePlay);
        video.removeEventListener('pause', handlePause);
        video.removeEventListener('ended', handleEnded);
        video.removeEventListener('error', handleError);
        document.removeEventListener('fullscreenchange', handleFullscreenChange);
      };
    }
  }, [isOpen]);

  // Auto-hide controls on mouse movement
  const handleMouseMove = () => {
    setShowControls(true);
    
    // Clear existing timeout
    if (mouseTimeout) {
      clearTimeout(mouseTimeout);
    }
    
    // Set new timeout to hide controls after 4 seconds
    const timeout = setTimeout(() => {
      setShowControls(false);
    }, 4000);
    
    setMouseTimeout(timeout);
  };

  const handleMouseLeave = () => {
    setShowControls(false);
    if (mouseTimeout) {
      clearTimeout(mouseTimeout);
    }
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (mouseTimeout) {
        clearTimeout(mouseTimeout);
      }
    };
  }, [mouseTimeout]);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setShowCover(true);
      } else {
        videoRef.current.play();
        setShowCover(false);
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (videoRef.current && progressRef.current) {
      const rect = progressRef.current.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const width = rect.width;
      const newTime = (clickX / width) * duration;
      videoRef.current.currentTime = newTime;
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const toggleFullscreen = async () => {
    const videoContainer = videoRef.current?.parentElement;
    if (!videoContainer) return;

    try {
      if (!document.fullscreenElement) {
        // Try different fullscreen methods for browser compatibility
        const requestFullscreen = videoContainer.requestFullscreen || 
                                (videoContainer as any).webkitRequestFullscreen || 
                                (videoContainer as any).mozRequestFullScreen || 
                                (videoContainer as any).msRequestFullscreen;
        
        if (requestFullscreen) {
          await requestFullscreen.call(videoContainer);
          setIsFullscreen(true);
        }
      } else {
        const exitFullscreen = document.exitFullscreen || 
                              (document as any).webkitExitFullscreen || 
                              (document as any).mozCancelFullScreen || 
                              (document as any).msExitFullscreen;
        
        if (exitFullscreen) {
          await exitFullscreen.call(document);
          setIsFullscreen(false);
        }
      }
    } catch (error) {
      console.error('Fullscreen toggle failed:', error);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Only close if clicking on the backdrop itself, not on child elements
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 transition-all duration-500 ease-in-out"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-6xl mx-4 transition-all duration-500 ease-in-out">

               {/* Video Container */}
               <div 
                 className="relative bg-[#0d0d0d] overflow-hidden"
                 onMouseMove={handleMouseMove}
                 onMouseLeave={handleMouseLeave}
                 onClick={(e) => e.stopPropagation()}
               >
          {/* Close Button - Top Right */}
          <button
            onClick={onClose}
            className={`absolute top-4 right-4 z-10 text-[#888888] hover:text-white p-2 transition-all duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Centered Play Button - Only when paused or not started */}
          {showCover && !videoError && (
            <button
              onClick={togglePlay}
              className="absolute inset-0 z-10 flex items-center justify-center bg-black/20 hover:bg-black/30 transition-all"
            >
              <div className="border-2 border-white/80 hover:border-white rounded-full p-6 transition-colors">
                <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </div>
            </button>
          )}

          {videoError ? (
            <div className="w-full h-96 flex flex-col items-center justify-center text-center p-8">
              <div className="text-6xl mb-4">🎬</div>
              <h3 className="text-xl font-semibold text-white mb-2">Video Preview Unavailable</h3>
              <p className="text-[#888888] mb-4">
                The video file cannot be loaded directly in the browser.
              </p>
              <p className="text-sm text-[#666666] mb-6">
                File: {videoPath.split('/').pop()}
              </p>
              <button
                onClick={() => window.open(videoPath, '_blank')}
                className="px-6 py-2 bg-[#007acc] text-white hover:bg-[#005a9e] transition-colors rounded"
              >
                Open in System Player
              </button>
            </div>
                 ) : (
                   <video
                     ref={videoRef}
                     src={videoPath.startsWith('http') ? videoPath : `http://127.0.0.1:8123/videos/${videoPath.split('/').pop()}`}
                     className="w-full h-auto max-h-[70vh]"
                     controls={false}
                     preload="metadata"
                     poster=""
                     onClick={togglePlay}
                   />
                 )}

                 {/* Custom Controls Overlay */}
                 {!videoError && (
                   <div 
                     className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-4 transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}
                     onClick={(e) => e.stopPropagation()}
                   >
            {/* Progress Bar - Flush against bottom */}
            <div
              ref={progressRef}
              className="w-full h-1 bg-[#333333] cursor-pointer mb-4"
              onClick={handleProgressClick}
            >
              <div
                className="h-full bg-[#007acc] transition-all duration-100"
                style={{ width: `${duration ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">

                {/* Time Display - Hidden */}
                <div className="text-white text-sm font-mono opacity-0">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </div>

              </div>

              <div className="flex items-center space-x-2">
                {/* Fullscreen Button */}
                <button
                  onClick={toggleFullscreen}
                  className="text-white hover:text-[#007acc] transition-colors"
                >
                  {isFullscreen ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
          )}
        </div>

      </div>
    </div>
  );
};
