"""
FFmpeg and ffprobe availability checker
Cross-platform verification of FFmpeg installation
"""

import subprocess
import shutil
import platform
from typing import Tuple, Optional

class FFmpegChecker:
    """Handles FFmpeg and ffprobe availability checks"""
    
    @staticmethod
    def find_ffmpeg_executable() -> Optional[str]:
        """Find FFmpeg executable in PATH or common locations"""
        # Try common names
        names = ["ffmpeg", "ffmpeg.exe"]
        
        for name in names:
            if shutil.which(name):
                return name
        
        # Platform-specific fallbacks
        system = platform.system().lower()
        
        if system == "windows":
            common_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"
            ]
        elif system == "darwin":  # macOS
            common_paths = [
                "/usr/local/bin/ffmpeg",
                "/opt/homebrew/bin/ffmpeg",
                "/usr/bin/ffmpeg"
            ]
        else:  # Linux
            common_paths = [
                "/usr/bin/ffmpeg",
                "/usr/local/bin/ffmpeg",
                "/snap/bin/ffmpeg"
            ]
        
        for path in common_paths:
            if shutil.which(path):
                return path
        
        return None
    
    @staticmethod
    def find_ffprobe_executable() -> Optional[str]:
        """Find ffprobe executable in PATH or common locations"""
        # Try common names
        names = ["ffprobe", "ffprobe.exe"]
        
        for name in names:
            if shutil.which(name):
                return name
        
        # Platform-specific fallbacks
        system = platform.system().lower()
        
        if system == "windows":
            common_paths = [
                r"C:\ffmpeg\bin\ffprobe.exe",
                r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe"
            ]
        elif system == "darwin":  # macOS
            common_paths = [
                "/usr/local/bin/ffprobe",
                "/opt/homebrew/bin/ffprobe",
                "/usr/bin/ffprobe"
            ]
        else:  # Linux
            common_paths = [
                "/usr/bin/ffprobe",
                "/usr/local/bin/ffprobe",
                "/snap/bin/ffprobe"
            ]
        
        for path in common_paths:
            if shutil.which(path):
                return path
        
        return None
    
    @classmethod
    def check_ffmpeg_availability(cls) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if both FFmpeg and ffprobe are available
        
        Returns:
            Tuple of (is_available, ffmpeg_path, ffprobe_path)
        """
        ffmpeg_path = cls.find_ffmpeg_executable()
        ffprobe_path = cls.find_ffprobe_executable()
        
        is_available = ffmpeg_path is not None and ffprobe_path is not None
        
        return is_available, ffmpeg_path, ffprobe_path
    
    @classmethod
    def verify_ffmpeg_functionality(cls, ffmpeg_path: str, ffprobe_path: str) -> Tuple[bool, str]:
        """
        Verify that FFmpeg and ffprobe actually work
        
        Returns:
            Tuple of (is_working, version_info)
        """
        try:
            # Test FFmpeg
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"FFmpeg test failed: {result.stderr}"
            
            # Test ffprobe
            result = subprocess.run(
                [ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False, f"ffprobe test failed: {result.stderr}"
            
            # Extract version info
            version_line = result.stdout.split('\n')[0]
            return True, version_line
            
        except subprocess.TimeoutExpired:
            return False, "FFmpeg/ffprobe test timed out"
        except Exception as e:
            return False, f"FFmpeg/ffprobe test error: {str(e)}"
    
    @classmethod
    def get_installation_instructions(cls) -> str:
        """Get platform-specific installation instructions"""
        system = platform.system().lower()
        
        if system == "windows":
            return """
Windows FFmpeg Installation:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to C:\\ffmpeg\\
3. Add C:\\ffmpeg\\bin to your PATH environment variable
4. Restart your terminal/command prompt
5. Verify with: ffmpeg -version
            """.strip()
        
        elif system == "darwin":  # macOS
            return """
macOS FFmpeg Installation:
1. Install Homebrew: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install FFmpeg: brew install ffmpeg
3. Verify with: ffmpeg -version
            """.strip()
        
        else:  # Linux
            return """
Linux FFmpeg Installation:
Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
CentOS/RHEL: sudo yum install ffmpeg
Arch Linux: sudo pacman -S ffmpeg
Snap: sudo snap install ffmpeg
Verify with: ffmpeg -version
            """.strip()
