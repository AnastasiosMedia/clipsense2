"""
ClipSense FastAPI Backend Worker

Handles video processing requests from the Tauri frontend.
Creates highlight videos by trimming, concatenating clips and overlaying music.
"""

import os
import tempfile
import subprocess
import json
import time
import socket
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from video_processor import VideoProcessor
from conform import ConformProcessor
from config import Config
from ffmpeg_checker import FFmpegChecker
from simple_beat_detector import SimpleBeatDetector
from fcp7_xml_generator import generate_fcp7_xml

# Global state
ffmpeg_available = False
ffmpeg_path = None
ffprobe_path = None
ffmpeg_version = None

def check_port_availability(host: str, port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

def find_available_port(start_port: int, max_retries: int = 3) -> Optional[int]:
    """Find an available port starting from start_port"""
    for i in range(max_retries):
        port = start_port + i
        if check_port_availability(Config.WORKER_HOST, port):
            return port
        print(f"Port {port} is occupied, trying {port + 1}...")
        time.sleep(Config.PORT_RETRY_DELAY)
    return None

def initialize_ffmpeg_check():
    """Initialize FFmpeg availability check"""
    global ffmpeg_available, ffmpeg_path, ffprobe_path, ffmpeg_version
    
    print("🔍 Checking FFmpeg availability...")
    
    is_available, ffmpeg_path, ffprobe_path = FFmpegChecker.check_ffmpeg_availability()
    
    if is_available:
        is_working, version_info = FFmpegChecker.verify_ffmpeg_functionality(ffmpeg_path, ffprobe_path)
        if is_working:
            ffmpeg_available = True
            ffmpeg_version = version_info
            print(f"✅ FFmpeg found: {version_info}")
        else:
            print(f"❌ FFmpeg verification failed: {version_info}")
    else:
        print("❌ FFmpeg or ffprobe not found in PATH")
        print(FFmpegChecker.get_installation_instructions())

# Initialize FFmpeg check
initialize_ffmpeg_check()

# Initialize FastAPI app
app = FastAPI(
    title="ClipSense Worker",
    description="Local video processing worker for ClipSense",
    version="1.0.0"
)

# Enable CORS for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://127.0.0.1:1420"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video processor
video_processor = VideoProcessor()

class AutoCutRequest(BaseModel):
    """Request model for auto-cut processing"""
    clips: List[str]
    music: str
    target_seconds: int = 60

class AutoCutResponse(BaseModel):
    """Response model for auto-cut processing"""
    ok: bool
    proxy_output: Optional[str] = None
    timeline_path: Optional[str] = None
    timeline_hash: Optional[str] = None
    error: Optional[str] = None
    proxy_time: Optional[float] = None
    render_time: Optional[float] = None
    total_time: Optional[float] = None


class ConformRequest(BaseModel):
    """Request model for conform processing"""
    timeline_path: str
    out: Optional[str] = None
    music: Optional[str] = None
    no_audio: bool = False


class ConformResponse(BaseModel):
    """Response model for conform processing"""
    ok: bool
    master_output: Optional[str] = None
    error: Optional[str] = None
    conform_time: Optional[float] = None


class AnalyzeMusicRequest(BaseModel):
    """Request model for music analysis"""
    music_path: str
    target_duration: Optional[float] = None


class AnalyzeMusicResponse(BaseModel):
    """Response model for music analysis"""
    ok: bool
    tempo: Optional[float] = None
    beat_times: Optional[List[float]] = None
    bar_times: Optional[List[float]] = None
    bars_per_minute: Optional[float] = None
    beats_per_bar: Optional[int] = None
    time_signature: Optional[str] = None
    analysis_duration: Optional[float] = None
    error: Optional[str] = None


class FCP7XMLRequest(BaseModel):
    """Request model for FCP7 XML generation"""
    timeline_path: str
    output_path: Optional[str] = None


class FCP7XMLResponse(BaseModel):
    """Response model for FCP7 XML generation"""
    ok: bool
    xml_path: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ClipSense Worker is running", "status": "healthy"}

@app.post("/autocut", response_model=AutoCutResponse)
async def auto_cut(request: AutoCutRequest):
    """
    Process video clips and music to create a highlight video
    
    Args:
        request: AutoCutRequest containing clips, music, and target duration
        
    Returns:
        AutoCutResponse with output file path or error message
    """
    start_time = time.time()
    
    # Check FFmpeg availability first
    if not ffmpeg_available:
        return AutoCutResponse(
            ok=False,
            error="FFmpeg not found. Please install FFmpeg and restart the worker."
        )
    
    try:
        # Validate input files exist
        for clip_path in request.clips:
            if not os.path.exists(clip_path):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Video file not found: {clip_path}"
                )
        
        if not os.path.exists(request.music):
            raise HTTPException(
                status_code=400, 
                detail=f"Music file not found: {request.music}"
            )
        
        # Process the videos with timing
        result = await video_processor.process_highlight(
            clips=request.clips,
            music_path=request.music,
            target_duration=request.target_seconds
        )
        
        total_time = time.time() - start_time
        
        return AutoCutResponse(
            ok=True,
            proxy_output=result["proxy_output"],
            timeline_path=result["timeline_path"],
            timeline_hash=result["timeline_hash"],
            proxy_time=result.get("proxy_time"),
            render_time=result.get("render_time"),
            total_time=total_time
        )
        
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr if isinstance(e.stderr, str) else e.stderr.decode() if e.stderr else str(e)
        # Truncate very long error messages
        if len(stderr_text) > 500:
            stderr_text = stderr_text[:500] + "... (truncated)"
        error_msg = f"FFmpeg processing failed: {stderr_text}"
        return AutoCutResponse(ok=False, error=error_msg)
        
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        print(f"❌ General exception caught: {type(e).__name__}: {e}")
        return AutoCutResponse(ok=False, error=error_msg)


@app.post("/conform", response_model=ConformResponse)
async def conform_timeline(request: ConformRequest):
    """Conform a timeline to master quality output"""
    if not ffmpeg_available:
        return ConformResponse(ok=False, error="FFmpeg not available")
    
    start_time = time.time()
    
    try:
        processor = ConformProcessor()
        result = await processor.conform_from_timeline(
            timeline_path=request.timeline_path,
            output_path=request.out,
            music_path=request.music,
            no_audio=request.no_audio
        )
        
        conform_time = time.time() - start_time
        
        return ConformResponse(
            ok=True,
            master_output=result["output"],
            conform_time=conform_time
        )
        
    except subprocess.CalledProcessError as e:
        stderr_text = e.stderr if isinstance(e.stderr, str) else e.stderr.decode() if e.stderr else str(e)
        if len(stderr_text) > 500:
            stderr_text = stderr_text[:500] + "... (truncated)"
        error_msg = f"FFmpeg conform failed: {stderr_text}"
        return ConformResponse(ok=False, error=error_msg)
        
    except Exception as e:
        error_msg = f"Conform error: {str(e)}"
        return ConformResponse(ok=False, error=error_msg)


@app.post("/analyze_music", response_model=AnalyzeMusicResponse)
async def analyze_music(request: AnalyzeMusicRequest):
    """
    Analyze music file to detect tempo, beats, and bars
    
    Args:
        request: AnalyzeMusicRequest containing music path and optional target duration
        
    Returns:
        AnalyzeMusicResponse with tempo, beat times, bar times, and metadata
    """
    if not ffmpeg_available:
        return AnalyzeMusicResponse(ok=False, error="FFmpeg not available")
    
    try:
        # Validate music file exists
        if not os.path.exists(request.music_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Music file not found: {request.music_path}"
            )
        
        # Analyze the music
        detector = SimpleBeatDetector()
        analysis = await detector.analyze_music(request.music_path, request.target_duration)
        
        return AnalyzeMusicResponse(
            ok=True,
            tempo=analysis["tempo"],
            beat_times=analysis["beat_times"],
            bar_times=analysis["bar_times"],
            bars_per_minute=analysis["bars_per_minute"],
            beats_per_bar=analysis["beats_per_bar"],
            time_signature=analysis["time_signature"],
            analysis_duration=analysis["analysis_duration"]
        )
        
    except Exception as e:
        error_msg = f"Music analysis error: {str(e)}"
        print(f"❌ Music analysis exception: {type(e).__name__}: {e}")
        return AnalyzeMusicResponse(ok=False, error=error_msg)


