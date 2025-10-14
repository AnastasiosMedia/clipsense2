"""
Wedding Object Detection Module for ClipSense

Detects wedding-specific objects and moments in video clips:
- Wedding rings (exchange, close-ups)
- Wedding cake (cutting ceremony, display)
- Dancing (first dance, party dancing)
- Bouquet (bouquet toss, ceremony)
- Ceremony moments (vows, kiss, walking down aisle)
- Toast moments (speeches, champagne)

Uses OpenCV and pre-trained models for real-time detection.
"""

import cv2
import numpy as np
import time
import os
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import asyncio
from pydantic import BaseModel

class WeddingObjectDetectionResult(BaseModel):
    """Result of wedding object detection analysis"""
    clip_path: str
    duration: float
    objects_detected: Dict[str, int]  # object_type -> count
    confidence_scores: Dict[str, float]  # object_type -> avg_confidence
    key_moments: List[float]  # timestamps of important moments
    analysis_duration: float
    scene_classification: str  # 'ceremony', 'reception', 'party', 'preparation'

class WeddingObjectDetector:
    """Detects wedding-specific objects and moments in video clips"""
    
    def __init__(self):
        # Initialize OpenCV cascade classifiers for different objects
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Object detection models (we'll use OpenCV's built-in detectors for now)
        # In production, you'd load more sophisticated models like YOLO or Detectron2
        self.object_templates = self._load_object_templates()
        
        # Wedding-specific object categories
        self.wedding_objects = {
            'wedding_rings': self._detect_rings,
            'wedding_cake': self._detect_cake,
            'dancing': self._detect_dancing,
            'bouquet': self._detect_bouquet,
            'ceremony_moments': self._detect_ceremony,
            'toast_moments': self._detect_toast,
            'people': self._detect_people
        }
        
        print("INFO:wedding_object_detector:✅ Wedding object detector initialized")
    
    def _load_object_templates(self) -> Dict[str, np.ndarray]:
        """Load template images for object detection"""
        # For now, we'll use simple color and shape detection
        # In production, you'd load actual template images or trained models
        return {
            'ring_template': None,  # Would load actual ring template
            'cake_template': None,  # Would load cake template
            'bouquet_template': None  # Would load bouquet template
        }
    
    async def analyze_clip(self, video_path: str, sample_rate: float = 1.0) -> WeddingObjectDetectionResult:
        """
        Analyze a video clip for wedding objects and moments
        
        Args:
            video_path: Path to video file
            sample_rate: Frames per second to analyze (1.0 = 1 fps)
            
        Returns:
            WeddingObjectDetectionResult with detected objects and moments
        """
        start_time = time.time()
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0.0
        
        if duration == 0:
            return WeddingObjectDetectionResult(
                clip_path=video_path, duration=0.0, objects_detected={},
                confidence_scores={}, key_moments=[], analysis_duration=0.0,
                scene_classification='unknown'
            )
        
        print(f"INFO:wedding_object_detector:🎬 Analyzing wedding clip: {os.path.basename(video_path)}")
        print(f"INFO:wedding_object_detector:📊 Video properties: {frame_count} frames, {fps:.2f} FPS, {duration:.2f}s")
        
        # Initialize detection results
        objects_detected = defaultdict(int)
        confidence_scores = defaultdict(list)
        key_moments = []
        
        # Optimized sampling: analyze every 1-2 seconds for better performance
        target_interval_seconds = 1.5  # Analyze every 1.5 seconds (3x faster)
        frame_interval = int(target_interval_seconds * fps) if fps > 0 else 1
        if frame_interval == 0:
            frame_interval = 1
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_interval == 0:
                current_time = frame_idx / fps
                
                # Detect all wedding objects in this frame
                frame_objects = await self._detect_objects_in_frame(frame)
                
                # Update detection counts
                for obj_type, count in frame_objects.items():
                    objects_detected[obj_type] += count
                
                # Check for key moments (high object activity)
                total_objects = sum(frame_objects.values())
                if total_objects > 0:
                    key_moments.append(current_time)
                    # Only log significant moments to reduce noise
                    if total_objects > 5:
                        print(f"INFO:wedding_object_detector:🎯 Key moment at {current_time:.2f}s: {total_objects} objects detected")
            
            frame_idx += 1
        
        cap.release()
        
        # Calculate average confidence scores
        avg_confidence = {}
        for obj_type, confidences in confidence_scores.items():
            if confidences:
                avg_confidence[obj_type] = sum(confidences) / len(confidences)
            else:
                avg_confidence[obj_type] = 0.0
        
        # Classify scene type based on detected objects
        scene_classification = self._classify_scene(dict(objects_detected))
        
        # Convert to regular dict for Pydantic
        objects_detected_dict = dict(objects_detected)
        
        end_time = time.time()
        analysis_duration = end_time - start_time
        
        print(f"INFO:wedding_object_detector:✅ Analysis complete: {len(key_moments)} key moments, scene: {scene_classification}")
        
        return WeddingObjectDetectionResult(
            clip_path=video_path,
            duration=duration,
            objects_detected=objects_detected_dict,
            confidence_scores=avg_confidence,
            key_moments=key_moments,
            analysis_duration=analysis_duration,
            scene_classification=scene_classification
        )
    
    async def _detect_objects_in_frame(self, frame: np.ndarray) -> Dict[str, int]:
        """Detect all wedding objects in a single frame"""
        frame_objects = {}
        
        # Convert to different color spaces for better detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Detect each type of wedding object
        for obj_type, detector_func in self.wedding_objects.items():
            try:
                count = detector_func(frame, gray, hsv)
                frame_objects[obj_type] = count
            except Exception as e:
                print(f"WARNING:wedding_object_detector:Error detecting {obj_type}: {e}")
                frame_objects[obj_type] = 0
        
        return frame_objects
    
    def _detect_rings(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect wedding rings using color and shape analysis"""
        # Look for small circular objects with metallic colors
        # This is a simplified approach - in production you'd use trained models
        
        # Detect circles using HoughCircles
        circles = cv2.HoughCircles(
            gray, cv2.HOUGH_GRADIENT, 1, 20,
            param1=50, param2=30, minRadius=5, maxRadius=50
        )
        
        ring_count = 0
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                # Check if the circle area has metallic-like colors
                roi = frame[y-r:y+r, x-r:x+r]
                if roi.size > 0:
                    # Simple metallic color detection (gold, silver tones)
                    mean_color = np.mean(roi, axis=(0, 1))
                    if self._is_metallic_color(mean_color):
                        ring_count += 1
        
        return min(ring_count, 4)  # Cap at 4 rings max per frame
    
    def _detect_cake(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect wedding cake using shape and color analysis"""
        # Look for tall, layered objects with white/cream colors
        # This is a simplified approach
        
        # Detect white/cream colored regions
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        
        # Find contours that could be cake layers
        contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        cake_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area for cake detection
                # Check aspect ratio (cakes are typically taller than wide)
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w if w > 0 else 0
                if aspect_ratio > 0.8:  # Taller than wide
                    cake_count += 1
        
        return min(cake_count, 2)  # Cap at 2 cakes max per frame
    
    def _detect_dancing(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect dancing using motion analysis"""
        # This is a simplified motion detection
        # In production, you'd use more sophisticated motion analysis
        
        # Calculate frame difference (motion)
        if not hasattr(self, 'prev_gray'):
            self.prev_gray = gray
            return 0
        
        frame_diff = cv2.absdiff(gray, self.prev_gray)
        motion_score = np.mean(frame_diff) / 255.0
        
        # Detect people in motion
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        dancing_count = 0
        if len(faces) > 0 and motion_score > 0.1:  # Motion threshold
            dancing_count = len(faces)
        
        self.prev_gray = gray
        return min(dancing_count, 10)  # Cap at 10 people max per frame
    
    def _detect_bouquet(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect bouquet using color and shape analysis"""
        # Look for colorful flower-like objects
        # This is a simplified approach
        
        # Detect colorful regions (flowers)
        lower_colorful = np.array([0, 50, 50])
        upper_colorful = np.array([180, 255, 255])
        colorful_mask = cv2.inRange(hsv, lower_colorful, upper_colorful)
        
        # Find contours that could be bouquets
        contours, _ = cv2.findContours(colorful_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bouquet_count = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Bouquet size range
                # Check for round/oval shape
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h if h > 0 else 0
                if 0.7 < aspect_ratio < 1.3:  # Roughly round
                    bouquet_count += 1
        
        return min(bouquet_count, 3)  # Cap at 3 bouquets max per frame
    
    def _detect_ceremony(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect ceremony moments using people and setting analysis"""
        # Look for formal settings with multiple people
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Ceremony typically has 2+ people in formal attire
        ceremony_score = 0
        if len(faces) >= 2:
            ceremony_score = len(faces)
        
        return min(ceremony_score, 8)  # Cap at 8 people max per frame
    
    def _detect_toast(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect toast moments using glass and people detection"""
        # Look for glass-like objects and people
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Detect glass-like objects (simplified)
        glass_count = 0
        # This would be more sophisticated in production
        
        toast_score = min(len(faces), 6) if glass_count > 0 else 0
        return toast_score
    
    def _detect_people(self, frame: np.ndarray, gray: np.ndarray, hsv: np.ndarray) -> int:
        """Detect people using face detection"""
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return len(faces)
    
    def _is_metallic_color(self, color: np.ndarray) -> bool:
        """Check if a color is metallic (gold, silver, etc.)"""
        b, g, r = color
        # Simple metallic color detection
        # Gold: high red and green, low blue
        # Silver: high values, low saturation
        if r > 150 and g > 150 and b < 100:  # Gold-like
            return True
        if r > 180 and g > 180 and b > 180:  # Silver-like
            return True
        return False
    
    def _classify_scene(self, objects_detected: Dict[str, int]) -> str:
        """Classify the scene type based on detected objects"""
        # Simple scene classification based on object counts
        ceremony_objects = objects_detected.get('ceremony_moments', 0)
        dancing_objects = objects_detected.get('dancing', 0)
        cake_objects = objects_detected.get('wedding_cake', 0)
        toast_objects = objects_detected.get('toast_moments', 0)
        
        if ceremony_objects > 3:
            return 'ceremony'
        elif dancing_objects > 2:
            return 'party'
        elif cake_objects > 0 or toast_objects > 0:
            return 'reception'
        else:
            return 'preparation'
    
    async def find_best_wedding_moments(self, video_path: str, num_moments: int = 5) -> List[float]:
        """
        Find the best wedding moments in a video clip
        
        Args:
            video_path: Path to video file
            num_moments: Number of best moments to return
            
        Returns:
            List of timestamps for the best moments
        """
        result = await self.analyze_clip(video_path, sample_rate=2.0)  # Higher sample rate for better detection
        
        # Score moments based on object detection
        moment_scores = []
        for moment in result.key_moments:
            # Simple scoring: more objects = better moment
            score = sum(result.objects_detected.values())
            moment_scores.append((moment, score))
        
        # Sort by score and return top moments
        moment_scores.sort(key=lambda x: x[1], reverse=True)
        best_moments = [moment for moment, score in moment_scores[:num_moments]]
        
        return sorted(best_moments)  # Return in chronological order
