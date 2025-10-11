"""
Visual Intelligence Module for ClipSense

Analyzes video content to find the most interesting moments, detect faces,
score visual quality, and provide content-aware cut recommendations.
"""

import cv2
import numpy as np
import os
import asyncio
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisualAnalysisResult:
    """Results from visual analysis of a video clip"""
    clip_path: str
    duration: float
    face_count: int
    face_confidence: float
    motion_score: float
    brightness_score: float
    contrast_score: float
    stability_score: float
    overall_quality: float
    best_moments: List[float]  # Timestamps of best moments
    analysis_duration: float

@dataclass
class MomentScore:
    """Score for a specific moment in time"""
    timestamp: float
    face_score: float
    motion_score: float
    quality_score: float
    combined_score: float

class VisualAnalyzer:
    """
    Advanced visual analysis for video content
    
    Features:
    - Face detection and counting
    - Motion analysis
    - Visual quality scoring (brightness, contrast, stability)
    - Best moment identification
    - Content-aware cut recommendations
    """
    
    def __init__(self):
        """Initialize the visual analyzer with OpenCV models"""
        self.face_cascade = None
        self._load_models()
        
    def _load_models(self):
        """Load OpenCV models for face detection"""
        try:
            # Load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                logger.warning("Failed to load face cascade, face detection disabled")
                self.face_cascade = None
            else:
                logger.info("✅ Face detection model loaded successfully")
                
        except Exception as e:
            logger.error(f"❌ Failed to load face detection model: {e}")
            self.face_cascade = None
    
    async def analyze_clip(self, video_path: str, sample_rate: float = 1.0) -> VisualAnalysisResult:
        """
        Analyze a video clip for visual content and quality
        
        Args:
            video_path: Path to video file
            sample_rate: How often to sample frames (1.0 = every second, 0.5 = every 0.5 seconds)
            
        Returns:
            VisualAnalysisResult with comprehensive analysis
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"🎬 Analyzing video: {Path(video_path).name}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            logger.info(f"📊 Video properties: {frame_count} frames, {fps:.2f} FPS, {duration:.2f}s")
            
            # Analyze frames
            frame_interval = max(1, int(fps * sample_rate))
            moments = []
            face_counts = []
            motion_scores = []
            brightness_scores = []
            contrast_scores = []
            stability_scores = []
            
            prev_frame = None
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Sample frames at specified rate
                if frame_idx % frame_interval == 0:
                    timestamp = frame_idx / fps
                    
                    # Analyze this frame
                    moment = await self._analyze_frame(frame, timestamp, prev_frame)
                    moments.append(moment)
                    
                    # Collect metrics
                    face_counts.append(moment.face_score)
                    motion_scores.append(moment.motion_score)
                    brightness_scores.append(moment.quality_score)
                    contrast_scores.append(self._calculate_contrast(frame))
                    stability_scores.append(self._calculate_stability(frame, prev_frame))
                
                prev_frame = frame.copy() if frame_idx % frame_interval == 0 else prev_frame
                frame_idx += 1
            
            cap.release()
            
            # Calculate overall metrics
            face_count = int(np.mean(face_counts)) if face_counts else 0
            face_confidence = float(np.mean(face_counts)) if face_counts else 0.0
            motion_score = float(np.mean(motion_scores)) if motion_scores else 0.0
            brightness_score = float(np.mean(brightness_scores)) if brightness_scores else 0.0
            contrast_score = float(np.mean(contrast_scores)) if contrast_scores else 0.0
            stability_score = float(np.mean(stability_scores)) if stability_scores else 0.0
            
            # Calculate overall quality (weighted combination)
            overall_quality = self._calculate_overall_quality(
                face_confidence, motion_score, brightness_score, 
                contrast_score, stability_score
            )
            
            # Find best moments
            best_moments = self._find_best_moments(moments, duration)
            
            analysis_duration = asyncio.get_event_loop().time() - start_time
            
            result = VisualAnalysisResult(
                clip_path=video_path,
                duration=duration,
                face_count=face_count,
                face_confidence=face_confidence,
                motion_score=motion_score,
                brightness_score=brightness_score,
                contrast_score=contrast_score,
                stability_score=stability_score,
                overall_quality=overall_quality,
                best_moments=best_moments,
                analysis_duration=analysis_duration
            )
            
            logger.info(f"✅ Analysis complete: {face_count} faces, quality: {overall_quality:.2f}, {len(best_moments)} best moments")
            return result
            
        except Exception as e:
            logger.error(f"❌ Visual analysis failed: {e}")
            # Return minimal result on error
            return VisualAnalysisResult(
                clip_path=video_path,
                duration=0.0,
                face_count=0,
                face_confidence=0.0,
                motion_score=0.0,
                brightness_score=0.0,
                contrast_score=0.0,
                stability_score=0.0,
                overall_quality=0.0,
                best_moments=[],
                analysis_duration=asyncio.get_event_loop().time() - start_time
            )
    
    async def _analyze_frame(self, frame: np.ndarray, timestamp: float, prev_frame: Optional[np.ndarray]) -> MomentScore:
        """Analyze a single frame for visual content"""
        
        # Face detection
        face_score = self._detect_faces(frame)
        
        # Motion analysis
        motion_score = self._calculate_motion(frame, prev_frame)
        
        # Quality analysis
        quality_score = self._calculate_brightness(frame)
        
        # Combined score
        combined_score = (face_score * 0.4 + motion_score * 0.3 + quality_score * 0.3)
        
        return MomentScore(
            timestamp=timestamp,
            face_score=face_score,
            motion_score=motion_score,
            quality_score=quality_score,
            combined_score=combined_score
        )
    
    def _detect_faces(self, frame: np.ndarray) -> float:
        """Detect faces in frame and return confidence score"""
        if self.face_cascade is None:
            return 0.0
        
        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Return normalized face count (0-1 scale)
            face_count = len(faces)
            return min(1.0, face_count / 5.0)  # Cap at 5 faces for normalization
            
        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
            return 0.0
    
    def _calculate_motion(self, frame: np.ndarray, prev_frame: Optional[np.ndarray]) -> float:
        """Calculate motion score between frames"""
        if prev_frame is None:
            return 0.0
        
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate absolute difference
            diff = cv2.absdiff(gray1, gray2)
            
            # Calculate mean difference (motion intensity)
            motion_intensity = np.mean(diff) / 255.0
            
            # Normalize to 0-1 scale
            return min(1.0, motion_intensity * 10)  # Scale factor for normalization
            
        except Exception as e:
            logger.warning(f"Motion calculation failed: {e}")
            return 0.0
    
    def _calculate_brightness(self, frame: np.ndarray) -> float:
        """Calculate brightness score (0-1, where 0.5 is ideal)"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate mean brightness
            brightness = np.mean(gray) / 255.0
            
            # Score based on distance from ideal brightness (0.5)
            # Peak at 0.5, decreases as we move away
            ideal_brightness = 0.5
            distance_from_ideal = abs(brightness - ideal_brightness)
            brightness_score = max(0.0, 1.0 - distance_from_ideal * 2)
            
            return brightness_score
            
        except Exception as e:
            logger.warning(f"Brightness calculation failed: {e}")
            return 0.0
    
    def _calculate_contrast(self, frame: np.ndarray) -> float:
        """Calculate contrast score"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate standard deviation as contrast measure
            contrast = np.std(gray) / 255.0
            
            # Normalize to 0-1 scale (higher contrast is better)
            return min(1.0, contrast * 4)  # Scale factor for normalization
            
        except Exception as e:
            logger.warning(f"Contrast calculation failed: {e}")
            return 0.0
    
    def _calculate_stability(self, frame: np.ndarray, prev_frame: Optional[np.ndarray]) -> float:
        """Calculate stability score (inverse of motion)"""
        if prev_frame is None:
            return 1.0  # First frame is considered stable
        
        motion_score = self._calculate_motion(frame, prev_frame)
        stability_score = 1.0 - motion_score
        return max(0.0, stability_score)
    
    def _calculate_overall_quality(self, face_confidence: float, motion_score: float, 
                                 brightness_score: float, contrast_score: float, 
                                 stability_score: float) -> float:
        """Calculate overall quality score from individual metrics"""
        
        # Weighted combination of metrics
        weights = {
            'face': 0.3,      # Faces are important for highlights
            'motion': 0.2,    # Some motion is good, too much is bad
            'brightness': 0.2, # Good lighting is important
            'contrast': 0.15,  # Good contrast helps
            'stability': 0.15  # Stability is good
        }
        
        # Normalize motion score (some motion is good, too much is bad)
        optimal_motion = 0.3  # Sweet spot for motion
        motion_penalty = abs(motion_score - optimal_motion)
        normalized_motion = max(0.0, 1.0 - motion_penalty * 2)
        
        overall_quality = (
            face_confidence * weights['face'] +
            normalized_motion * weights['motion'] +
            brightness_score * weights['brightness'] +
            contrast_score * weights['contrast'] +
            stability_score * weights['stability']
        )
        
        return min(1.0, max(0.0, overall_quality))
    
    def _find_best_moments(self, moments: List[MomentScore], duration: float, 
                          max_moments: int = 10) -> List[float]:
        """Find the best moments in the video based on combined scores"""
        
        if not moments:
            return []
        
        # Sort by combined score (descending)
        sorted_moments = sorted(moments, key=lambda x: x.combined_score, reverse=True)
        
        # Take top moments, ensuring they're spread out
        best_moments = []
        min_interval = duration * 0.1  # Minimum 10% of duration between moments
        
        for moment in sorted_moments:
            # Check if this moment is far enough from existing ones
            too_close = any(abs(moment.timestamp - existing) < min_interval 
                          for existing in best_moments)
            
            if not too_close:
                best_moments.append(moment.timestamp)
                
            if len(best_moments) >= max_moments:
                break
        
        # Sort by timestamp
        best_moments.sort()
        
        return best_moments
    
    async def find_best_moments_in_duration(self, video_path: str, start_time: float, 
                                          duration: float) -> List[float]:
        """
        Find the best moments within a specific time range
        
        Args:
            video_path: Path to video file
            start_time: Start time in seconds
            duration: Duration to analyze in seconds
            
        Returns:
            List of timestamps for best moments within the range
        """
        try:
            # Analyze the specific segment
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            start_frame = int(start_time * fps)
            end_frame = int((start_time + duration) * fps)
            
            # Seek to start time
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            moments = []
            prev_frame = None
            frame_idx = start_frame
            
            while frame_idx < end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
                
                timestamp = frame_idx / fps
                moment = await self._analyze_frame(frame, timestamp, prev_frame)
                moments.append(moment)
                
                prev_frame = frame.copy()
                frame_idx += 1
            
            cap.release()
            
            # Find best moments within this range
            best_moments = self._find_best_moments(moments, duration, max_moments=5)
            
            # Adjust timestamps to be relative to start_time
            adjusted_moments = [start_time + moment for moment in best_moments]
            
            return adjusted_moments
            
        except Exception as e:
            logger.error(f"Failed to find best moments in duration: {e}")
            return []

# Example usage and testing
async def test_visual_analyzer():
    """Test the visual analyzer with a sample video"""
    analyzer = VisualAnalyzer()
    
    # Test with a sample video (replace with actual path)
    video_path = "tests/media/clip1.mp4"
    
    if os.path.exists(video_path):
        result = await analyzer.analyze_clip(video_path)
        print(f"Analysis Results:")
        print(f"  Duration: {result.duration:.2f}s")
        print(f"  Face Count: {result.face_count}")
        print(f"  Overall Quality: {result.overall_quality:.2f}")
        print(f"  Best Moments: {result.best_moments}")
        print(f"  Analysis Time: {result.analysis_duration:.2f}s")
    else:
        print(f"Test video not found: {video_path}")

if __name__ == "__main__":
    asyncio.run(test_visual_analyzer())