@app.post("/generate_fcp7_xml", response_model=FCP7XMLResponse)
async def generate_fcp7_xml_endpoint(request: FCP7XMLRequest):
    """
    Generate FCP7 XML file for Premiere Pro import
    
    Args:
        request: FCP7XMLRequest containing timeline path and optional output path
        
    Returns:
        FCP7XMLResponse with XML file path
    """
    try:
        # Validate timeline file exists
        if not os.path.exists(request.timeline_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Timeline file not found: {request.timeline_path}"
            )
        
        # Determine output path
        if request.output_path:
            output_path = request.output_path
        else:
            # Generate default output path
            timeline_dir = os.path.dirname(request.timeline_path)
            output_path = os.path.join(timeline_dir, "highlight_timeline.xml")
        
        # Generate FCP7 XML
        xml_path = generate_fcp7_xml(request.timeline_path, output_path)
        
        return FCP7XMLResponse(
            ok=True,
            xml_path=xml_path
        )
        
    except Exception as e:
        error_msg = f"FCP7 XML generation error: {str(e)}"
        print(f"❌ FCP7 XML generation exception: {type(e).__name__}: {e}")
        return FCP7XMLResponse(ok=False, error=error_msg)


@app.get("/health")
async def health_check():
    """Detailed health check including FFmpeg availability"""
    return {
        "status": "healthy" if ffmpeg_available else "unhealthy",
        "ffmpeg_available": ffmpeg_available,
        "ffmpeg_version": ffmpeg_version,
        "ffmpeg_path": ffmpeg_path,
        "ffprobe_path": ffprobe_path,
        "installation_instructions": FFmpegChecker.get_installation_instructions() if not ffmpeg_available else None
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint for connection testing"""
    return {"message": "pong", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ClipSense Worker")
    parser.add_argument("--once", action="store_true", help="Run once and exit after first request (for testing)")
    parser.add_argument("--port", type=int, help="Override port from environment")
    args = parser.parse_args()
    
    # Use command line port override if provided
    if args.port:
        Config.WORKER_PORT = args.port
    
    # Find available port
    port = find_available_port(Config.WORKER_PORT, Config.MAX_PORT_RETRIES)
    
    if port is None:
        print(f"❌ Could not find an available port after {Config.MAX_PORT_RETRIES} attempts")
        print(f"   Tried ports {Config.WORKER_PORT} to {Config.WORKER_PORT + Config.MAX_PORT_RETRIES - 1}")
        print("   Please free up a port or change the configuration")
        exit(1)
    
    if port != Config.WORKER_PORT:
        print(f"⚠️  Port {Config.WORKER_PORT} was occupied, using port {port}")
        print(f"   Update your frontend configuration to use port {port}")
    
    print(f"🚀 Starting ClipSense worker on {Config.WORKER_HOST}:{port}")
    print(f"   Health check: http://{Config.WORKER_HOST}:{port}/health")
    print(f"   API docs: http://{Config.WORKER_HOST}:{port}/docs")
    
    if args.once:
        print("🧪 Running in test mode (--once)")
        # For test mode, we'll run normally and let the test framework handle shutdown
        uvicorn.run(app, host=Config.WORKER_HOST, port=port)
    else:
        uvicorn.run(app, host=Config.WORKER_HOST, port=port)
