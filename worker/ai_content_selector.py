"""
AI-Powered Content Selection Module for ClipSense

Integrates all AI components for intelligent content selection:
- Object detection for wedding elements
- Emotion analysis for emotional moments
- Story arc creation for narrative flow
- Style presets for consistent editing

Creates truly intelligent, story-driven wedding highlights.
"""

import time
import asyncio
import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from pydantic import BaseModel

try:
    from .wedding_object_detector import WeddingObjectDetector, WeddingObjectDetectionResult
    from .emotion_analyzer import EmotionAnalyzer, EmotionAnalysisResult
    from .story_arc_creator import StoryArcCreator, StoryArcResult
    from .style_presets import StylePresetEngine, StylePresetResult
    from .openai_vision import OpenAIVisionClient
    from .ai_story_narrative import AIStoryNarrativeGenerator, ClipDescription, StoryNarrative
except ImportError:
    from wedding_object_detector import WeddingObjectDetector, WeddingObjectDetectionResult
    from emotion_analyzer import EmotionAnalyzer, EmotionAnalysisResult
    from story_arc_creator import StoryArcCreator, StoryArcResult
    from style_presets import StylePresetEngine, StylePresetResult
    from openai_vision import OpenAIVisionClient
    from ai_story_narrative import AIStoryNarrativeGenerator, ClipDescription, StoryNarrative

class AIContentSelectionResult(BaseModel):
    """Result of AI-powered content selection"""
    clip_path: str
    object_analysis: WeddingObjectDetectionResult
    emotion_analysis: EmotionAnalysisResult
    story_arc: StoryArcResult
    style_preset: StylePresetResult
    final_score: float  # Overall quality score for this clip
    selection_reason: str  # Human-readable reason for selection
    description: str  # 1-2 sentence description of the clip content

