"""
Style Presets Module for ClipSense

Implements different editing styles for wedding highlights:
- Romantic: Soft, warm, emotional
- Energetic: Fast-paced, vibrant, celebratory
- Cinematic: Film-like, dramatic, professional
- Documentary: Natural, authentic, storytelling

Each preset includes color grading, transitions, timing, and focus preferences.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
try:
    from .story_arc_creator import StoryArcResult
except ImportError:
    from story_arc_creator import StoryArcResult

class StylePresetConfig(BaseModel):
    """Configuration for a style preset"""
    name: str
    color_grade: str
    transition_style: str
    music_tempo: str
    clip_duration_preference: str
    focus_priority: str
    transition_duration: float
    color_saturation: float
    color_warmth: float
    contrast_level: float
    brightness_offset: float

class StylePresetResult(BaseModel):
    """Result of applying a style preset"""
    clip_path: str
    applied_style: str
    color_grade_applied: str
    transition_style_applied: str
    recommended_duration: float
    style_notes: str

class StylePresetEngine:
    """Applies different editing styles to wedding highlights"""
    
    def __init__(self):
        # Define style presets
        self.presets = {
            'romantic': StylePresetConfig(
                name='Romantic',
                color_grade='warm_tones',
                transition_style='soft_crossfade',
                music_tempo='slow_to_medium',
                clip_duration_preference='longer',
                focus_priority='emotional_moments',
                transition_duration=0.8,
                color_saturation=1.1,
                color_warmth=1.2,
                contrast_level=0.9,
                brightness_offset=0.1
            ),
            'energetic': StylePresetConfig(
                name='Energetic',
                color_grade='vibrant',
                transition_style='quick_cuts',
                music_tempo='fast',
                clip_duration_preference='shorter',
                focus_priority='action_moments',
                transition_duration=0.2,
                color_saturation=1.3,
                color_warmth=1.0,
                contrast_level=1.1,
                brightness_offset=0.0
            ),
            'cinematic': StylePresetConfig(
                name='Cinematic',
                color_grade='film_look',
                transition_style='cinematic_wipes',
                music_tempo='dramatic',
                clip_duration_preference='varied',
                focus_priority='story_beats',
                transition_duration=1.2,
                color_saturation=0.9,
                color_warmth=1.1,
                contrast_level=1.2,
                brightness_offset=-0.1
            ),
            'documentary': StylePresetConfig(
                name='Documentary',
                color_grade='natural',
                transition_style='fade',
                music_tempo='moderate',
                clip_duration_preference='medium',
                focus_priority='authentic_moments',
                transition_duration=0.5,
                color_saturation=1.0,
                color_warmth=1.0,
                contrast_level=1.0,
                brightness_offset=0.0
            )
        }
        
        # Color grading definitions
        self.color_grades = {
            'warm_tones': {
                'description': 'Warm, golden tones perfect for romantic moments',
                'ffmpeg_filter': 'colorbalance=rs=0.1:gs=0.05:bs=-0.1:rm=0.1:gm=0.05:bm=-0.1',
                'saturation': 1.1,
                'warmth': 1.2
            },
            'vibrant': {
                'description': 'Bright, saturated colors for energetic moments',
                'ffmpeg_filter': 'eq=saturation=1.3:contrast=1.1',
                'saturation': 1.3,
                'warmth': 1.0
            },
            'film_look': {
                'description': 'Cinematic film look with enhanced contrast',
                'ffmpeg_filter': 'colorbalance=rs=0.05:gs=0.02:bs=-0.05:rm=0.05:gm=0.02:bm=-0.05,eq=contrast=1.2',
                'saturation': 0.9,
                'warmth': 1.1
            },
            'natural': {
                'description': 'Natural colors with minimal processing',
                'ffmpeg_filter': 'eq=saturation=1.0:contrast=1.0',
                'saturation': 1.0,
                'warmth': 1.0
            }
        }
        
        # Transition styles
        self.transition_styles = {
            'soft_crossfade': {
                'description': 'Soft crossfade between clips',
                'ffmpeg_filter': 'xfade=transition=fade:duration=0.8:offset=0',
                'duration': 0.8
            },
            'quick_cuts': {
                'description': 'Quick cuts with minimal transition',
                'ffmpeg_filter': 'xfade=transition=wipeleft:duration=0.2:offset=0',
                'duration': 0.2
            },
            'cinematic_wipes': {
                'description': 'Cinematic wipe transitions',
                'ffmpeg_filter': 'xfade=transition=wiperight:duration=1.2:offset=0',
                'duration': 1.2
            },
            'fade': {
                'description': 'Simple fade transitions',
                'ffmpeg_filter': 'xfade=transition=fade:duration=0.5:offset=0',
                'duration': 0.5
            }
        }
        
        print("INFO:style_presets:✅ Style preset engine initialized")
    
    async def apply_style_preset(self, 
                               story_arc: StoryArcResult,
                               preset_name: str) -> StylePresetResult:
        """
        Apply a style preset to a story arc
        
        Args:
            story_arc: Story arc information for the clip
            preset_name: Name of the style preset to apply
            
        Returns:
            StylePresetResult with applied style information
        """
        if preset_name not in self.presets:
            raise ValueError(f"Unknown style preset: {preset_name}")
        
        preset = self.presets[preset_name]
        
        # Adjust recommended duration based on style
        adjusted_duration = self._adjust_duration_for_style(
            story_arc.recommended_duration, preset
        )
        
        # Select appropriate color grade
        color_grade = self._select_color_grade(story_arc, preset)
        
        # Select appropriate transition style
        transition_style = self._select_transition_style(story_arc, preset)
        
        # Generate style notes
        style_notes = self._generate_style_notes(story_arc, preset, color_grade, transition_style)
        
        return StylePresetResult(
            clip_path=story_arc.clip_path,
            applied_style=preset_name,
            color_grade_applied=color_grade,
            transition_style_applied=transition_style,
            recommended_duration=adjusted_duration,
            style_notes=style_notes
        )
    
    def _adjust_duration_for_style(self, base_duration: float, preset: StylePresetConfig) -> float:
        """Adjust clip duration based on style preferences"""
        duration_multipliers = {
            'longer': 1.3,
            'shorter': 0.7,
            'varied': 1.0,
            'medium': 1.0
        }
        
        multiplier = duration_multipliers.get(preset.clip_duration_preference, 1.0)
        adjusted_duration = base_duration * multiplier
        
        # Clamp between 1.0 and 10.0 seconds
        return max(1.0, min(10.0, adjusted_duration))
    
    def _select_color_grade(self, story_arc: StoryArcResult, preset: StylePresetConfig) -> str:
        """Select appropriate color grade based on story arc and preset"""
        # Base color grade from preset
        base_grade = preset.color_grade
        
        # Adjust based on emotional tone
        tone_adjustments = {
            'romantic': 'warm_tones',
            'joyful': 'vibrant',
            'dramatic': 'film_look',
            'intimate': 'warm_tones',
            'celebratory': 'vibrant'
        }
        
        # Override if emotional tone suggests different grade
        if story_arc.emotional_tone in tone_adjustments:
            suggested_grade = tone_adjustments[story_arc.emotional_tone]
            if preset.name in ['Romantic', 'Cinematic']:  # These presets can be overridden
                return suggested_grade
        
        return base_grade
    
    def _select_transition_style(self, story_arc: StoryArcResult, preset: StylePresetConfig) -> str:
        """Select appropriate transition style based on story arc and preset"""
        # Base transition style from preset
        base_style = preset.transition_style
        
        # Adjust based on narrative position
        position_adjustments = {
            'opening': 'fade',
            'rising_action': 'soft_crossfade',
            'climax': 'cinematic_wipes',
            'falling_action': 'soft_crossfade',
            'resolution': 'fade'
        }
        
        # Override if narrative position suggests different style
        if story_arc.narrative_position in position_adjustments:
            suggested_style = position_adjustments[story_arc.narrative_position]
            if preset.name in ['Cinematic', 'Documentary']:  # These presets can be overridden
                return suggested_style
        
        return base_style
    
    def _generate_style_notes(self, 
                            story_arc: StoryArcResult,
                            preset: StylePresetConfig,
                            color_grade: str,
                            transition_style: str) -> str:
        """Generate human-readable style notes"""
        notes = []
        
        # Style description
        notes.append(f"Applied {preset.name} style")
        
        # Color grade description
        color_info = self.color_grades.get(color_grade, {})
        if color_info:
            notes.append(f"Color: {color_info['description']}")
        
        # Transition description
        transition_info = self.transition_styles.get(transition_style, {})
        if transition_info:
            notes.append(f"Transitions: {transition_info['description']}")
        
        # Focus priority
        focus_descriptions = {
            'emotional_moments': 'Focus on emotional and romantic moments',
            'action_moments': 'Focus on dynamic and energetic moments',
            'story_beats': 'Focus on key story moments and narrative flow',
            'authentic_moments': 'Focus on natural and authentic moments'
        }
        
        focus_desc = focus_descriptions.get(preset.focus_priority, 'Standard focus')
        notes.append(focus_desc)
        
        # Duration preference
        duration_descriptions = {
            'longer': 'Longer clips for emotional impact',
            'shorter': 'Shorter clips for fast-paced editing',
            'varied': 'Varied clip lengths for dynamic pacing',
            'medium': 'Medium-length clips for balanced pacing'
        }
        
        duration_desc = duration_descriptions.get(preset.clip_duration_preference, 'Standard duration')
        notes.append(duration_desc)
        
        return '; '.join(notes)
    
    def get_ffmpeg_color_filter(self, color_grade: str) -> str:
        """Get FFmpeg filter string for color grading"""
        color_info = self.color_grades.get(color_grade, {})
        return color_info.get('ffmpeg_filter', 'eq=saturation=1.0:contrast=1.0')
    
    def get_ffmpeg_transition_filter(self, transition_style: str) -> str:
        """Get FFmpeg filter string for transitions"""
        transition_info = self.transition_styles.get(transition_style, {})
        return transition_info.get('ffmpeg_filter', 'xfade=transition=fade:duration=0.5:offset=0')
    
    def get_preset_summary(self, preset_name: str) -> Dict[str, Any]:
        """Get a summary of a style preset"""
        if preset_name not in self.presets:
            return {}
        
        preset = self.presets[preset_name]
        color_info = self.color_grades.get(preset.color_grade, {})
        transition_info = self.transition_styles.get(preset.transition_style, {})
        
        return {
            'name': preset.name,
            'description': f"{preset.name} style for wedding highlights",
            'color_grade': {
                'name': preset.color_grade,
                'description': color_info.get('description', ''),
                'saturation': preset.color_saturation,
                'warmth': preset.color_warmth
            },
            'transitions': {
                'name': preset.transition_style,
                'description': transition_info.get('description', ''),
                'duration': preset.transition_duration
            },
            'timing': {
                'music_tempo': preset.music_tempo,
                'clip_duration': preset.clip_duration_preference
            },
            'focus': preset.focus_priority,
            'technical': {
                'contrast': preset.contrast_level,
                'brightness': preset.brightness_offset
            }
        }
    
    def list_available_presets(self) -> List[str]:
        """List all available style presets"""
        return list(self.presets.keys())
    
    def get_preset_recommendations(self, story_arc: StoryArcResult) -> List[Tuple[str, float]]:
        """
        Get style preset recommendations based on story arc
        
        Returns:
            List of (preset_name, confidence_score) tuples sorted by confidence
        """
        recommendations = []
        
        for preset_name, preset in self.presets.items():
            score = 0.0
            
            # Score based on emotional tone
            tone_scores = {
                'romantic': {'romantic': 0.9, 'cinematic': 0.7, 'documentary': 0.5, 'energetic': 0.2},
                'joyful': {'energetic': 0.9, 'documentary': 0.6, 'romantic': 0.4, 'cinematic': 0.5},
                'dramatic': {'cinematic': 0.9, 'romantic': 0.6, 'documentary': 0.4, 'energetic': 0.3},
                'intimate': {'romantic': 0.9, 'documentary': 0.7, 'cinematic': 0.5, 'energetic': 0.1},
                'celebratory': {'energetic': 0.9, 'documentary': 0.6, 'romantic': 0.4, 'cinematic': 0.5}
            }
            
            tone_scores_for_tone = tone_scores.get(story_arc.emotional_tone, {})
            score += tone_scores_for_tone.get(preset_name, 0.0) * 0.4
            
            # Score based on scene classification
            scene_scores = {
                'preparation': {'documentary': 0.8, 'romantic': 0.6, 'cinematic': 0.5, 'energetic': 0.3},
                'ceremony': {'cinematic': 0.9, 'romantic': 0.8, 'documentary': 0.6, 'energetic': 0.2},
                'reception': {'documentary': 0.7, 'energetic': 0.6, 'romantic': 0.5, 'cinematic': 0.4},
                'party': {'energetic': 0.9, 'documentary': 0.6, 'cinematic': 0.5, 'romantic': 0.3},
                'intimate_moments': {'romantic': 0.9, 'documentary': 0.7, 'cinematic': 0.6, 'energetic': 0.1},
                'scenic_moments': {'cinematic': 0.8, 'documentary': 0.7, 'romantic': 0.5, 'energetic': 0.2}
            }
            
            scene_scores_for_scene = scene_scores.get(story_arc.scene_classification, {})
            score += scene_scores_for_scene.get(preset_name, 0.0) * 0.3
            
            # Score based on story importance
            if story_arc.story_importance > 0.7:
                # High importance clips work well with cinematic style
                if preset_name == 'cinematic':
                    score += 0.2
            elif story_arc.story_importance < 0.3:
                # Low importance clips work well with documentary style
                if preset_name == 'documentary':
                    score += 0.2
            
            recommendations.append((preset_name, score))
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations
