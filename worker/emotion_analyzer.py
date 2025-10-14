"""
Emotion Analysis Module for ClipSense

Analyzes emotional content in video clips:
- Facial expression recognition
- Audio sentiment analysis
- Scene emotion classification
- Emotional moment detection

Uses OpenCV for facial analysis and audio processing for sentiment.
"""

import cv2
import numpy as np
import time
import os
import librosa
import soundfile as sf
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import asyncio
from pydantic import BaseModel

class EmotionAnalysisResult(BaseModel):
    """Result of emotion analysis"""
    clip_path: str
    duration: float
    emotions: Dict[str, float]  # emotion -> confidence score
    emotional_moments: List[Tuple[float, str, float]]  # (timestamp, emotion, confidence)
    overall_sentiment: str  # 'positive', 'negative', 'neutral'
    excitement_level: float  # 0.0 to 1.0
    analysis_duration: float

class EmotionAnalyzer:
    """Analyzes emotional content in video clips"""
    
    def __init__(self):
        # Load face cascade for facial expression analysis
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Emotion categories we'll detect
        self.emotion_categories = {
            'joy': self._detect_joy,
            'surprise': self._detect_surprise,
            'love': self._detect_love,
            'excitement': self._detect_excitement,
            'tenderness': self._detect_tenderness,
            'celebration': self._detect_celebration
        }
        
        # Audio analysis parameters
        self.sample_rate = 22050
        self.hop_length = 512
        
        print("INFO:emotion_analyzer:✅ Emotion analyzer initialized")
    
    async def analyze_clip(self, video_path: str, sample_rate: float = 2.0) -> EmotionAnalysisResult:
        """
        Analyze emotional content in a video clip
        
        Args:
            video_path: Path to video file
            sample_rate: Frames per second to analyze
            
        Returns:
            EmotionAnalysisResult with emotional analysis
        """
        start_time = time.time()
        
        # Extract video and audio
        video_emotions = await self._analyze_video_emotions(video_path, sample_rate)
        audio_emotions = await self._analyze_audio_emotions(video_path)
        
        # Combine video and audio analysis
        combined_emotions = self._combine_emotions(video_emotions, audio_emotions)
        
        # Determine overall sentiment
        overall_sentiment = self._determine_overall_sentiment(combined_emotions)
        
        # Calculate excitement level
        excitement_level = self._calculate_excitement_level(combined_emotions)
        
        # Find emotional moments
        emotional_moments = self._find_emotional_moments(video_emotions, audio_emotions)
        
        # Get video duration
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0.0
        cap.release()
        
        end_time = time.time()
        analysis_duration = end_time - start_time
        
        print(f"INFO:emotion_analyzer:✅ Emotion analysis complete: {overall_sentiment} sentiment, {len(emotional_moments)} emotional moments")
        
        return EmotionAnalysisResult(
            clip_path=video_path,
            duration=duration,
            emotions=combined_emotions,
            emotional_moments=emotional_moments,
            overall_sentiment=overall_sentiment,
            excitement_level=excitement_level,
            analysis_duration=analysis_duration
        )
    
    async def _analyze_video_emotions(self, video_path: str, sample_rate: float) -> Dict[str, List[Tuple[float, float]]]:
        """Analyze emotions from video frames"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        # Optimized sampling: analyze every 1-2 seconds for better performance
        target_interval_seconds = 1.5  # Analyze every 1.5 seconds (3x faster)
        frame_interval = int(target_interval_seconds * fps) if fps > 0 else 1
        if frame_interval == 0:
            frame_interval = 1
        
        emotions_over_time = defaultdict(list)
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_interval == 0:
                current_time = frame_idx / fps
                
                # Analyze emotions in this frame
                frame_emotions = self._analyze_frame_emotions(frame)
                
                for emotion, confidence in frame_emotions.items():
                    emotions_over_time[emotion].append((current_time, confidence))
            
            frame_idx += 1
        
        cap.release()
        return dict(emotions_over_time)
    
    def _analyze_frame_emotions(self, frame: np.ndarray) -> Dict[str, float]:
        """Analyze emotions in a single frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return {emotion: 0.0 for emotion in self.emotion_categories.keys()}
        
        # Analyze emotions for each face
        frame_emotions = defaultdict(list)
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            if face_roi.size > 0:
                face_emotions = self._analyze_face_emotions(face_roi)
                for emotion, confidence in face_emotions.items():
                    frame_emotions[emotion].append(confidence)
        
        # Average emotions across all faces
        avg_emotions = {}
        for emotion in self.emotion_categories.keys():
            if emotion in frame_emotions and frame_emotions[emotion]:
                avg_emotions[emotion] = sum(frame_emotions[emotion]) / len(frame_emotions[emotion])
            else:
                avg_emotions[emotion] = 0.0
        
        return avg_emotions
    
    def _analyze_face_emotions(self, face_roi: np.ndarray) -> Dict[str, float]:
        """Analyze emotions in a face region"""
        emotions = {}
        
        for emotion, detector_func in self.emotion_categories.items():
            try:
                confidence = detector_func(face_roi)
                emotions[emotion] = confidence
            except Exception as e:
                print(f"WARNING:emotion_analyzer:Error detecting {emotion}: {e}")
                emotions[emotion] = 0.0
        
        return emotions
    
    def _detect_joy(self, face_roi: np.ndarray) -> float:
        """Detect joy/smiles using mouth and eye analysis"""
        # Simple smile detection using mouth region
        h, w = face_roi.shape
        mouth_region = face_roi[int(h*0.6):h, int(w*0.2):int(w*0.8)]
        
        if mouth_region.size == 0:
            return 0.0
        
        # Look for upward curve in mouth (simplified)
        # In production, you'd use more sophisticated facial landmark detection
        mouth_edges = cv2.Canny(mouth_region, 50, 150)
        mouth_contours, _ = cv2.findContours(mouth_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        joy_score = 0.0
        for contour in mouth_contours:
            # Check if contour has upward curve (smile shape)
            if len(contour) > 5:
                # Simple curvature analysis
                moments = cv2.moments(contour)
                if moments['m00'] != 0:
                    cx = int(moments['m10'] / moments['m00'])
                    cy = int(moments['m01'] / moments['m00'])
                    
                    # Check if center is above the contour (upward curve)
                    if cy < mouth_region.shape[0] * 0.5:
                        joy_score += 0.3
        
        return min(joy_score, 1.0)
    
    def _detect_surprise(self, face_roi: np.ndarray) -> float:
        """Detect surprise using eye and mouth analysis"""
        h, w = face_roi.shape
        eye_region = face_roi[int(h*0.2):int(h*0.5), int(w*0.1):int(w*0.9)]
        
        if eye_region.size == 0:
            return 0.0
        
        # Look for wide eyes (simplified)
        eye_edges = cv2.Canny(eye_region, 50, 150)
        eye_contours, _ = cv2.findContours(eye_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        surprise_score = 0.0
        for contour in eye_contours:
            area = cv2.contourArea(contour)
            if area > 50:  # Minimum area for eye detection
                # Check aspect ratio (wide eyes)
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                if aspect_ratio > 1.5:  # Wide eyes
                    surprise_score += 0.4
        
        return min(surprise_score, 1.0)
    
    def _detect_love(self, face_roi: np.ndarray) -> float:
        """Detect love/tenderness using facial proximity and soft features"""
        # This is a simplified approach
        # In production, you'd use more sophisticated analysis
        
        # Look for soft, gentle features
        # This is a placeholder - real implementation would be more complex
        return 0.0  # Placeholder
    
    def _detect_excitement(self, face_roi: np.ndarray) -> float:
        """Detect excitement using facial energy and movement"""
        # Look for high energy facial features
        # This is a simplified approach
        
        # Calculate facial energy (brightness, contrast)
        energy = np.std(face_roi) / 255.0
        return min(energy, 1.0)
    
    def _detect_tenderness(self, face_roi: np.ndarray) -> float:
        """Detect tenderness using soft facial features"""
        # Look for gentle, soft features
        # This is a simplified approach
        
        # Calculate softness (low contrast, smooth gradients)
        laplacian = cv2.Laplacian(face_roi, cv2.CV_64F)
        softness = 1.0 - (np.std(laplacian) / 255.0)
        return max(0.0, softness)
    
    def _detect_celebration(self, face_roi: np.ndarray) -> float:
        """Detect celebration using high energy and joy combination"""
        joy_score = self._detect_joy(face_roi)
        excitement_score = self._detect_excitement(face_roi)
        
        # Celebration is combination of joy and excitement
        celebration_score = (joy_score + excitement_score) / 2.0
        return celebration_score
    
    async def _analyze_audio_emotions(self, video_path: str) -> Dict[str, float]:
        """Analyze emotions from audio track"""
        try:
            # Extract audio from video
            audio, sr = librosa.load(video_path, sr=self.sample_rate)
            
            # Check if audio is silent (no audio track or very quiet)
            if len(audio) == 0 or np.max(np.abs(audio)) < 0.001:
                print("INFO:emotion_analyzer:No audio track detected, using visual-only analysis")
                return {emotion: 0.0 for emotion in self.emotion_categories.keys()}
            
            # Analyze audio features
            audio_emotions = {}
            
            # Energy analysis
            energy = np.mean(librosa.feature.rms(y=audio)[0])
            audio_emotions['excitement'] = min(energy * 2, 1.0)
            
            # Spectral centroid (brightness)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr)[0])
            audio_emotions['joy'] = min(spectral_centroid / 3000, 1.0)  # Normalize
            
            # Zero crossing rate (speech vs music)
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio)[0])
            audio_emotions['celebration'] = min(zcr * 10, 1.0)  # Higher ZCR = more celebration
            
            # Tempo analysis
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
            audio_emotions['excitement'] = min(tempo / 200, 1.0)  # Higher tempo = more excitement
            
            return audio_emotions
            
        except Exception as e:
            print(f"INFO:emotion_analyzer:Audio analysis skipped (no audio track): {e}")
            return {emotion: 0.0 for emotion in self.emotion_categories.keys()}
    
    def _combine_emotions(self, video_emotions: Dict[str, List[Tuple[float, float]]], 
                         audio_emotions: Dict[str, float]) -> Dict[str, float]:
        """Combine video and audio emotion analysis"""
        combined = {}
        
        # Check if we have any audio data
        has_audio = any(score > 0.0 for score in audio_emotions.values())
        
        for emotion in self.emotion_categories.keys():
            # Get average video emotion
            video_scores = video_emotions.get(emotion, [])
            video_avg = sum(score for _, score in video_scores) / len(video_scores) if video_scores else 0.0
            
            # Get audio emotion
            audio_score = audio_emotions.get(emotion, 0.0)
            
            if has_audio:
                # Combine with weights (70% video, 30% audio)
                combined[emotion] = 0.7 * video_avg + 0.3 * audio_score
            else:
                # Use only video analysis if no audio
                combined[emotion] = video_avg
        
        return combined
    
    def _determine_overall_sentiment(self, emotions: Dict[str, float]) -> str:
        """Determine overall sentiment from emotion scores"""
        positive_emotions = emotions.get('joy', 0) + emotions.get('love', 0) + emotions.get('celebration', 0)
        negative_emotions = 0  # We're not detecting negative emotions in this implementation
        neutral_emotions = emotions.get('tenderness', 0)
        
        if positive_emotions > 0.5:
            return 'positive'
        elif negative_emotions > 0.5:
            return 'negative'
        else:
            return 'neutral'
    
    def _calculate_excitement_level(self, emotions: Dict[str, float]) -> float:
        """Calculate overall excitement level"""
        excitement = emotions.get('excitement', 0)
        celebration = emotions.get('celebration', 0)
        joy = emotions.get('joy', 0)
        
        # Weighted combination
        excitement_level = (excitement * 0.5 + celebration * 0.3 + joy * 0.2)
        return min(excitement_level, 1.0)
    
    def _find_emotional_moments(self, video_emotions: Dict[str, List[Tuple[float, float]]], 
                               audio_emotions: Dict[str, float]) -> List[Tuple[float, str, float]]:
        """Find the most emotional moments in the clip"""
        emotional_moments = []
        
        for emotion, moments in video_emotions.items():
            for timestamp, confidence in moments:
                if confidence > 0.3:  # Threshold for emotional moment
                    emotional_moments.append((timestamp, emotion, confidence))
        
        # Sort by confidence and return top moments
        emotional_moments.sort(key=lambda x: x[2], reverse=True)
        return emotional_moments[:10]  # Return top 10 emotional moments
    
    async def find_emotional_highlights(self, video_path: str, num_highlights: int = 5) -> List[float]:
        """
        Find the most emotional moments in a video clip
        
        Args:
            video_path: Path to video file
            num_highlights: Number of emotional highlights to return
            
        Returns:
            List of timestamps for the most emotional moments
        """
        result = await self.analyze_clip(video_path, sample_rate=2.0)
        
        # Extract timestamps from emotional moments
        highlights = [moment[0] for moment in result.emotional_moments[:num_highlights]]
        
        return sorted(highlights)  # Return in chronological order