class AIContentSelector:
    """Main AI-powered content selection system"""
    
    def __init__(self):
        self.object_detector = WeddingObjectDetector()
        self.emotion_analyzer = EmotionAnalyzer()
        self.story_creator = StoryArcCreator()
        self.style_engine = StylePresetEngine()
        self.vision = OpenAIVisionClient()
        self.story_narrative = AIStoryNarrativeGenerator()
        
        # Simple cache to avoid re-analyzing the same clips
        self._analysis_cache = {}
        
        # Clear cache on startup to ensure fresh analysis
        print("INFO:ai_content_selector:🧹 Cleared analysis cache for fresh analysis")
        
        print("INFO:ai_content_selector:✅ AI Content Selector initialized")
    
    def clear_cache(self):
        """Clear the analysis cache to force fresh analysis"""
        self._analysis_cache.clear()
        print("INFO:ai_content_selector:🧹 Analysis cache cleared")
    
    async def analyze_clip(self, 
                          video_path: str,
                          story_style: str = 'traditional',
                          style_preset: str = 'romantic') -> AIContentSelectionResult:
        """
        Perform complete AI analysis on a single clip with caching
        
        Args:
            video_path: Path to video file
            story_style: Story template ('traditional', 'modern', 'intimate', 'destination')
            style_preset: Style preset ('romantic', 'energetic', 'cinematic', 'documentary')
            
        Returns:
            AIContentSelectionResult with complete analysis
        """
        # Check cache first (but only for non-object detection parts)
        cache_key = f"{video_path}_{story_style}_{style_preset}_v2"
        # Note: We don't cache object detection as it should be real-time
        
        print(f"INFO:ai_content_selector:🎬 Analyzing clip: {Path(video_path).name}")
        
        # Run base analyses in parallel for efficiency
        object_task = self.object_detector.analyze_clip(video_path)
        emotion_task = self.emotion_analyzer.analyze_clip(video_path)
        object_analysis, emotion_analysis = await asyncio.gather(object_task, emotion_task)

        # Optionally enrich with OpenAI Vision hints before story arc
        object_analysis, emotion_analysis = await self._maybe_enrich_with_vision(
            video_path, object_analysis, emotion_analysis
        )
        
        # Create story arc
        story_arc = await self.story_creator.create_story_arc(
            object_analysis, emotion_analysis, story_style
        )
        
        # Apply style preset
        style_preset_result = await self.style_engine.apply_style_preset(
            story_arc, style_preset
        )
        
        # Calculate final score
        final_score = self._calculate_final_score(
            object_analysis, emotion_analysis, story_arc, style_preset_result
        )
        
        # Generate selection reason
        selection_reason = self._generate_selection_reason(
            object_analysis, emotion_analysis, story_arc, final_score
        )
        
        # Generate clip description using OpenAI Vision
        description = "AI analysis in progress..."
        try:
            thumb_path = await self._extract_thumbnail(video_path)
            if thumb_path and self.vision:
                description = self.vision.generate_clip_description(thumb_path)
                # Clean up thumbnail
                try:
                    os.unlink(thumb_path)
                except:
                    pass
        except Exception as e:
            print(f"WARNING:ai_content_selector:Description generation failed: {e}")
            description = "Unable to generate description"
        
        print(f"INFO:ai_content_selector:✅ Analysis complete: score={final_score:.2f}, reason={selection_reason[:50]}...")
        
        result = AIContentSelectionResult(
            clip_path=video_path,
            object_analysis=object_analysis,
            emotion_analysis=emotion_analysis,
            story_arc=story_arc,
            style_preset=style_preset_result,
            final_score=final_score,
            selection_reason=selection_reason,
            description=description
        )
        
        # Cache the result
        self._analysis_cache[cache_key] = result
        
        return result
    
    async def analyze_clip_fast(self, 
                               video_path: str,
                               story_style: str = 'traditional',
                               style_preset: str = 'romantic') -> AIContentSelectionResult:
        """
        Fast analysis mode - skips expensive operations for better performance
        
        Only does basic object detection and visual quality assessment
        """
        print(f"INFO:ai_content_selector:⚡ Fast analyzing clip: {Path(video_path).name}")
        
        # Check cache first (but only for non-object detection parts)
        cache_key = f"{video_path}_{story_style}_{style_preset}_fast_v2"
        # Note: We don't cache object detection as it should be real-time
        
        # Only do basic object detection (skip emotion analysis)
        object_analysis = await self.object_detector.analyze_clip(video_path)
        
        # Create minimal emotion analysis result
        emotion_analysis = EmotionAnalysisResult(
            clip_path=video_path,
            duration=object_analysis.duration,
            emotions={'neutral': 0.5},  # Default neutral emotion score
            emotional_moments=[(0.0, 'neutral', 0.5)],  # Single moment as tuple
            overall_sentiment='neutral',
            excitement_level=0.3,  # Default moderate excitement
            analysis_duration=0.1
        )
        
        # Optional: enrich with OpenAI Vision on fast path too
        object_analysis, emotion_analysis = await self._maybe_enrich_with_vision(
            video_path, object_analysis, emotion_analysis
        )

        # Create basic story arc
        story_arc = await self.story_creator.create_story_arc(
            object_analysis, emotion_analysis, story_style
        )
        
        # Apply style preset
        style_preset_result = await self.style_engine.apply_style_preset(
            story_arc, style_preset
        )
        
        # Calculate final score (simplified)
        final_score = self._calculate_final_score_fast(
            object_analysis, emotion_analysis, story_arc, style_preset_result
        )
        
        # Generate selection reason
        selection_reason = self._generate_selection_reason(
            object_analysis, emotion_analysis, story_arc, final_score
        )
        
        # Generate clip description using OpenAI Vision
        description = "AI analysis in progress..."
        try:
            thumb_path = await self._extract_thumbnail(video_path)
            if thumb_path and self.vision:
                description = self.vision.generate_clip_description(thumb_path)
                # Clean up thumbnail
                try:
                    os.unlink(thumb_path)
                except:
                    pass
        except Exception as e:
            print(f"WARNING:ai_content_selector:Description generation failed: {e}")
            description = "Unable to generate description"
        
        print(f"INFO:ai_content_selector:⚡ Fast analysis complete: score={final_score:.2f}")
        
        result = AIContentSelectionResult(
            clip_path=video_path,
            object_analysis=object_analysis,
            emotion_analysis=emotion_analysis,
            story_arc=story_arc,
            style_preset=style_preset_result,
            final_score=final_score,
            selection_reason=selection_reason,
            description=description
        )
        
        # Cache the result
        self._analysis_cache[cache_key] = result
        
        return result

    async def _maybe_enrich_with_vision(self,
                                       video_path: str,
                                       object_analysis: WeddingObjectDetectionResult,
                                       emotion_analysis: EmotionAnalysisResult) -> Tuple[WeddingObjectDetectionResult, EmotionAnalysisResult]:
        """If enabled, call OpenAI Vision on a first-frame thumbnail and merge hints."""
        if not getattr(self, 'vision', None) or not getattr(self.vision, 'enabled', False):
            return object_analysis, emotion_analysis
        thumb_path: Optional[str] = None
        try:
            thumb_path = await self._extract_thumbnail(video_path)
            if not thumb_path:
                return object_analysis, emotion_analysis
            hints = self.vision.analyze_thumbnail(thumb_path) or {}
            if hints:
                object_analysis, emotion_analysis = self._merge_vision_hints(object_analysis, emotion_analysis, hints)
        except Exception as e:
            print(f"WARNING:ai_content_selector:Vision enrichment failed: {e}")
        finally:
            if thumb_path and os.path.exists(thumb_path):
                try:
                    os.remove(thumb_path)
                except Exception:
                    pass
        return object_analysis, emotion_analysis

    async def _extract_thumbnail(self, video_path: str) -> Optional[str]:
        """Extract first frame using ffmpeg; return path or None."""
        try:
            tmpdir = tempfile.mkdtemp(prefix="cs_thumb_")
            out = os.path.join(tmpdir, "thumb.jpg")
            cmd = [
                "ffmpeg", "-y",
                "-ss", "0",
                "-i", video_path,
                "-frames:v", "1",
                "-q:v", "2",
                out,
            ]
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                return None
            return out
        except Exception:
            return None

    def _merge_vision_hints(self,
                            object_analysis: WeddingObjectDetectionResult,
                            emotion_analysis: EmotionAnalysisResult,
                            hints: Dict[str, Any]) -> Tuple[WeddingObjectDetectionResult, EmotionAnalysisResult]:
        """Merge scene/subjects/emotion from Vision into existing analyses."""
        try:
            scene = hints.get('scene')
            if isinstance(scene, str) and scene:
                object_analysis.scene_classification = scene
            subjects = hints.get('subjects') or []
            if isinstance(subjects, list):
                mapping = {
                    'rings': 'wedding_rings',
                    'cake': 'wedding_cake',
                    'dance': 'dancing',
                    'toast': 'toast_moments',
                    'bouquet': 'bouquet',
                    'guests': 'people',
                    'bride': 'people',
                    'groom': 'people',
                }
                for s in subjects:
                    key = mapping.get(str(s).lower())
                    if key:
                        object_analysis.objects_detected[key] = object_analysis.objects_detected.get(key, 0) + 1
            emotion = hints.get('emotion')
            if isinstance(emotion, str):
                emotions = dict(emotion_analysis.emotions)
                emotions[emotion] = max(0.6, emotions.get(emotion, 0.0))
                emotion_analysis.emotions = emotions
                if emotion in ['romantic', 'joyful', 'intimate', 'celebratory']:
                    emotion_analysis.overall_sentiment = 'positive'
                    emotion_analysis.excitement_level = max(0.5, emotion_analysis.excitement_level)
        except Exception as e:
            print(f"WARNING:ai_content_selector:Failed to merge vision hints: {e}")
        return object_analysis, emotion_analysis
    
    async def select_best_clips(self,
                               video_paths: List[str],
                               target_count: int = 10,
                               story_style: str = 'traditional',
                               style_preset: str = 'romantic',
                               fast_mode: bool = True) -> List[AIContentSelectionResult]:
        """
        Select the best clips from a collection of videos with optimized performance
        
        Args:
            video_paths: List of video file paths
            target_count: Number of clips to select
            story_style: Story template to use
            style_preset: Style preset to apply
            fast_mode: Use fast analysis mode (skips expensive operations)
            
        Returns:
            List of AIContentSelectionResult for selected clips, sorted by quality
        """
        print(f"INFO:ai_content_selector:🎯 Selecting best {target_count} clips from {len(video_paths)} videos")
        
        # For large clip sets or fast mode, use batch processing with early exit
        if len(video_paths) > 8 or fast_mode:
            return await self._select_best_clips_batch(video_paths, target_count, story_style, style_preset, fast_mode)
        
        # For smaller sets, use full parallel analysis
        analysis_tasks = []
        for video_path in video_paths:
            task = self.analyze_clip(video_path, story_style, style_preset)
            analysis_tasks.append(task)
        
        # Run all analyses in parallel
        all_results = await asyncio.gather(*analysis_tasks)
        
        # Sort by final score
        all_results.sort(key=lambda x: x.final_score, reverse=True)
        
        # Select top clips
        selected_clips = all_results[:target_count]
        
        print(f"INFO:ai_content_selector:✅ Selected {len(selected_clips)} clips")
        for i, result in enumerate(selected_clips[:5]):  # Show top 5
            print(f"  {i+1}. {Path(result.clip_path).name} (score: {result.final_score:.2f})")
        
        return selected_clips
    
    async def _select_best_clips_batch(self,
                                     video_paths: List[str],
                                     target_count: int,
                                     story_style: str,
                                     style_preset: str,
                                     fast_mode: bool = True) -> List[AIContentSelectionResult]:
        """
        Optimized batch processing for large clip sets with early exit
        
        Processes clips in batches and stops when we have enough high-quality clips
        """
        print(f"INFO:ai_content_selector:🚀 Using batch processing for {len(video_paths)} clips")
        
        # Process clips in batches of 4 for better memory management
        batch_size = 4
        all_results = []
        processed_count = 0
        
        for i in range(0, len(video_paths), batch_size):
            batch = video_paths[i:i + batch_size]
            print(f"INFO:ai_content_selector:📦 Processing batch {i//batch_size + 1}/{(len(video_paths) + batch_size - 1)//batch_size}")
            
            # Analyze batch in parallel (use fast mode if enabled)
            batch_tasks = []
            for video_path in batch:
                if fast_mode:
                    task = self.analyze_clip_fast(video_path, story_style, style_preset)
                else:
                    task = self.analyze_clip(video_path, story_style, style_preset)
                batch_tasks.append(task)
            
            batch_results = await asyncio.gather(*batch_tasks)
            all_results.extend(batch_results)
            processed_count += len(batch)
            
            # Early exit: if we have enough high-quality clips, stop processing
            if len(all_results) >= target_count * 2:  # Get 2x target for better selection
                high_quality_count = len([r for r in all_results if r.final_score > 0.6])
                if high_quality_count >= target_count:
                    print(f"INFO:ai_content_selector:⚡ Early exit: Found {high_quality_count} high-quality clips after {processed_count} processed")
                    break
        
        # Sort by final score
        all_results.sort(key=lambda x: x.final_score, reverse=True)
        
        # Select top clips
        selected_clips = all_results[:target_count]
        
        print(f"INFO:ai_content_selector:✅ Selected {len(selected_clips)} clips from {processed_count} processed")
        for i, result in enumerate(selected_clips[:5]):  # Show top 5
            print(f"  {i+1}. {Path(result.clip_path).name} (score: {result.final_score:.2f})")
        
        return selected_clips
    
    def _calculate_final_score_fast(self,
                                   object_analysis: WeddingObjectDetectionResult,
                                   emotion_analysis: EmotionAnalysisResult,
                                   story_arc: StoryArcResult,
                                   style_preset: StylePresetResult) -> float:
        """Calculate simplified quality score for fast mode"""
        score = 0.0
        
        # Object detection score (50% - simplified)
        object_score = min(len(object_analysis.key_moments) / 10.0, 1.0)  # Normalize to 0-1
        score += object_score * 0.5
        
        # Story importance (30% - simplified)
        story_score = story_arc.story_importance
        score += story_score * 0.3
        
        # Style match (20% - simplified)
        # Use a default score since StylePresetResult doesn't have overall_score
        style_score = 0.5  # Default moderate style match
        score += style_score * 0.2
        
        return min(score, 1.0)
    
    def _calculate_final_score(self,
                             object_analysis: WeddingObjectDetectionResult,
                             emotion_analysis: EmotionAnalysisResult,
                             story_arc: StoryArcResult,
                             style_preset: StylePresetResult) -> float:
        """Calculate overall quality score for a clip"""
        score = 0.0
        
        # Object detection score (30%)
        object_score = self._calculate_object_score(object_analysis)
        score += object_score * 0.3
        
        # Emotion analysis score (25%)
        emotion_score = self._calculate_emotion_score(emotion_analysis)
        score += emotion_score * 0.25
        
        # Story arc score (25%)
        story_score = self._calculate_story_score(story_arc)
        score += story_score * 0.25
        
        # Style compatibility score (20%)
        style_score = self._calculate_style_score(story_arc, style_preset)
        score += style_score * 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_object_score(self, object_analysis: WeddingObjectDetectionResult) -> float:
        """Calculate score based on object detection"""
        objects = object_analysis.objects_detected
        key_moments = len(object_analysis.key_moments)
        
        score = 0.0
        
        # Wedding-specific objects
        if objects.get('wedding_rings', 0) > 0:
            score += 0.4  # Ring exchange is very important
        if objects.get('wedding_cake', 0) > 0:
            score += 0.3  # Cake cutting is important
        if objects.get('ceremony_moments', 0) > 0:
            score += 0.5  # Ceremony moments are crucial
        if objects.get('dancing', 0) > 0:
            score += 0.2  # Dancing is nice
        if objects.get('people', 0) > 2:
            score += 0.1  # Multiple people is good
        
        # Key moments bonus
        if key_moments > 3:
            score += 0.2
        elif key_moments > 1:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_emotion_score(self, emotion_analysis: EmotionAnalysisResult) -> float:
        """Calculate score based on emotion analysis"""
        emotions = emotion_analysis.emotions
        excitement = emotion_analysis.excitement_level
        sentiment = emotion_analysis.overall_sentiment
        
        score = 0.0
        
        # Positive emotions
        if emotions.get('joy', 0) > 0.6:
            score += 0.3
        if emotions.get('love', 0) > 0.5:
            score += 0.4
        if emotions.get('celebration', 0) > 0.6:
            score += 0.2
        if emotions.get('tenderness', 0) > 0.5:
            score += 0.3
        
        # Excitement level
        if excitement > 0.7:
            score += 0.2
        elif excitement > 0.4:
            score += 0.1
        
        # Overall sentiment
        if sentiment == 'positive':
            score += 0.2
        elif sentiment == 'neutral':
            score += 0.1
        
        # Emotional moments
        if len(emotion_analysis.emotional_moments) > 2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_story_score(self, story_arc: StoryArcResult) -> float:
        """Calculate score based on story arc"""
        score = 0.0
        
        # Story importance
        score += story_arc.story_importance * 0.4
        
        # Scene classification
        scene_scores = {
            'ceremony': 0.9,
            'intimate_moments': 0.8,
            'preparation': 0.6,
            'reception': 0.7,
            'party': 0.5,
            'scenic_moments': 0.4
        }
        score += scene_scores.get(story_arc.scene_classification, 0.5) * 0.3
        
        # Emotional tone
        tone_scores = {
            'romantic': 0.9,
            'intimate': 0.8,
            'joyful': 0.7,
            'dramatic': 0.6,
            'celebratory': 0.5
        }
        score += tone_scores.get(story_arc.emotional_tone, 0.5) * 0.2
        
        # Narrative position
        position_scores = {
            'climax': 0.9,
            'rising_action': 0.8,
            'opening': 0.6,
            'falling_action': 0.7,
            'resolution': 0.5
        }
        score += position_scores.get(story_arc.narrative_position, 0.5) * 0.1
        
        return min(score, 1.0)
    
    def _calculate_style_score(self, story_arc: StoryArcResult, style_preset: StylePresetResult) -> float:
        """Calculate score based on style compatibility"""
        # This is a simplified compatibility check
        # In production, you'd have more sophisticated style matching
        
        score = 0.5  # Base score
        
        # Check if style matches emotional tone
        tone_style_matches = {
            'romantic': ['romantic', 'cinematic'],
            'joyful': ['energetic', 'documentary'],
            'dramatic': ['cinematic'],
            'intimate': ['romantic', 'documentary'],
            'celebratory': ['energetic']
        }
        
        recommended_styles = tone_style_matches.get(story_arc.emotional_tone, [])
        if style_preset.applied_style in recommended_styles:
            score += 0.3
        
        # Check if style matches scene
        scene_style_matches = {
            'ceremony': ['cinematic', 'romantic'],
            'intimate_moments': ['romantic', 'documentary'],
            'party': ['energetic', 'documentary'],
            'preparation': ['documentary', 'romantic']
        }
        
        recommended_styles = scene_style_matches.get(story_arc.scene_classification, [])
        if style_preset.applied_style in recommended_styles:
            score += 0.2
        
        return min(score, 1.0)
    
    def _generate_selection_reason(self,
                                 object_analysis: WeddingObjectDetectionResult,
                                 emotion_analysis: EmotionAnalysisResult,
                                 story_arc: StoryArcResult,
                                 final_score: float) -> str:
        """Generate human-readable reason for clip selection"""
        reasons = []
        
        # Object-based reasons (with higher thresholds to avoid false positives)
        objects = object_analysis.objects_detected
        if objects.get('wedding_rings', 0) >= 2:  # Require at least 2 rings
            reasons.append("features ring exchange")
        if objects.get('wedding_cake', 0) >= 2:  # Require at least 2 cakes (very conservative)
            reasons.append("includes cake cutting")
        if objects.get('ceremony_moments', 0) >= 3:  # Require multiple ceremony moments
            reasons.append("shows ceremony moments")
        if objects.get('dancing', 0) >= 2:  # Require at least 2 people dancing
            reasons.append("captures dancing")
        if objects.get('people', 0) >= 5:  # Good number of people
            reasons.append("shows wedding party")
        
        # Emotion-based reasons (with higher thresholds)
        emotions = emotion_analysis.emotions
        if emotions.get('joy', 0) > 0.7:  # Higher threshold
            reasons.append("high joy and happiness")
        if emotions.get('love', 0) > 0.6:  # Higher threshold
            reasons.append("romantic and loving")
        if emotions.get('celebration', 0) > 0.7:  # Higher threshold
            reasons.append("celebratory atmosphere")
        
        # Story-based reasons
        if story_arc.story_importance > 0.7:
            reasons.append("high story importance")
        if story_arc.emotional_tone == 'romantic':
            reasons.append("romantic tone")
        if story_arc.emotional_tone == 'intimate':
            reasons.append("intimate moment")
        if story_arc.narrative_position == 'climax':
            reasons.append("climactic moment")
        
        # Key moments (with higher threshold)
        if len(object_analysis.key_moments) > 3:
            reasons.append(f"{len(object_analysis.key_moments)} key moments")
        
        # Score-based reason
        if final_score > 0.8:
            reasons.append("excellent overall quality")
        elif final_score > 0.6:
            reasons.append("good quality")
        else:
            reasons.append("decent quality")
        
        # Fallback reasons based on what we actually detected
        if not reasons:
            if objects.get('people', 0) > 0:
                reasons.append("shows people")
            if story_arc.story_importance > 0.3:
                reasons.append("story relevance")
            reasons.append("meets basic criteria")
        
        return ", ".join(reasons)
    
    async def create_intelligent_highlight(self,
                                         video_paths: List[str],
                                         music_path: str,
                                         target_duration: int = 60,
                                         story_style: str = 'traditional',
                                         style_preset: str = 'romantic') -> Dict[str, Any]:
        """
        Create an intelligent highlight using AI-powered content selection
        
        Args:
            video_paths: List of video file paths
            music_path: Path to music file
            target_duration: Target duration in seconds
            story_style: Story template to use
            style_preset: Style preset to apply
            
        Returns:
            Dictionary with highlight information and selected clips
        """
        print(f"INFO:ai_content_selector:🎬 Creating intelligent highlight with {len(video_paths)} clips")
        print(f"INFO:ai_content_selector:📖 Story style: {story_style}, Style preset: {style_preset}")
        
        # Calculate target clip count based on duration
        avg_clip_duration = 3.0  # Average clip duration
        target_clip_count = min(len(video_paths), max(5, target_duration // avg_clip_duration))
        
        # Select best clips
        selected_clips = await self.select_best_clips(
            video_paths, target_clip_count, story_style, style_preset
        )
        
        # Create summary
        highlight_summary = {
            'total_clips_analyzed': len(video_paths),
            'clips_selected': len(selected_clips),
            'story_style': story_style,
            'style_preset': style_preset,
            'target_duration': target_duration,
            'selected_clips': [
                {
                    'path': clip.clip_path,
                    'score': clip.final_score,
                    'scene': clip.story_arc.scene_classification,
                    'tone': clip.story_arc.emotional_tone,
                    'importance': clip.story_arc.story_importance,
                    'reason': clip.selection_reason
                }
                for clip in selected_clips
            ],
            'story_breakdown': self._create_story_breakdown(selected_clips),
            'quality_metrics': self._calculate_quality_metrics(selected_clips),
            'storyboard_suggestion': self._suggest_storyboard(selected_clips)
        }
        
        print(f"INFO:ai_content_selector:✅ Intelligent highlight created with {len(selected_clips)} clips")
        
        return highlight_summary

    def _suggest_storyboard(self, selected_clips: List['AIContentSelectionResult']) -> List[Dict[str, Any]]:
        """Suggest an ordered storyboard based on scene classes and scores."""
        if not selected_clips:
            return []
        scene_order = {
            'preparation': 0,
            'intimate_moments': 1,
            'ceremony': 2,
            'reception': 3,
            'party': 4,
            'scenic_moments': 5
        }
        def sort_key(clip: 'AIContentSelectionResult'):
            return (scene_order.get(clip.story_arc.scene_classification, 99), -clip.final_score)
        ordered = sorted(selected_clips, key=sort_key)
        return [
            {
                'path': c.clip_path,
                'scene': c.story_arc.scene_classification,
                'tone': c.story_arc.emotional_tone,
                'score': c.final_score,
                'reason': c.selection_reason
            }
            for c in ordered
        ]
    
    def _create_story_breakdown(self, selected_clips: List[AIContentSelectionResult]) -> Dict[str, Any]:
        """Create a breakdown of the story structure"""
        scene_counts = {}
        tone_counts = {}
        position_counts = {}
        
        for clip in selected_clips:
            scene = clip.story_arc.scene_classification
            tone = clip.story_arc.emotional_tone
            position = clip.story_arc.narrative_position
            
            scene_counts[scene] = scene_counts.get(scene, 0) + 1
            tone_counts[tone] = tone_counts.get(tone, 0) + 1
            position_counts[position] = position_counts.get(position, 0) + 1
        
        return {
            'scenes': scene_counts,
            'tones': tone_counts,
            'positions': position_counts,
            'total_clips': len(selected_clips)
        }
    
    def _calculate_quality_metrics(self, selected_clips: List[AIContentSelectionResult]) -> Dict[str, float]:
        """Calculate quality metrics for the selected clips"""
        if not selected_clips:
            return {}
        
        scores = [clip.final_score for clip in selected_clips]
        
        return {
            'average_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores),
            'high_quality_clips': len([s for s in scores if s > 0.7]),
            'story_importance_avg': sum(clip.story_arc.story_importance for clip in selected_clips) / len(selected_clips)
        }
    
    async def generate_story_narrative(self, 
                                     video_paths: List[str],
                                     narrative_style: str = 'modern',
                                     target_duration: float = 60.0) -> StoryNarrative:
        """
        Generate a complete story narrative from video clips
        
        Args:
            video_paths: List of video file paths
            narrative_style: Style of narrative ('traditional', 'modern', 'cinematic', 'documentary')
            target_duration: Target duration for the final story in seconds
            
        Returns:
            StoryNarrative with complete story structure
        """
        print(f"INFO:ai_content_selector:🎬 Generating {narrative_style} story narrative from {len(video_paths)} clips")
        
        # Analyze all clips to create descriptions
        clip_descriptions = []
        
        for video_path in video_paths:
            print(f"INFO:ai_content_selector:📹 Analyzing clip: {Path(video_path).name}")
            
            # Run AI analysis on the clip
            try:
                print(f"INFO:ai_content_selector:🔍 Starting analysis for {video_path}")
                analysis_result = await self.analyze_clip(video_path, 'traditional', 'romantic')
                print(f"INFO:ai_content_selector:✅ Analysis completed for {video_path}")
                
                # Create clip description from analysis
                clip_description = ClipDescription(
                    clip_path=video_path,
                    description=analysis_result.description,
                    scene_type=analysis_result.story_arc.scene_classification,
                    emotional_tone=analysis_result.story_arc.emotional_tone,
                    key_moments=[str(moment) for moment in analysis_result.object_analysis.key_moments],
                    people_count=analysis_result.object_analysis.people_count,
                    quality_score=analysis_result.final_score,
                    timestamp=0.0  # We'll calculate this based on selection order
                )
                
                clip_descriptions.append(clip_description)
                print(f"INFO:ai_content_selector:✅ Clip description created for {video_path}")
                
            except Exception as e:
                print(f"WARNING:ai_content_selector:Failed to analyze {video_path}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not clip_descriptions:
            raise ValueError("No clips could be analyzed for story generation")
        
        # Generate story narrative
        story_narrative = await self.story_narrative.generate_story_narrative(
            clip_descriptions, narrative_style, target_duration
        )
        
        print(f"INFO:ai_content_selector:✅ Generated story: '{story_narrative.story_title}'")
        return story_narrative
