"""
Beat Detection Module for ClipSense

Analyzes music files to detect beats and downbeats for precise clip timing.
Uses librosa for audio analysis and beat tracking.
"""

import os
import librosa
import numpy as np
from typing import List, Tuple, Optional
import tempfile
import subprocess
import asyncio


class BeatDetector:
    """Detects beats and downbeats in audio files for precise clip timing"""
    
    def __init__(self):
        self.sample_rate = 22050  # Standard sample rate for beat detection
        self.hop_length = 512     # Hop length for analysis
    
    async def detect_beats(self, music_path: str, target_duration: float) -> List[float]:
        """
        Detect beats in music file and return beat times for target duration
        
        Args:
            music_path: Path to music file
            target_duration: Target duration in seconds
            
        Returns:
            List of beat times in seconds
        """
        try:
            # Convert to WAV if needed for better compatibility
            wav_path = await self._ensure_wav_format(music_path)
            
            # Load audio file
            print(f"🎵 Loading audio file: {music_path}")
            y, sr = librosa.load(wav_path, sr=self.sample_rate)
            
            # Detect tempo and beats
            print("🥁 Detecting tempo and beats...")
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            
            # Convert beat frames to time
            beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
            
            print(f"🎼 Detected tempo: {tempo:.1f} BPM")
            print(f"🥁 Found {len(beat_times)} beats")
            
            # Filter beats to target duration
            target_beats = beat_times[beat_times <= target_duration]
            
            if len(target_beats) == 0:
                print("⚠️  No beats found in target duration, using fallback timing")
                return self._fallback_timing(target_duration)
            
            print(f"🎯 Using {len(target_beats)} beats for {target_duration:.1f}s duration")
            return target_beats.tolist()
            
        except Exception as e:
            print(f"❌ Beat detection failed: {e}")
            print("🔄 Falling back to regular timing")
            return self._fallback_timing(target_duration)
    
    async def detect_downbeats(self, music_path: str, target_duration: float) -> List[float]:
        """
        Detect downbeats (strong beats) in music file
        
        Args:
            music_path: Path to music file
            target_duration: Target duration in seconds
            
        Returns:
            List of downbeat times in seconds
        """
        try:
            # Convert to WAV if needed
            wav_path = await self._ensure_wav_format(music_path)
            
            # Load audio file
            print(f"🎵 Loading audio file for downbeat detection: {music_path}")
            y, sr = librosa.load(wav_path, sr=self.sample_rate)
            
            # Detect tempo and beats first
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            beat_times = librosa.frames_to_time(beats, sr=sr, hop_length=self.hop_length)
            
            # Detect downbeats using onset strength
            print("🥁 Detecting downbeats...")
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=self.hop_length)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=self.hop_length)
            
            # Find downbeats by looking for strong onsets that align with beat grid
            downbeats = []
            beat_interval = 60.0 / tempo  # Time between beats
            
            for beat_time in beat_times:
                if beat_time > target_duration:
                    break
                    
                # Find the strongest onset near this beat
                nearby_onsets = onset_times[
                    (onset_times >= beat_time - beat_interval/4) & 
                    (onset_times <= beat_time + beat_interval/4)
                ]
                
                if len(nearby_onsets) > 0:
                    # Use the closest onset to the beat
                    closest_onset = nearby_onsets[np.argmin(np.abs(nearby_onsets - beat_time))]
                    downbeats.append(closest_onset)
                else:
                    # Use the beat time if no strong onset nearby
                    downbeats.append(beat_time)
            
            # Filter to target duration
            target_downbeats = [db for db in downbeats if db <= target_duration]
            
            if len(target_downbeats) == 0:
                print("⚠️  No downbeats found, using regular beats")
                return beat_times[beat_times <= target_duration].tolist()
            
            print(f"🎯 Found {len(target_downbeats)} downbeats for {target_duration:.1f}s duration")
            return target_downbeats
            
        except Exception as e:
            print(f"❌ Downbeat detection failed: {e}")
            print("🔄 Falling back to regular beat detection")
            return await self.detect_beats(music_path, target_duration)
    
    async def _ensure_wav_format(self, music_path: str) -> str:
        """Convert music file to WAV format for better librosa compatibility"""
        if music_path.lower().endswith('.wav'):
            return music_path
        
        # Create temporary WAV file
        temp_dir = tempfile.gettempdir()
        wav_path = os.path.join(temp_dir, f"temp_beat_detect_{os.getpid()}.wav")
        
        try:
            # Convert to WAV using FFmpeg
            cmd = [
                "ffmpeg", "-y",
                "-i", music_path,
                "-acodec", "pcm_s16le",
                "-ar", str(self.sample_rate),
                "-ac", "1",  # Mono for beat detection
                wav_path
            ]
            
            print(f"🔄 Converting to WAV for beat detection...")
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg conversion failed: {stderr.decode()}")
            
            return wav_path
            
        except Exception as e:
            print(f"⚠️  WAV conversion failed: {e}")
            # Return original path as fallback
            return music_path
    
    def _fallback_timing(self, target_duration: float) -> List[float]:
        """Fallback timing when beat detection fails"""
        # Use regular intervals based on typical music tempo
        interval = 0.5  # 120 BPM = 0.5 second intervals
        beats = []
        current_time = 0.0
        
        while current_time < target_duration:
            beats.append(current_time)
            current_time += interval
        
        return beats
    
    def cleanup_temp_files(self):
        """Clean up temporary WAV files"""
        temp_dir = tempfile.gettempdir()
        pattern = f"temp_beat_detect_{os.getpid()}.wav"
        
        try:
            for file in os.listdir(temp_dir):
                if file.startswith("temp_beat_detect_"):
                    os.remove(os.path.join(temp_dir, file))
        except Exception:
            pass  # Ignore cleanup errors
