"""
Story Arc Creation Module for ClipSense

Creates narrative flow for wedding highlights:
- Scene classification (preparation, ceremony, reception, party)
- Story structure templates
- Narrative flow optimization
- Emotional pacing

Uses object detection and emotion analysis to create compelling story arcs.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import asyncio
from pydantic import BaseModel
try:
    from .wedding_object_detector import WeddingObjectDetectionResult
except ImportError:
    from wedding_object_detector import WeddingObjectDetectionResult
try:
    from .emotion_analyzer import EmotionAnalysisResult
except ImportError:
    from emotion_analyzer import EmotionAnalysisResult

class StoryArcResult(BaseModel):
    """Result of story arc creation"""
    clip_path: str
    scene_classification: str
    story_importance: float  # 0.0 to 1.0
    narrative_position: str  # 'opening', 'rising_action', 'climax', 'falling_action', 'resolution'
    emotional_tone: str  # 'romantic', 'joyful', 'dramatic', 'intimate', 'celebratory'
    recommended_duration: float  # Suggested clip duration in seconds
    story_notes: str  # Human-readable story context

class StoryArcCreator:
    """Creates narrative story arcs for wedding highlights"""
    
    def __init__(self):
        # Story structure templates for different wedding styles
        self.story_templates = {
            'traditional': {
                'structure': ['preparation', 'ceremony', 'reception', 'party'],
                'weights': [0.15, 0.35, 0.30, 0.20],
                'emotional_arc': ['anticipation', 'solemnity', 'joy', 'celebration']
            },
            'modern': {
                'structure': ['getting_ready', 'first_look', 'ceremony', 'cocktail', 'dinner', 'dancing'],
                'weights': [0.10, 0.15, 0.25, 0.15, 0.20, 0.15],
                'emotional_arc': ['excitement', 'intimacy', 'solemnity', 'social', 'warmth', 'celebration']
            },
            'intimate': {
                'structure': ['preparation', 'ceremony', 'intimate_moments', 'celebration'],
                'weights': [0.20, 0.40, 0.25, 0.15],
                'emotional_arc': ['anticipation', 'solemnity', 'tenderness', 'joy']
            },
            'destination': {
                'structure': ['preparation', 'ceremony', 'scenic_moments', 'reception', 'party'],
                'weights': [0.15, 0.30, 0.20, 0.20, 0.15],
                'emotional_arc': ['anticipation', 'solemnity', 'wonder', 'joy', 'celebration']
            }
        }
        
        # Scene classification rules
        self.scene_classifiers = {
            'preparation': self._classify_preparation,
            'ceremony': self._classify_ceremony,
            'reception': self._classify_reception,
            'party': self._classify_party,
            'intimate_moments': self._classify_intimate,
            'scenic_moments': self._classify_scenic
        }
        
        # Emotional tone classifiers
        self.tone_classifiers = {
            'romantic': self._classify_romantic,
            'joyful': self._classify_joyful,
            'dramatic': self._classify_dramatic,
            'intimate': self._classify_intimate_tone,
            'celebratory': self._classify_celebratory
        }
        
        print("INFO:story_arc_creator:✅ Story arc creator initialized")
    
    async def create_story_arc(self, 
                             object_analysis: WeddingObjectDetectionResult,
                             emotion_analysis: EmotionAnalysisResult,
                             story_style: str = 'traditional') -> StoryArcResult:
        """
        Create a story arc for a video clip
        
        Args:
            object_analysis: Results from wedding object detection
            emotion_analysis: Results from emotion analysis
            story_style: Story template to use ('traditional', 'modern', 'intimate', 'destination')
            
        Returns:
            StoryArcResult with narrative information
        """
        # Determine scene classification
        scene_classification = self._determine_scene_classification(object_analysis, emotion_analysis)
        
        # Calculate story importance
        story_importance = self._calculate_story_importance(object_analysis, emotion_analysis)
        
        # Determine narrative position
        narrative_position = self._determine_narrative_position(scene_classification, story_style)
        
        # Determine emotional tone
        emotional_tone = self._determine_emotional_tone(emotion_analysis, scene_classification)
        
        # Calculate recommended duration
        recommended_duration = self._calculate_recommended_duration(
            scene_classification, story_importance, emotional_tone
        )
        
        # Generate story notes
        story_notes = self._generate_story_notes(
            scene_classification, emotional_tone, object_analysis, emotion_analysis
        )
        
        return StoryArcResult(
            clip_path=object_analysis.clip_path,
            scene_classification=scene_classification,
            story_importance=story_importance,
            narrative_position=narrative_position,
            emotional_tone=emotional_tone,
            recommended_duration=recommended_duration,
            story_notes=story_notes
        )
    
    def _determine_scene_classification(self, 
                                      object_analysis: WeddingObjectDetectionResult,
                                      emotion_analysis: EmotionAnalysisResult) -> str:
        """Determine the scene classification based on objects and emotions"""
        # Use object detection results
        objects = object_analysis.objects_detected
        scene_from_objects = object_analysis.scene_classification
        
        # Use emotion analysis to refine classification
        emotions = emotion_analysis.emotions
        excitement = emotion_analysis.excitement_level
        
        # Refine scene classification based on emotions
        if scene_from_objects == 'ceremony' and excitement > 0.7:
            return 'ceremony'  # High energy ceremony
        elif scene_from_objects == 'party' and emotions.get('tenderness', 0) > 0.5:
            return 'intimate_moments'  # Intimate party moments
        elif scene_from_objects == 'reception' and excitement > 0.8:
            return 'party'  # High energy reception
        elif emotions.get('love', 0) > 0.6 and excitement < 0.4:
            return 'intimate_moments'  # Romantic intimate moments
        else:
            return scene_from_objects
    
    def _calculate_story_importance(self, 
                                  object_analysis: WeddingObjectDetectionResult,
                                  emotion_analysis: EmotionAnalysisResult) -> float:
        """Calculate the story importance of this clip"""
        importance = 0.0
        
        # Object-based importance
        objects = object_analysis.objects_detected
        if objects.get('wedding_rings', 0) > 0:
            importance += 0.3  # Ring exchange is very important
        if objects.get('wedding_cake', 0) > 0:
            importance += 0.2  # Cake cutting is important
        if objects.get('ceremony_moments', 0) > 0:
            importance += 0.4  # Ceremony moments are crucial
        if objects.get('dancing', 0) > 0:
            importance += 0.1  # Dancing is nice but not crucial
        
        # Emotion-based importance
        emotions = emotion_analysis.emotions
        if emotions.get('joy', 0) > 0.7:
            importance += 0.2  # High joy is important
        if emotions.get('love', 0) > 0.6:
            importance += 0.3  # Love moments are very important
        if emotions.get('celebration', 0) > 0.7:
            importance += 0.1  # Celebration is good
        
        # Key moments importance
        if len(object_analysis.key_moments) > 2:
            importance += 0.1  # Multiple key moments
        
        return min(importance, 1.0)
    
    def _determine_narrative_position(self, scene_classification: str, story_style: str) -> str:
        """Determine the narrative position in the story arc"""
        template = self.story_templates.get(story_style, self.story_templates['traditional'])
        structure = template['structure']
        
        # Map scene to narrative position
        position_mapping = {
            'preparation': 'opening',
            'getting_ready': 'opening',
            'first_look': 'rising_action',
            'ceremony': 'climax',
            'reception': 'falling_action',
            'cocktail': 'falling_action',
            'dinner': 'falling_action',
            'party': 'resolution',
            'dancing': 'resolution',
            'intimate_moments': 'rising_action',
            'scenic_moments': 'rising_action'
        }
        
        return position_mapping.get(scene_classification, 'rising_action')
    
    def _determine_emotional_tone(self, 
                                emotion_analysis: EmotionAnalysisResult,
                                scene_classification: str) -> str:
        """Determine the emotional tone of the clip"""
        emotions = emotion_analysis.emotions
        excitement = emotion_analysis.excitement_level
        
        # Score each tone
        tone_scores = {}
        for tone, classifier in self.tone_classifiers.items():
            tone_scores[tone] = classifier(emotions, excitement, scene_classification)
        
        # Return the tone with highest score
        return max(tone_scores.items(), key=lambda x: x[1])[0]
    
    def _calculate_recommended_duration(self, 
                                      scene_classification: str,
                                      story_importance: float,
                                      emotional_tone: str) -> float:
        """Calculate recommended duration for this clip"""
        base_durations = {
            'preparation': 3.0,
            'ceremony': 5.0,  # Ceremony moments are longer
            'reception': 4.0,
            'party': 3.0,
            'intimate_moments': 4.0,  # Intimate moments are longer
            'scenic_moments': 3.0
        }
        
        base_duration = base_durations.get(scene_classification, 3.0)
        
        # Adjust based on story importance
        importance_multiplier = 0.5 + (story_importance * 0.5)  # 0.5 to 1.0
        duration = base_duration * importance_multiplier
        
        # Adjust based on emotional tone
        tone_multipliers = {
            'romantic': 1.2,
            'intimate': 1.3,
            'dramatic': 1.1,
            'joyful': 0.9,
            'celebratory': 0.8
        }
        
        tone_multiplier = tone_multipliers.get(emotional_tone, 1.0)
        duration *= tone_multiplier
        
        # Clamp between 1.0 and 8.0 seconds
        return max(1.0, min(8.0, duration))
    
    def _generate_story_notes(self, 
                            scene_classification: str,
                            emotional_tone: str,
                            object_analysis: WeddingObjectDetectionResult,
                            emotion_analysis: EmotionAnalysisResult) -> str:
        """Generate human-readable story notes"""
        notes = []
        
        # Scene context
        scene_descriptions = {
            'preparation': 'Getting ready moments with anticipation and excitement',
            'ceremony': 'The main ceremony with vows, ring exchange, and the kiss',
            'reception': 'Cocktail hour and dinner with speeches and toasts',
            'party': 'Dancing and celebration with high energy',
            'intimate_moments': 'Romantic and tender moments between the couple',
            'scenic_moments': 'Beautiful location shots and environmental beauty'
        }
        
        notes.append(scene_descriptions.get(scene_classification, 'Wedding moment'))
        
        # Object highlights
        objects = object_analysis.objects_detected
        if objects.get('wedding_rings', 0) > 0:
            notes.append('Features ring exchange - a key wedding moment')
        if objects.get('wedding_cake', 0) > 0:
            notes.append('Includes cake cutting ceremony')
        if objects.get('dancing', 0) > 0:
            notes.append('Shows dancing and celebration')
        if objects.get('people', 0) > 3:
            notes.append('Features multiple people - great for group shots')
        
        # Emotional highlights
        emotions = emotion_analysis.emotions
        if emotions.get('joy', 0) > 0.7:
            notes.append('High joy and happiness - perfect for highlight')
        if emotions.get('love', 0) > 0.6:
            notes.append('Romantic and loving moments')
        if emotions.get('celebration', 0) > 0.7:
            notes.append('Celebratory and festive atmosphere')
        
        # Key moments
        if len(object_analysis.key_moments) > 2:
            notes.append(f'Contains {len(object_analysis.key_moments)} key moments')
        
        return '; '.join(notes)
    
    # Scene classification methods
    def _classify_preparation(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as preparation scene"""
        score = 0.0
        if objects.get('people', 0) > 0 and excitement > 0.3:
            score += 0.5
        if emotions.get('joy', 0) > 0.4:
            score += 0.3
        return score
    
    def _classify_ceremony(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as ceremony scene"""
        score = 0.0
        if objects.get('ceremony_moments', 0) > 0:
            score += 0.8
        if objects.get('wedding_rings', 0) > 0:
            score += 0.6
        if excitement < 0.6:  # Ceremony is usually more solemn
            score += 0.2
        return score
    
    def _classify_reception(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as reception scene"""
        score = 0.0
        if objects.get('wedding_cake', 0) > 0:
            score += 0.7
        if objects.get('toast_moments', 0) > 0:
            score += 0.6
        if 0.4 < excitement < 0.8:  # Moderate excitement
            score += 0.3
        return score
    
    def _classify_party(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as party scene"""
        score = 0.0
        if objects.get('dancing', 0) > 0:
            score += 0.8
        if excitement > 0.7:
            score += 0.6
        if emotions.get('celebration', 0) > 0.6:
            score += 0.4
        return score
    
    def _classify_intimate(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as intimate moments"""
        score = 0.0
        if emotions.get('love', 0) > 0.6:
            score += 0.8
        if emotions.get('tenderness', 0) > 0.5:
            score += 0.6
        if excitement < 0.5:  # Intimate moments are usually calmer
            score += 0.3
        return score
    
    def _classify_scenic(self, objects: Dict[str, int], emotions: Dict[str, float], excitement: float) -> float:
        """Classify as scenic moments"""
        score = 0.0
        if objects.get('people', 0) < 3:  # Fewer people, more scenic
            score += 0.4
        if excitement < 0.4:  # Calmer, more scenic
            score += 0.3
        return score
    
    # Tone classification methods
    def _classify_romantic(self, emotions: Dict[str, float], excitement: float, scene: str) -> float:
        """Classify as romantic tone"""
        score = 0.0
        if emotions.get('love', 0) > 0.5:
            score += 0.6
        if emotions.get('tenderness', 0) > 0.4:
            score += 0.4
        if scene in ['ceremony', 'intimate_moments']:
            score += 0.3
        return score
    
    def _classify_joyful(self, emotions: Dict[str, float], excitement: float, scene: str) -> float:
        """Classify as joyful tone"""
        score = 0.0
        if emotions.get('joy', 0) > 0.6:
            score += 0.8
        if excitement > 0.5:
            score += 0.4
        if scene in ['party', 'reception']:
            score += 0.3
        return score
    
    def _classify_dramatic(self, emotions: Dict[str, float], excitement: float, scene: str) -> float:
        """Classify as dramatic tone"""
        score = 0.0
        if emotions.get('surprise', 0) > 0.5:
            score += 0.6
        if scene == 'ceremony':
            score += 0.4
        if excitement > 0.6:
            score += 0.3
        return score
    
    def _classify_intimate_tone(self, emotions: Dict[str, float], excitement: float, scene: str) -> float:
        """Classify as intimate tone"""
        score = 0.0
        if emotions.get('tenderness', 0) > 0.6:
            score += 0.8
        if emotions.get('love', 0) > 0.5:
            score += 0.6
        if excitement < 0.4:
            score += 0.4
        return score
    
    def _classify_celebratory(self, emotions: Dict[str, float], excitement: float, scene: str) -> float:
        """Classify as celebratory tone"""
        score = 0.0
        if emotions.get('celebration', 0) > 0.6:
            score += 0.8
        if excitement > 0.7:
            score += 0.6
        if scene in ['party', 'reception']:
            score += 0.4
        return score
    
    async def create_complete_story_arc(self, 
                                      clips_with_analysis: List[Tuple[WeddingObjectDetectionResult, EmotionAnalysisResult]],
                                      story_style: str = 'traditional') -> List[StoryArcResult]:
        """
        Create a complete story arc for multiple clips
        
        Args:
            clips_with_analysis: List of (object_analysis, emotion_analysis) tuples
            story_style: Story template to use
            
        Returns:
            List of StoryArcResult for each clip
        """
        story_arcs = []
        
        for object_analysis, emotion_analysis in clips_with_analysis:
            story_arc = await self.create_story_arc(object_analysis, emotion_analysis, story_style)
            story_arcs.append(story_arc)
        
        # Sort by story importance and narrative position
        story_arcs.sort(key=lambda x: (x.story_importance, x.narrative_position), reverse=True)
        
        return story_arcs
