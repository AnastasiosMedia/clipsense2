#!/usr/bin/env python3
"""
Final Cut Pro 7 XML Generator for Premiere Pro

Creates FCP7 XML (.xml) files that Premiere Pro can import directly.
This is the recommended approach according to Adobe's documentation.
"""

import json
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
import urllib.parse


class FCP7XMLGenerator:
    """Generates FCP7 XML files for Premiere Pro import"""
    
    def __init__(self):
        self.sequence_name = "ClipSense Bar Detection Sequence"
        self.fps = 25
        self.width = 1280
        self.height = 720
        
    def create_fcp7_xml(self, timeline_path: str, output_path: str) -> str:
        """
        Create FCP7 XML file from timeline data
        
        Args:
            timeline_path: Path to timeline.json file
            output_path: Path where to save the .xml file
            
        Returns:
            Path to created XML file
        """
        # Load timeline data
        with open(timeline_path, 'r') as f:
            timeline = json.load(f)
        
        # Create FCP7 XML structure
        root = self._create_xmeml_root()
        
        # Add sequence
        sequence = self._create_sequence(timeline)
        root.append(sequence)
        
        # Write to file
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0)
        
        # Write with proper XML declaration
        with open(output_path, 'wb') as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding='utf-8', xml_declaration=False)
        
        return output_path
    
    def _create_xmeml_root(self) -> ET.Element:
        """Create the root xmeml element"""
        root = ET.Element("xmeml")
        root.set("version", "5")
        return root
    
    def _create_sequence(self, timeline: Dict[str, Any]) -> ET.Element:
        """Create sequence element with video and audio tracks"""
        
        sequence = ET.Element("sequence")
        sequence.set("id", "sequence-1")
        
        # Sequence name
        name = ET.SubElement(sequence, "name")
        name.text = self.sequence_name
        
        # Duration in frames
        duration_seconds = timeline["target_seconds"]
        duration_frames = int(duration_seconds * self.fps)
        duration = ET.SubElement(sequence, "duration")
        duration.text = str(duration_frames)
        
        # Rate (frame rate)
        rate = ET.SubElement(sequence, "rate")
        timebase = ET.SubElement(rate, "timebase")
        timebase.text = str(self.fps)
        ntsc = ET.SubElement(rate, "ntsc")
        ntsc.text = "FALSE"
        
        # Timecode
        timecode = ET.SubElement(sequence, "timecode")
        timecode_rate = ET.SubElement(timecode, "rate")
        timecode_rate_timebase = ET.SubElement(timecode_rate, "timebase")
        timecode_rate_timebase.text = str(self.fps)
        timecode_rate_ntsc = ET.SubElement(timecode_rate, "ntsc")
        timecode_rate_ntsc.text = "FALSE"
        timecode_string = ET.SubElement(timecode, "string")
        timecode_string.text = "01:00:00:00"
        timecode_frame = ET.SubElement(timecode, "frame")
        timecode_frame.text = "0"
        timecode_displayformat = ET.SubElement(timecode, "displayformat")
        timecode_displayformat.text = "NDF"
        
        # Media section
        media = ET.SubElement(sequence, "media")
        
        # Video track
        video_track = self._create_video_track(timeline)
        media.append(video_track)
        
        # Audio track
        audio_track = self._create_audio_track(timeline)
        media.append(audio_track)
        
        return sequence
    
    def _create_video_track(self, timeline: Dict[str, Any]) -> ET.Element:
        """Create video track with all clips"""
        
        video = ET.Element("video")
        
        # Format
        format_elem = ET.SubElement(video, "format")
        sample_characteristics = ET.SubElement(format_elem, "samplecharacteristics")
        rate = ET.SubElement(sample_characteristics, "rate")
        timebase = ET.SubElement(rate, "timebase")
        timebase.text = str(self.fps)
        ntsc = ET.SubElement(rate, "ntsc")
        ntsc.text = "FALSE"
        width = ET.SubElement(sample_characteristics, "width")
        width.text = str(self.width)
        height = ET.SubElement(sample_characteristics, "height")
        height.text = str(self.height)
        pixelaspectratio = ET.SubElement(sample_characteristics, "pixelaspectratio")
        pixelaspectratio.text = "square"
        fielddominance = ET.SubElement(sample_characteristics, "fielddominance")
        fielddominance.text = "none"
        colordepth = ET.SubElement(sample_characteristics, "colordepth")
        colordepth.text = "24"
        
        # Track
        track = ET.SubElement(video, "track")
        
        # Add all video clips
        current_frame = 0
        for i, clip in enumerate(timeline["clips"]):
            clip_element = self._create_video_clipitem(clip, i, current_frame)
            track.append(clip_element)
            
            # Update current frame for next clip (2 seconds = 50 frames at 25fps)
            current_frame += 50  # 2 seconds * 25 fps
        
        return video
    
    def _create_video_clipitem(self, clip: Dict[str, Any], index: int, start_frame: int) -> ET.Element:
        """Create individual video clipitem element"""
        
        clipitem = ET.Element("clipitem")
        clipitem.set("id", f"clipitem-{index + 1}")
        
        # Name
        name = ET.SubElement(clipitem, "name")
        name.text = os.path.basename(clip["src"])
        
        # Duration (2 seconds = 50 frames at 25fps)
        duration_frames = 50
        duration = ET.SubElement(clipitem, "duration")
        duration.text = str(duration_frames)
        
        # Start/End times on timeline
        start = ET.SubElement(clipitem, "start")
        start.text = str(start_frame)
        end = ET.SubElement(clipitem, "end")
        end.text = str(start_frame + duration_frames)
        
        # In/Out points in source media
        in_point = ET.SubElement(clipitem, "in")
        in_point.text = str(int(clip["in"] * self.fps))
        out_point = ET.SubElement(clipitem, "out")
        out_point.text = str(int(clip["out"] * self.fps))
        
        # File reference
        file_elem = ET.SubElement(clipitem, "file")
        file_elem.set("id", f"file-{index + 1}")
        
        # File path (URL encoded)
        pathurl = ET.SubElement(file_elem, "pathurl")
        file_path = urllib.parse.quote(clip["src"], safe=':/')
        pathurl.text = f"file://{file_path}"
        
        # File duration
        file_duration = ET.SubElement(file_elem, "duration")
        file_duration.text = str(int((clip["out"] - clip["in"]) * self.fps))
        
        # File rate
        file_rate = ET.SubElement(file_elem, "rate")
        file_timebase = ET.SubElement(file_rate, "timebase")
        file_timebase.text = str(self.fps)
        file_ntsc = ET.SubElement(file_rate, "ntsc")
        file_ntsc.text = "FALSE"
        
        # File media characteristics
        file_media = ET.SubElement(file_elem, "media")
        file_video = ET.SubElement(file_media, "video")
        file_samplecharacteristics = ET.SubElement(file_video, "samplecharacteristics")
        file_width = ET.SubElement(file_samplecharacteristics, "width")
        file_width.text = str(self.width)
        file_height = ET.SubElement(file_samplecharacteristics, "height")
        file_height.text = str(self.height)
        file_pixelaspectratio = ET.SubElement(file_samplecharacteristics, "pixelaspectratio")
        file_pixelaspectratio.text = "square"
        file_fielddominance = ET.SubElement(file_samplecharacteristics, "fielddominance")
        file_fielddominance.text = "none"
        
        # Source track
        sourcetrack = ET.SubElement(clipitem, "sourcetrack")
        mediatype = ET.SubElement(sourcetrack, "mediatype")
        mediatype.text = "video"
        trackindex = ET.SubElement(sourcetrack, "trackindex")
        trackindex.text = "1"
        
        return clipitem
    
    def _create_audio_track(self, timeline: Dict[str, Any]) -> ET.Element:
        """Create audio track with music"""
        
        audio = ET.Element("audio")
        
        # Format
        format_elem = ET.SubElement(audio, "format")
        sample_characteristics = ET.SubElement(format_elem, "samplecharacteristics")
        depth = ET.SubElement(sample_characteristics, "depth")
        depth.text = "16"
        samplerate = ET.SubElement(sample_characteristics, "samplerate")
        samplerate.text = "48000"
        
        # Track
        track = ET.SubElement(audio, "track")
        
        # Music clipitem
        music_clipitem = self._create_music_clipitem(timeline)
        track.append(music_clipitem)
        
        return audio
    
    def _create_music_clipitem(self, timeline: Dict[str, Any]) -> ET.Element:
        """Create music clipitem element"""
        
        clipitem = ET.Element("clipitem")
        clipitem.set("id", "music-clipitem")
        
        # Name
        name = ET.SubElement(clipitem, "name")
        name.text = "Background Music"
        
        # Duration (full timeline duration)
        duration_seconds = timeline["target_seconds"]
        duration_frames = int(duration_seconds * self.fps)
        duration = ET.SubElement(clipitem, "duration")
        duration.text = str(duration_frames)
        
        # Start/End times (spans entire sequence)
        start = ET.SubElement(clipitem, "start")
        start.text = "0"
        end = ET.SubElement(clipitem, "end")
        end.text = str(duration_frames)
        
        # In/Out points (full music file)
        in_point = ET.SubElement(clipitem, "in")
        in_point.text = "0"
        out_point = ET.SubElement(clipitem, "out")
        out_point.text = str(duration_frames)
        
        # File reference
        file_elem = ET.SubElement(clipitem, "file")
        file_elem.set("id", "music-file")
        
        # File path (URL encoded)
        pathurl = ET.SubElement(file_elem, "pathurl")
        file_path = urllib.parse.quote(timeline["music"], safe=':/')
        pathurl.text = f"file://{file_path}"
        
        # File duration
        file_duration = ET.SubElement(file_elem, "duration")
        file_duration.text = str(duration_frames)
        
        # File rate
        file_rate = ET.SubElement(file_elem, "rate")
        file_timebase = ET.SubElement(file_rate, "timebase")
        file_timebase.text = str(self.fps)
        file_ntsc = ET.SubElement(file_rate, "ntsc")
        file_ntsc.text = "FALSE"
        
        # File media characteristics
        file_media = ET.SubElement(file_elem, "media")
        file_audio = ET.SubElement(file_media, "audio")
        file_samplecharacteristics = ET.SubElement(file_audio, "samplecharacteristics")
        file_depth = ET.SubElement(file_samplecharacteristics, "depth")
        file_depth.text = "16"
        file_samplerate = ET.SubElement(file_samplecharacteristics, "samplerate")
        file_samplerate.text = "48000"
        
        # Source track
        sourcetrack = ET.SubElement(clipitem, "sourcetrack")
        mediatype = ET.SubElement(sourcetrack, "mediatype")
        mediatype.text = "audio"
        trackindex = ET.SubElement(sourcetrack, "trackindex")
        trackindex.text = "1"
        
        return clipitem


def generate_fcp7_xml(timeline_path: str, output_path: str) -> str:
    """
    Generate FCP7 XML file for Premiere Pro import
    
    Args:
        timeline_path: Path to timeline.json file
        output_path: Path where to save the .xml file
        
    Returns:
        Path to created XML file
    """
    generator = FCP7XMLGenerator()
    return generator.create_fcp7_xml(timeline_path, output_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python fcp7_xml_generator.py <timeline.json> <output.xml>")
        sys.exit(1)
    
    timeline_path = sys.argv[1]
    output_path = sys.argv[2]
    
    result = generate_fcp7_xml(timeline_path, output_path)
    print(f"FCP7 XML file created: {result}")
    print("Import this .xml file into Premiere Pro to create the sequence")
