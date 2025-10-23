"""
AI Story Narrative Generator for ClipSense

Creates intelligent, flowing narratives from video clip descriptions:
- Analyzes clip descriptions to understand content
- Builds coherent story arcs with proper narrative flow
- Generates story-aware clip selection and ordering
- Creates compelling narrative structures for wedding highlights

This is the core of ClipSense's AI storybuilding capabilities.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from pydantic import BaseModel
from collections import defaultdict
import json

try:
    from .openai_vision import OpenAIVisionClient
except ImportError:
    from openai_vision import OpenAIVisionClient

class ClipDescription(BaseModel):
    """Description of a video clip for story analysis"""
    clip_path: str
    description: str
    scene_type: str  # 'preparation', 'ceremony', 'reception', 'party', etc.
    emotional_tone: str  # 'romantic', 'joyful', 'dramatic', etc.
    key_moments: List[str]  # List of key moments detected
    people_count: int
    quality_score: float
    timestamp: float  # When this clip occurs in the timeline

class StoryNarrative(BaseModel):
    """Complete story narrative structure"""
    story_title: str
    story_theme: str  # 'romantic', 'celebratory', 'intimate', 'adventurous'
    narrative_structure: str  # 'traditional', 'modern', 'cinematic', 'documentary'
    story_arc: List[Dict[str, Any]]  # Complete story structure
    selected_clips: List[ClipDescription]  # Clips selected for the story
    rejected_clips: List[Dict[str, Any]]  # Clips not selected with reasons
    narrative_flow: str  # Human-readable story flow description
    emotional_journey: List[str]  # Emotional progression through the story
    story_duration: float  # Total estimated duration
    story_notes: str  # Additional story context and recommendations

class AIStoryNarrativeGenerator:
    """Generates intelligent story narratives from clip descriptions"""
    
    def __init__(self):
        self.vision_client = OpenAIVisionClient()
        
        # Story templates for different narrative styles
        self.narrative_templates = {
            'traditional': {
                'structure': ['preparation', 'ceremony', 'reception', 'celebration'],
                'emotional_arc': ['anticipation', 'solemnity', 'joy', 'celebration'],
                'themes': ['love', 'commitment', 'family', 'celebration'],
                'pacing': 'moderate'
            },
            'modern': {
                'structure': ['getting_ready', 'first_look', 'ceremony', 'cocktail', 'dinner', 'dancing'],
                'emotional_arc': ['excitement', 'intimacy', 'solemnity', 'social', 'warmth', 'celebration'],
                'themes': ['authenticity', 'connection', 'celebration', 'community'],
                'pacing': 'dynamic'
            },
            'cinematic': {
                'structure': ['establishing', 'rising_action', 'climax', 'resolution', 'epilogue'],
                'emotional_arc': ['mystery', 'tension', 'climax', 'resolution', 'satisfaction'],
                'themes': ['journey', 'transformation', 'love', 'destiny'],
                'pacing': 'dramatic'
            },
            'documentary': {
                'structure': ['context', 'preparation', 'ceremony', 'reception', 'reflection'],
                'emotional_arc': ['context', 'anticipation', 'solemnity', 'joy', 'reflection'],
                'themes': ['story', 'tradition', 'community', 'memory'],
                'pacing': 'contemplative'
            }
        }
        
        # Scene classification patterns
        self.scene_patterns = {
            'preparation': {
                'keywords': ['getting ready', 'preparation', 'anticipation', 'excitement', 'nervous'],
                'emotions': ['anticipation', 'excitement', 'nervousness'],
                'objects': ['mirror', 'dress', 'suit', 'makeup', 'hair']
            },
            'ceremony': {
                'keywords': ['ceremony', 'vows', 'rings', 'kiss', 'altar', 'officiant'],
                'emotions': ['solemnity', 'love', 'commitment', 'emotion'],
                'objects': ['altar', 'rings', 'flowers', 'officiant']
            },
            'reception': {
                'keywords': ['reception', 'dinner', 'speeches', 'toasts', 'cake', 'celebration'],
                'emotions': ['joy', 'celebration', 'warmth', 'community'],
                'objects': ['cake', 'tables', 'guests', 'speeches']
            },
            'party': {
                'keywords': ['dancing', 'party', 'music', 'celebration', 'fun', 'dance floor'],
                'emotions': ['joy', 'celebration', 'excitement', 'energy'],
                'objects': ['dance floor', 'music', 'lights', 'guests']
            }
        }
        
        print("INFO:ai_story_narrative:✅ AI Story Narrative Generator initialized")
    
    async def generate_story_narrative(self, 
                                     clip_descriptions: List[ClipDescription],
                                     narrative_style: str = 'modern',
                                     target_duration: float = 60.0,
                                     progress_callback=None) -> StoryNarrative:
        """
        Generate a complete story narrative from clip descriptions
        
        Args:
            clip_descriptions: List of clip descriptions with content analysis
            narrative_style: Style of narrative ('traditional', 'modern', 'cinematic', 'documentary')
            target_duration: Target duration for the final story in seconds
            
        Returns:
            StoryNarrative with complete story structure
        """
        print(f"INFO:ai_story_narrative:🎬 Generating {narrative_style} story from {len(clip_descriptions)} clips")
        
        # Send initial progress
        if progress_callback:
            await progress_callback({
                "type": "analysis_started",
                "total_clips": len(clip_descriptions),
                "message": f"Starting analysis of {len(clip_descriptions)} clips..."
            })
        
        # Add delay to prevent rate limiting
        await asyncio.sleep(0.5)
        
        # Analyze clips and create story structure
        story_analysis = await self._analyze_clips_for_story(clip_descriptions)
        
        if progress_callback:
            await progress_callback({
                "type": "analysis_complete",
                "message": "Clip analysis completed, building story structure..."
            })
        
        # Build narrative structure
        narrative_structure = await self._build_narrative_structure(
            story_analysis, narrative_style, target_duration
        )
        
        if progress_callback:
            await progress_callback({
                "type": "structure_built",
                "message": "Story structure created, selecting clips..."
            })
        
        # Select and order clips for the story
        selected_clips, rejected_clips = await self._select_clips_for_story(
            clip_descriptions, narrative_structure, target_duration, progress_callback
        )
        
        if progress_callback:
            await progress_callback({
                "type": "clips_selected",
                "selected_count": len(selected_clips),
                "rejected_count": len(rejected_clips),
                "message": f"Selected {len(selected_clips)} clips for the story"
            })
        
        # Generate story flow and emotional journey
        story_flow = await self._generate_story_flow(selected_clips, narrative_style)
        emotional_journey = await self._generate_emotional_journey(selected_clips)
        
        if progress_callback:
            await progress_callback({
                "type": "story_generated",
                "message": "Story narrative completed!"
            })
        
        # Create final story narrative
        story_narrative = StoryNarrative(
            story_title=await self._generate_story_title(selected_clips, narrative_style),
            story_theme=await self._determine_story_theme(selected_clips),
            narrative_structure=narrative_style,
            story_arc=narrative_structure,
            selected_clips=selected_clips,
            rejected_clips=rejected_clips,
            narrative_flow=story_flow,
            emotional_journey=emotional_journey,
            story_duration=sum(clip.quality_score * 3.0 for clip in selected_clips),  # Estimate duration
            story_notes=await self._generate_story_notes(selected_clips, narrative_style)
        )
        
        print(f"INFO:ai_story_narrative:✅ Generated story: '{story_narrative.story_title}' ({len(selected_clips)} clips)")
        return story_narrative
    
    async def _analyze_clips_for_story(self, clip_descriptions: List[ClipDescription]) -> Dict[str, Any]:
        """Analyze clips to understand the overall story content"""
        analysis = {
            'total_clips': len(clip_descriptions),
            'scene_distribution': defaultdict(int),
            'emotional_themes': defaultdict(int),
            'key_moments': [],
            'people_presence': 0,
            'quality_distribution': []
        }
        
        for clip in clip_descriptions:
            # Scene distribution
            analysis['scene_distribution'][clip.scene_type] += 1
            
            # Emotional themes
            analysis['emotional_themes'][clip.emotional_tone] += 1
            
            # Key moments
            analysis['key_moments'].extend(clip.key_moments)
            
            # People presence
            analysis['people_presence'] += clip.people_count
            
            # Quality distribution
            analysis['quality_distribution'].append(clip.quality_score)
        
        # Calculate average quality
        analysis['average_quality'] = sum(analysis['quality_distribution']) / len(analysis['quality_distribution'])
        
        # Determine dominant themes
        analysis['dominant_scene'] = max(analysis['scene_distribution'].items(), key=lambda x: x[1])[0]
        analysis['dominant_emotion'] = max(analysis['emotional_themes'].items(), key=lambda x: x[1])[0]
        
        return analysis
    
    async def _build_narrative_structure(self, 
                                       story_analysis: Dict[str, Any],
                                       narrative_style: str,
                                       target_duration: float) -> List[Dict[str, Any]]:
        """Build the narrative structure for the story"""
        template = self.narrative_templates.get(narrative_style, self.narrative_templates['modern'])
        
        structure = []
        total_duration = 0.0
        
        for i, scene_type in enumerate(template['structure']):
            # Calculate duration for this scene
            scene_duration = target_duration * (1.0 / len(template['structure']))
            
            # Adjust based on scene importance
            if scene_type == 'ceremony':
                scene_duration *= 1.5  # Ceremony gets more time
            elif scene_type in ['preparation', 'getting_ready']:
                scene_duration *= 0.8  # Preparation gets less time
            
            structure.append({
                'scene_type': scene_type,
                'narrative_position': template['structure'][i],
                'emotional_tone': template['emotional_arc'][i],
                'target_duration': scene_duration,
                'description': self._get_scene_description(scene_type, narrative_style),
                'key_elements': self._get_scene_key_elements(scene_type)
            })
            
            total_duration += scene_duration
        
        return structure
    
    async def _select_clips_for_story(self, 
                                    clip_descriptions: List[ClipDescription],
                                    narrative_structure: List[Dict[str, Any]],
                                    target_duration: float,
                                    progress_callback=None) -> Tuple[List[ClipDescription], List[Dict[str, Any]]]:
        """Select and order clips to create the story, returning both selected and rejected clips with reasons"""
        selected_clips = []
        rejected_clips = []
        used_clips = set()
        
        # Sort clips by quality and relevance
        sorted_clips = sorted(clip_descriptions, key=lambda x: x.quality_score, reverse=True)
        
        print(f"INFO:ai_story_narrative:🎯 Selecting clips from {len(sorted_clips)} available clips")
        print(f"INFO:ai_story_narrative:📊 Target duration: {target_duration}s")
        
        for scene in narrative_structure:
            scene_type = scene['scene_type']
            scene_duration = scene['target_duration']
            
            print(f"INFO:ai_story_narrative:🎬 Looking for clips for scene: {scene_type} (target: {scene_duration}s)")
            
            if progress_callback:
                await progress_callback({
                    "type": "scene_processing",
                    "scene_type": scene_type,
                    "message": f"Looking for clips for {scene_type} scene..."
                })
            
            # Find best clips for this scene
            scene_clips = []
            current_duration = 0.0
            
            for clip in sorted_clips:
                if clip.clip_path in used_clips:
                    continue
                
                # Check if clip matches scene type
                if self._clip_matches_scene(clip, scene_type):
                    scene_clips.append(clip)
                    used_clips.add(clip.clip_path)
                    current_duration += 3.0  # Assume 3 seconds per clip
                    print(f"INFO:ai_story_narrative:✅ Selected {Path(clip.clip_path).name} for {scene_type} (score: {clip.quality_score:.2f})")
                    
                    if progress_callback:
                        await progress_callback({
                            "type": "clip_selected",
                            "clip_name": Path(clip.clip_path).name,
                            "scene_type": scene_type,
                            "quality_score": clip.quality_score,
                            "message": f"Selected {Path(clip.clip_path).name} for {scene_type}"
                        })
                    
                    if current_duration >= scene_duration:
                        break
                else:
                    # Add to rejected clips with reason
                    rejection_reason = f"Doesn't match scene type '{scene_type}' (clip is '{clip.scene_type}')"
                    rejected_clips.append({
                        'clip': clip,
                        'reason': rejection_reason,
                        'scene_attempted': scene_type
                    })
                    
                    if progress_callback:
                        await progress_callback({
                            "type": "clip_rejected",
                            "clip_name": Path(clip.clip_path).name,
                            "scene_type": scene_type,
                            "reason": rejection_reason,
                            "message": f"Rejected {Path(clip.clip_path).name} for {scene_type}: {rejection_reason}"
                        })
            
            selected_clips.extend(scene_clips)
        
        # If we don't have enough clips, add the best remaining ones
        remaining_clips = [clip for clip in sorted_clips if clip.clip_path not in used_clips]
        if len(selected_clips) < len(clip_descriptions) * 0.5:  # If we selected less than 50%
            print(f"INFO:ai_story_narrative:⚠️ Only selected {len(selected_clips)} clips, adding {min(8, len(remaining_clips))} more from remaining")
            for clip in remaining_clips[:8]:  # Add more clips
                selected_clips.append(clip)
                used_clips.add(clip.clip_path)
                print(f"INFO:ai_story_narrative:✅ Added remaining clip {Path(clip.clip_path).name} (score: {clip.quality_score:.2f})")
        
        # Add remaining clips to rejected list with reasons
        for clip in remaining_clips[8:]:  # Skip the ones we just added
            rejected_clips.append({
                'clip': clip,
                'reason': f"Not selected - quality score {clip.quality_score:.2f} was lower than selected clips",
                'scene_attempted': 'none'
            })
        
        print(f"INFO:ai_story_narrative:📊 Final selection: {len(selected_clips)} selected, {len(rejected_clips)} rejected")
        
        return selected_clips, rejected_clips
    
    def _clip_matches_scene(self, clip: ClipDescription, scene_type: str) -> bool:
        """Check if a clip matches a scene type - more flexible matching"""
        # Direct match
        if clip.scene_type == scene_type:
            return True
        
        # More flexible matching - allow clips that are close to the scene type
        scene_mappings = {
            'getting_ready': ['preparation', 'getting_ready'],
            'first_look': ['ceremony', 'preparation', 'getting_ready'],
            'ceremony': ['ceremony', 'first_look'],
            'cocktail': ['reception', 'party', 'ceremony'],
            'dinner': ['reception', 'party'],
            'dancing': ['party', 'reception', 'dancing']
        }
        
        # Check if clip scene type is in the allowed mappings for this scene
        allowed_scenes = scene_mappings.get(scene_type, [scene_type])
        if clip.scene_type in allowed_scenes:
            return True
        
        # Pattern matching with keywords
        scene_pattern = self.scene_patterns.get(scene_type, {})
        keywords = scene_pattern.get('keywords', [])
        
        # Check if clip description contains scene keywords
        description_lower = clip.description.lower()
        keyword_matches = sum(1 for keyword in keywords if keyword in description_lower)
        
        # If at least 2 keywords match, consider it a match
        if keyword_matches >= 2:
            return True
        
        # Check emotional tone match
        emotions = scene_pattern.get('emotions', [])
        if clip.emotional_tone in emotions:
            return True
        
        # For high-quality clips, be more lenient
        if clip.quality_score > 0.7:
            return True
        
        return False
    
    async def _generate_story_flow(self, selected_clips: List[ClipDescription], narrative_style: str) -> str:
        """Generate human-readable story flow description"""
        if not selected_clips:
            return "No clips selected for story"
        
        # Group clips by scene type
        scene_groups = defaultdict(list)
        for clip in selected_clips:
            scene_groups[clip.scene_type].append(clip)
        
        # Generate flow description
        flow_parts = []
        
        for scene_type, clips in scene_groups.items():
            scene_description = self._get_scene_description(scene_type, narrative_style)
            flow_parts.append(f"{scene_description} ({len(clips)} clips)")
        
        return " → ".join(flow_parts)
    
    async def _generate_emotional_journey(self, selected_clips: List[ClipDescription]) -> List[str]:
        """Generate the emotional journey through the story"""
        emotional_journey = []
        
        for clip in selected_clips:
            emotional_journey.append(f"{clip.emotional_tone}: {clip.description[:50]}...")
        
        return emotional_journey
    
    async def _generate_story_title(self, selected_clips: List[ClipDescription], narrative_style: str) -> str:
        """Generate a compelling story title"""
        if not selected_clips:
            return "Wedding Story"
        
        # Analyze the clips to determine themes
        themes = []
        for clip in selected_clips:
            if 'love' in clip.description.lower() or 'romantic' in clip.description.lower():
                themes.append('Love')
            elif 'celebration' in clip.description.lower() or 'party' in clip.description.lower():
                themes.append('Celebration')
            elif 'ceremony' in clip.description.lower() or 'vows' in clip.description.lower():
                themes.append('Commitment')
        
        # Generate title based on themes
        if 'Love' in themes and 'Celebration' in themes:
            return "A Love Story Celebrated"
        elif 'Love' in themes:
            return "A Love Story"
        elif 'Celebration' in themes:
            return "A Celebration of Love"
        else:
            return "Wedding Highlights"
    
    async def _determine_story_theme(self, selected_clips: List[ClipDescription]) -> str:
        """Determine the overall story theme"""
        if not selected_clips:
            return 'romantic'
        
        # Analyze emotional tones
        emotional_counts = defaultdict(int)
        for clip in selected_clips:
            emotional_counts[clip.emotional_tone] += 1
        
        dominant_emotion = max(emotional_counts.items(), key=lambda x: x[1])[0]
        
        # Map emotions to themes
        emotion_to_theme = {
            'romantic': 'romantic',
            'joyful': 'celebratory',
            'intimate': 'intimate',
            'dramatic': 'cinematic',
            'celebratory': 'celebratory'
        }
        
        return emotion_to_theme.get(dominant_emotion, 'romantic')
    
    async def _generate_story_notes(self, selected_clips: List[ClipDescription], narrative_style: str) -> str:
        """Generate additional story context and recommendations"""
        notes = []
        
        # Story structure notes
        notes.append(f"Created a {narrative_style} narrative with {len(selected_clips)} carefully selected clips")
        
        # Quality notes
        avg_quality = sum(clip.quality_score for clip in selected_clips) / len(selected_clips)
        notes.append(f"Average clip quality: {avg_quality:.1f}/10")
        
        # Scene distribution notes
        scene_counts = defaultdict(int)
        for clip in selected_clips:
            scene_counts[clip.scene_type] += 1
        
        for scene, count in scene_counts.items():
            notes.append(f"{scene.title()}: {count} clips")
        
        # Emotional journey notes
        emotional_tones = [clip.emotional_tone for clip in selected_clips]
        unique_tones = set(emotional_tones)
        notes.append(f"Emotional range: {', '.join(unique_tones)}")
        
        return "; ".join(notes)
    
    def _get_scene_description(self, scene_type: str, narrative_style: str) -> str:
        """Get description for a scene type"""
        descriptions = {
            'preparation': 'Getting Ready',
            'getting_ready': 'Getting Ready',
            'first_look': 'First Look',
            'ceremony': 'The Ceremony',
            'reception': 'Reception',
            'cocktail': 'Cocktail Hour',
            'dinner': 'Dinner',
            'party': 'Celebration',
            'dancing': 'Dancing',
            'intimate_moments': 'Intimate Moments',
            'scenic_moments': 'Scenic Beauty'
        }
        return descriptions.get(scene_type, scene_type.title())
    
    def _get_scene_key_elements(self, scene_type: str) -> List[str]:
        """Get key elements for a scene type"""
        elements = {
            'preparation': ['anticipation', 'excitement', 'getting ready'],
            'ceremony': ['vows', 'rings', 'kiss', 'commitment'],
            'reception': ['celebration', 'speeches', 'toasts', 'cake'],
            'party': ['dancing', 'music', 'celebration', 'joy']
        }
        return elements.get(scene_type, [])
    
    async def enhance_with_ai_analysis(self, clip_descriptions: List[ClipDescription]) -> List[ClipDescription]:
        """Enhance clip descriptions with AI analysis"""
        enhanced_clips = []
        
        for i, clip in enumerate(clip_descriptions):
            # Add delay between API calls to prevent rate limiting
            if i > 0:
                await asyncio.sleep(1.0)  # 1 second delay between calls
            
            # Use OpenAI Vision to enhance description if available
            try:
                if hasattr(self.vision_client, 'analyze_image'):
                    # This would analyze a thumbnail of the video
                    enhanced_description = await self._enhance_description_with_ai(clip)
                    clip.description = enhanced_description
            except Exception as e:
                print(f"WARNING:ai_story_narrative:Failed to enhance description: {e}")
            
            enhanced_clips.append(clip)
        
        return enhanced_clips
    
    async def _enhance_description_with_ai(self, clip: ClipDescription) -> str:
        """Enhance clip description using AI analysis"""
        # This would use OpenAI Vision to analyze video thumbnails
        # For now, return the original description
        return clip.description
