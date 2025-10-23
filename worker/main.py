"""
ClipSense FastAPI Backend Worker

Handles video processing requests from the Tauri frontend.
Creates highlight videos by trimming, concatenating clips and overlaying music.
"""

import os
import asyncio
import tempfile
import subprocess
import json
import time
import socket
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
try:
    # Try relative imports first (when run as module)
    from .video_processor import VideoProcessor
    from .conform import ConformProcessor
    from .config import Config
    from .ffmpeg_checker import FFmpegChecker
    from .simple_beat_detector import SimpleBeatDetector
    from .fcp7_xml_generator import generate_fcp7_xml
    from .visual_analyzer import VisualAnalyzer
    from .ai_content_selector import AIContentSelector
    from .ai_story_narrative import StoryNarrative
    from .background_processor import background_processor, ProcessingStatus
except ImportError:
    # Fall back to absolute imports (when run directly)
    from video_processor import VideoProcessor
    from conform import ConformProcessor
    from config import Config
    from ffmpeg_checker import FFmpegChecker
    from simple_beat_detector import SimpleBeatDetector
    from fcp7_xml_generator import generate_fcp7_xml
    from visual_analyzer import VisualAnalyzer
    from ai_content_selector import AIContentSelector
    from ai_story_narrative import StoryNarrative
    from background_processor import background_processor, ProcessingStatus

# Global state
ffmpeg_available = False
ffmpeg_path = None
ffprobe_path = None
ffmpeg_version = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Thumbnail directory
THUMBNAIL_DIR = "/tmp/clipsense_thumbnails"
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

def check_port_availability(host: str, port: int) -> bool:
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

async def generate_thumbnail(video_path: str) -> Optional[str]:
    """Generate a thumbnail for a video clip and return the URL path"""
    try:
        # Create a unique filename based on the video path
        import hashlib
        video_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
        thumbnail_filename = f"thumb_{video_hash}.jpg"
        thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
        
        # Check if thumbnail already exists
        if os.path.exists(thumbnail_path):
            return f"/thumbnails/{thumbnail_filename}"
        
        # Generate thumbnail using ffmpeg
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0",  # Start at beginning
            "-i", video_path,
            "-frames:v", "1",  # Extract 1 frame
            "-q:v", "2",  # High quality
            "-vf", "scale=320:180",  # Resize to thumbnail size
            thumbnail_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0 and os.path.exists(thumbnail_path):
            return f"/thumbnails/{thumbnail_filename}"
        else:
            print(f"Thumbnail generation failed for {video_path}: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"Error generating thumbnail for {video_path}: {e}")
        return None

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

# Mount static files for thumbnails and videos
app.mount("/thumbnails", StaticFiles(directory=THUMBNAIL_DIR), name="thumbnails")

# Serve video files from export directory
EXPORT_DIR = "/Users/anastasiosk/Documents/devprojects/OS/clipsense2/tests/testwedding/Export"
app.mount("/videos", StaticFiles(directory=EXPORT_DIR), name="videos")

# Initialize video processor
video_processor = VideoProcessor()

class AutoCutRequest(BaseModel):
    """Request model for auto-cut processing"""
    clips: List[str]
    music: str
    target_seconds: int = 60
    quality_settings: Optional[Dict[str, Any]] = None
    story_style: Optional[str] = 'traditional'
    style_preset: Optional[str] = 'romantic'
    use_ai_selection: Optional[bool] = False

class AutoCutResponse(BaseModel):
    """Response model for auto-cut processing"""
    ok: bool
    output: Optional[str] = None  # Changed from export_output to match frontend
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


class VisualAnalysisRequest(BaseModel):
    """Request model for visual analysis"""
    video_path: str
    sample_rate: float = 1.0


class VisualAnalysisResponse(BaseModel):
    """Response model for visual analysis"""
    ok: bool
    clip_path: Optional[str] = None
    duration: Optional[float] = None
    face_count: Optional[int] = None
    face_confidence: Optional[float] = None
    motion_score: Optional[float] = None
    brightness_score: Optional[float] = None
    contrast_score: Optional[float] = None
    stability_score: Optional[float] = None
    overall_quality: Optional[float] = None
    best_moments: Optional[List[float]] = None
    analysis_duration: Optional[float] = None
    error: Optional[str] = None

class AISelectionRequest(BaseModel):
    """Request model for AI content selection"""
    clips: List[str]
    music_path: str
    target_duration: int = 60
    story_style: str = 'traditional'
    style_preset: str = 'romantic'
    use_ai_selection: bool = True

class AISelectionResponse(BaseModel):
    """Response model for AI content selection"""
    ok: bool
    proxy_output: Optional[str] = None
    timeline_path: Optional[str] = None
    timeline_hash: Optional[str] = None
    proxy_time: Optional[float] = None
    render_time: Optional[float] = None
    total_time: Optional[float] = None
    selected_clips: Optional[List[Dict[str, Any]]] = None
    story_breakdown: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Background Processing Models
class BackgroundJobRequest(BaseModel):
    """Request model for background processing"""
    clips: List[str]
    music_path: str
    target_duration: int = 60
    story_style: str = 'traditional'
    style_preset: str = 'romantic'

class StoryNarrativeRequest(BaseModel):
    """Request model for story narrative generation"""
    clips: List[str]
    narrative_style: str = 'modern'
    target_duration: float = 60.0

class BackgroundJobResponse(BaseModel):
    """Response model for background job creation"""
    ok: bool
    job_id: Optional[str] = None
    error: Optional[str] = None

class JobStatusResponse(BaseModel):
    """Response model for job status"""
    ok: bool
    job_id: str
    status: str
    progress: float
    current_step: str
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

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
    
    print(f"🎬 AutoCut request received:")
    print(f"  - Clips: {request.clips}")
    print(f"  - Music: {request.music}")
    print(f"  - Target duration: {request.target_seconds}s")
    print(f"  - Use AI selection: {getattr(request, 'use_ai_selection', 'Not provided')}")
    
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
        
        response = AutoCutResponse(
            ok=True,
            output=result.get("export_output"),  # Map export_output to output field
            proxy_time=result.get("proxy_time"),
            render_time=result.get("render_time"),
            total_time=total_time
        )
        
        print(f"🎬 AutoCut response:")
        print(f"  - ok: {response.ok}")
        print(f"  - output: {response.output}")
        print(f"  - proxy_time: {response.proxy_time}")
        print(f"  - render_time: {response.render_time}")
        print(f"  - total_time: {response.total_time}")
        
        return response
        
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


@app.post("/analyze_visual", response_model=VisualAnalysisResponse)
async def analyze_visual_endpoint(request: VisualAnalysisRequest):
    """
    Analyze video content for visual quality and interesting moments
    
    Args:
        request: VisualAnalysisRequest containing video path and sample rate
        
    Returns:
        VisualAnalysisResponse with visual analysis results
    """
    try:
        # Validate video file exists
        if not os.path.exists(request.video_path):
            raise HTTPException(
                status_code=400, 
                detail=f"Video file not found: {request.video_path}"
            )
        
        # Perform visual analysis
        analyzer = VisualAnalyzer()
        result = await analyzer.analyze_clip(request.video_path, request.sample_rate)
        
        return VisualAnalysisResponse(
            ok=True,
            clip_path=result.clip_path,
            duration=result.duration,
            face_count=result.face_count,
            face_confidence=result.face_confidence,
            motion_score=result.motion_score,
            brightness_score=result.brightness_score,
            contrast_score=result.contrast_score,
            stability_score=result.stability_score,
            overall_quality=result.overall_quality,
            best_moments=result.best_moments,
            analysis_duration=result.analysis_duration
        )
        
    except Exception as e:
        error_msg = f"Visual analysis error: {str(e)}"
        print(f"❌ Visual analysis exception: {type(e).__name__}: {e}")
        return VisualAnalysisResponse(ok=False, error=error_msg)

@app.post("/ai_autocut_simple")
async def ai_autocut_simple_endpoint(request: AISelectionRequest):
    """Simple AI endpoint for testing"""
    print(f"🧪 Simple AI endpoint called with {len(request.clips)} clips")
    try:
        # Just return a simple response
        return {
            "ok": True,
            "message": "Simple AI endpoint working",
            "clips": len(request.clips),
            "music": request.music_path
        }
    except Exception as e:
        print(f"❌ Simple AI endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return {"ok": False, "error": str(e)}

@app.post("/ai_autocut_test")
async def ai_autocut_test_endpoint(request: AISelectionRequest):
    """Test endpoint for AI autocut"""
    print(f"🧪 AI test endpoint called with {len(request.clips)} clips")
    return {"ok": True, "message": "AI test endpoint working", "clips": len(request.clips)}

@app.post("/ai_autocut", response_model=AISelectionResponse)
async def ai_autocut_endpoint(request: AISelectionRequest):
    """
    AI-powered autocut endpoint with intelligent content selection
    
    Args:
        request: AISelectionRequest containing clips, music, and AI parameters
        
    Returns:
        AISelectionResponse with AI-selected clips and analysis
    """
    print(f"🚀 AI autocut endpoint called with {len(request.clips)} clips")
    print(f"🔍 Request details: clips={request.clips}, music={request.music_path}, duration={request.target_duration}")
    try:
        # Validate inputs
        if not request.clips:
            print("❌ No clips provided")
            raise HTTPException(status_code=400, detail="No clips provided")
        
        if not os.path.exists(request.music_path):
            print(f"❌ Music file not found: {request.music_path}")
            raise HTTPException(status_code=400, detail=f"Music file not found: {request.music_path}")
        
        # Validate clip files
        for clip_path in request.clips:
            if not os.path.exists(clip_path):
                print(f"❌ Clip file not found: {clip_path}")
                raise HTTPException(status_code=400, detail=f"Clip file not found: {clip_path}")
        
        print(f"✅ Validation passed")
        print(f"🤖 AI Autocut request: {len(request.clips)} clips, {request.target_duration}s, {request.story_style}/{request.style_preset}")
        
        # Process with AI selection
        processor = VideoProcessor()
        result = await processor.assemble_with_ai_selection(
            clips=request.clips,
            music_path=request.music_path,
            target_duration=request.target_duration,
            story_style=request.story_style,
            style_preset=request.style_preset,
            use_ai_selection=request.use_ai_selection
        )
        
        print(f"🔍 AI result: {result}")
        print(f"🔍 AI result type: {type(result)}")
        print(f"🔍 AI result ok: {result.get('ok', 'MISSING')}")
        
        if not result.get("ok", False):
            return AISelectionResponse(ok=False, error=result.get("error", "Unknown error"))
        
        # Get AI analysis if available
        print("🤖 Getting AI analysis...")
        ai_selector = AIContentSelector()
        selected_clips = []
        story_breakdown = {}
        quality_metrics = {}
        
        if request.use_ai_selection:
            try:
                print("🎯 Calling AI selector...")
                print(f"🎯 Request clips: {request.clips}")
                print(f"🎯 Target count: {len(request.clips)}")
                print(f"🎯 Story style: {request.story_style}")
                print(f"🎯 Style preset: {request.style_preset}")
                
                # Get AI analysis for selected clips
                ai_results = await ai_selector.select_best_clips(
                    request.clips,
                    target_count=len(request.clips),
                    story_style=request.story_style,
                    style_preset=request.style_preset
                )
                print(f"✅ AI selector returned {len(ai_results)} results")
                
                # Debug: Check if descriptions are present
                for i, ai_result in enumerate(ai_results):
                    print(f"🔍 Result {i+1}: description='{ai_result.description[:50] if ai_result.description else 'None'}...'")
                    print(f"🔍 Result {i+1}: has description field: {hasattr(ai_result, 'description')}")
                    print(f"🔍 Result {i+1}: description type: {type(ai_result.description)}")
                    print(f"🔍 Result {i+1}: description value: {repr(ai_result.description)}")
                
                # Format selected clips info
                selected_clips = []
                for ai_result in ai_results:
                    # Debug each result
                    print(f"🔍 Processing AI result: {ai_result.clip_path}")
                    print(f"🔍 Description: {repr(ai_result.description)}")
                    print(f"🔍 Has description attr: {hasattr(ai_result, 'description')}")
                    
                    # Generate thumbnail for this clip
                    thumbnail_path = await generate_thumbnail(ai_result.clip_path)
                    
                    selected_clips.append({
                        "path": ai_result.clip_path,
                        "score": ai_result.final_score,
                        "scene": ai_result.story_arc.scene_classification,
                        "tone": ai_result.story_arc.emotional_tone,
                        "importance": ai_result.story_arc.story_importance,
                        "reason": ai_result.selection_reason,
                        "description": ai_result.description if hasattr(ai_result, 'description') and ai_result.description else "Description not available",
                        "thumbnail_path": thumbnail_path,
                        "object_analysis": {
                            "key_moments": ai_result.object_analysis.key_moments,
                            "scene_classification": ai_result.object_analysis.scene_classification,
                            "objects_detected": ai_result.object_analysis.objects_detected
                        },
                        "story_arc": {
                            "scene_classification": ai_result.story_arc.scene_classification,
                            "emotional_tone": ai_result.story_arc.emotional_tone,
                            "story_importance": ai_result.story_arc.story_importance
                        }
                    })
                
                # Get story breakdown
                story_breakdown = {
                    "scenes": {},
                    "tones": {},
                    "positions": {},
                    "total_clips": len(ai_results)
                }
                
                for ai_result in ai_results:
                    scene = ai_result.story_arc.scene_classification
                    tone = ai_result.story_arc.emotional_tone
                    position = ai_result.story_arc.narrative_position
                    
                    story_breakdown["scenes"][scene] = story_breakdown["scenes"].get(scene, 0) + 1
                    story_breakdown["tones"][tone] = story_breakdown["tones"].get(tone, 0) + 1
                    story_breakdown["positions"][position] = story_breakdown["positions"].get(position, 0) + 1
                
                # Calculate quality metrics
                scores = []
                story_importances = []
                for ai_result in ai_results:
                    scores.append(ai_result.final_score)
                    story_importances.append(ai_result.story_arc.story_importance)
                
                quality_metrics = {
                    "average_score": sum(scores) / len(scores) if scores else 0,
                    "max_score": max(scores) if scores else 0,
                    "min_score": min(scores) if scores else 0,
                    "high_quality_clips": len([s for s in scores if s > 0.7]),
                    "story_importance_avg": sum(story_importances) / len(story_importances) if story_importances else 0
                }
                
            except Exception as e:
                print(f"⚠️ AI analysis failed: {e}")
                import traceback
                traceback.print_exc()
                # Continue without AI analysis
        
        return AISelectionResponse(
            ok=True,
            proxy_output=result.get("proxy_output"),
            timeline_path=result.get("timeline_path"),
            timeline_hash=result.get("timeline_hash"),
            proxy_time=result.get("proxy_time"),
            render_time=result.get("render_time"),
            total_time=result.get("total_time"),
            selected_clips=selected_clips,
            story_breakdown=story_breakdown,
            quality_metrics=quality_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"AI autocut error: {str(e)}"
        print(f"❌ AI autocut exception: {type(e).__name__}: {e}")
        print(f"❌ Exception details: {repr(e)}")
        import traceback
        traceback.print_exc()
        return AISelectionResponse(ok=False, error=error_msg)


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

@app.post("/clear_cache")
async def clear_analysis_cache():
    """Clear the AI analysis cache to force fresh analysis"""
    try:
        if 'ai_selector' in globals():
            ai_selector.clear_cache()
            return {"status": "success", "message": "Analysis cache cleared"}
        else:
            return {"status": "error", "message": "AI selector not initialized"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to clear cache: {str(e)}"}


# Background Processing Endpoints
@app.post("/preview/start", response_model=BackgroundJobResponse)
async def preview_start(request: AutoCutRequest):
    """Compatibility preview start endpoint mapping to background job system."""
    try:
        if not request.clips:
            raise HTTPException(status_code=400, detail="No clips provided")
        if not os.path.exists(request.music):
            raise HTTPException(status_code=400, detail=f"Music file not found: {request.music}")

        for clip_path in request.clips:
            if not os.path.exists(clip_path):
                raise HTTPException(status_code=400, detail=f"Clip file not found: {clip_path}")

        job_id = background_processor.create_job(
            clips=request.clips,
            music_path=request.music,
            target_duration=request.target_seconds,
            story_style=request.story_style or 'traditional',
            style_preset=request.style_preset or 'romantic'
        )
        asyncio.create_task(background_processor.start_processing(job_id))
        return BackgroundJobResponse(ok=True, job_id=job_id)
    except HTTPException:
        raise
    except Exception as e:
        return BackgroundJobResponse(ok=False, error=str(e))

@app.get("/preview/status/{job_id}", response_model=JobStatusResponse)
async def preview_status(job_id: str):
    job = background_processor.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    results_dict = None
    if job.results:
        results_dict = [
            {
                "clip_path": r.clip_path,
                "final_score": r.final_score,
                "selection_reason": r.selection_reason,
                "description": r.description,
                "object_analysis": {
                    "key_moments": r.object_analysis.key_moments,
                    "scene_classification": r.object_analysis.scene_classification,
                    "objects_detected": r.object_analysis.objects_detected,
                },
                "story_arc": {
                    "scene_classification": r.story_arc.scene_classification,
                    "emotional_tone": r.story_arc.emotional_tone,
                    "story_importance": r.story_arc.story_importance,
                },
            }
            for r in job.results
        ]
    return JobStatusResponse(
        ok=True,
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        current_step=job.current_step,
        results=results_dict,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
    )

@app.get("/preview/result/{job_id}")
async def preview_result(job_id: str):
    results = background_processor.get_job_results(job_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Job not found or not completed")

    selected_clips = []
    for r in results:
        # Generate thumbnail for this clip
        thumbnail_path = await generate_thumbnail(r.clip_path)
        
        selected_clips.append({
            "path": r.clip_path,
            "score": r.final_score,
            "scene": r.story_arc.scene_classification,
            "tone": r.story_arc.emotional_tone,
            "importance": r.story_arc.story_importance,
            "reason": r.selection_reason,
            "description": r.description,
            "thumbnail_path": thumbnail_path,
            "object_analysis": {
                "key_moments": r.object_analysis.key_moments,
                "scene_classification": r.object_analysis.scene_classification,
                "objects_detected": r.object_analysis.objects_detected,
            },
            "story_arc": {
                "scene_classification": r.story_arc.scene_classification,
                "emotional_tone": r.story_arc.emotional_tone,
                "story_importance": r.story_arc.story_importance,
            },
        })

    # Minimal preview shape expected by UI
    preview = {
        "selected_clips": selected_clips,
        "timeline": [],  # UI will fall back to selected_clips mapping
        "music_analysis": {},
        "story_arc": {
            "total_clips": len(selected_clips),
            "story_flow": [c["scene"] for c in selected_clips],
            "emotional_journey": [c["tone"] for c in selected_clips],
            "key_moments": [],
        },
        "total_duration": 0,
        "target_duration": 0,
    }
    return {"ok": True, "preview": preview}
@app.post("/background/start", response_model=BackgroundJobResponse)
async def start_background_job(request: BackgroundJobRequest):
    """Start a background AI processing job"""
    try:
        # Validate inputs
        if not request.clips:
            raise HTTPException(status_code=400, detail="No clips provided")
        
        if not os.path.exists(request.music_path):
            raise HTTPException(status_code=400, detail=f"Music file not found: {request.music_path}")
        
        # Validate clip files
        for clip_path in request.clips:
            if not os.path.exists(clip_path):
                raise HTTPException(status_code=400, detail=f"Clip file not found: {clip_path}")
        
        # Create background job
        job_id = background_processor.create_job(
            clips=request.clips,
            music_path=request.music_path,
            target_duration=request.target_duration,
            story_style=request.story_style,
            style_preset=request.style_preset
        )
        
        # Start processing in background
        asyncio.create_task(background_processor.start_processing(job_id))
        
        print(f"INFO:main:🚀 Started background job {job_id} for {len(request.clips)} clips")
        
        return BackgroundJobResponse(ok=True, job_id=job_id)
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Failed to start background job: {str(e)}"
        print(f"❌ Background job error: {error_msg}")
        return BackgroundJobResponse(ok=False, error=error_msg)

@app.get("/background/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a background job"""
    job = background_processor.get_job_status(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert results to dict format if available
    results_dict = None
    if job.results:
        results_dict = [
            {
                "clip_path": result.clip_path,
                "final_score": result.final_score,
                "selection_reason": result.selection_reason,
                "story_arc": {
                    "scene_classification": result.story_arc.scene_classification,
                    "emotional_tone": result.story_arc.emotional_tone,
                    "story_importance": result.story_arc.story_importance
                }
            }
            for result in job.results
        ]
    
    return JobStatusResponse(
        ok=True,
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        current_step=job.current_step,
        results=results_dict,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )

@app.post("/background/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running background job"""
    success = background_processor.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or cannot be cancelled")
    
    return {"ok": True, "message": f"Job {job_id} cancelled"}

@app.get("/background/results/{job_id}")
async def get_job_results(job_id: str):
    """Get the results of a completed background job"""
    results = background_processor.get_job_results(job_id)
    
    if results is None:
        raise HTTPException(status_code=404, detail="Job not found or not completed")
    
    # Convert results to dict format
    results_dict = [
        {
            "clip_path": result.clip_path,
            "final_score": result.final_score,
            "selection_reason": result.selection_reason,
            "object_analysis": {
                "key_moments": result.object_analysis.key_moments,
                "scene_classification": result.object_analysis.scene_classification,
                "objects_detected": result.object_analysis.objects_detected
            },
            "story_arc": {
                "scene_classification": result.story_arc.scene_classification,
                "emotional_tone": result.story_arc.emotional_tone,
                "story_importance": result.story_arc.story_importance
            }
        }
        for result in results
    ]
    
    return {"ok": True, "results": results_dict}

@app.post("/generate_story_narrative")
async def generate_story_narrative(request: dict):
    """Generate a complete story narrative from video clips"""
    try:
        video_paths = request.get("clips", [])
        narrative_style = request.get("narrative_style", "modern")
        target_duration = request.get("target_duration", 60.0)
        
        if not video_paths:
            raise HTTPException(status_code=400, detail="No clips provided")
        
        # Validate clip files
        for clip_path in video_paths:
            if not os.path.exists(clip_path):
                raise HTTPException(status_code=400, detail=f"Clip file not found: {clip_path}")
        
        print(f"🎬 Generating {narrative_style} story narrative from {len(video_paths)} clips")
        
        # Generate story narrative
        ai_selector = AIContentSelector()
        story_narrative = await ai_selector.generate_story_narrative(
            video_paths, narrative_style, target_duration
        )
        
        # Convert to dict for JSON response
        story_dict = {
            "story_title": story_narrative.story_title,
            "story_theme": story_narrative.story_theme,
            "narrative_structure": story_narrative.narrative_structure,
            "story_arc": story_narrative.story_arc,
            "selected_clips": [
                {
                    "clip_path": clip.clip_path,
                    "description": clip.description,
                    "scene_type": clip.scene_type,
                    "emotional_tone": clip.emotional_tone,
                    "key_moments": clip.key_moments,
                    "people_count": clip.people_count,
                    "quality_score": clip.quality_score,
                    "timestamp": clip.timestamp
                }
                for clip in story_narrative.selected_clips
            ],
            "narrative_flow": story_narrative.narrative_flow,
            "emotional_journey": story_narrative.emotional_journey,
            "story_duration": story_narrative.story_duration,
            "story_notes": story_narrative.story_notes
        }
        
        print(f"✅ Generated story: '{story_narrative.story_title}'")
        return {"ok": True, "story_narrative": story_dict}
        
    except Exception as e:
        print(f"❌ Story narrative generation failed: {e}")
        return {"ok": False, "error": str(e)}

@app.post("/generate_story_narrative_live")
async def generate_story_narrative_live_endpoint(request: StoryNarrativeRequest):
    """Generate AI story narrative with live WebSocket updates"""
    try:
        print(f"🎬 Live story narrative request: {len(request.clips)} clips, style: {request.narrative_style}")
        
        # Initialize AI components
        ai_selector = AIContentSelector()
        story_generator = AIStoryNarrativeGenerator()
        
        # Progress callback for WebSocket updates
        async def progress_callback(progress_data):
            await manager.broadcast(json.dumps({
                "type": "story_progress",
                "data": progress_data
            }))
        
        # Analyze clips and generate descriptions
        clip_descriptions = []
        for i, video_path in enumerate(request.clips):
            print(f"📹 Analyzing clip: {Path(video_path).name}")
            
            # Send clip analysis progress
            await progress_callback({
                "type": "clip_analysis_started",
                "clip_index": i + 1,
                "total_clips": len(request.clips),
                "clip_name": Path(video_path).name,
                "message": f"Analyzing clip {i + 1}/{len(request.clips)}: {Path(video_path).name}"
            })
            
            try:
                analysis_result = await ai_selector.analyze_clip(video_path, request.narrative_style, 'romantic')
                
                # Create clip description
                clip_description = ClipDescription(
                    clip_path=video_path,
                    description=analysis_result.description,
                    scene_type=analysis_result.story_arc.scene_classification,
                    emotional_tone=analysis_result.story_arc.emotional_tone,
                    key_moments=[str(moment) for moment in analysis_result.object_analysis.key_moments],
                    people_count=analysis_result.object_analysis.people_count,
                    quality_score=analysis_result.final_score,
                    timestamp=0.0
                )
                clip_descriptions.append(clip_description)
                
                # Send clip analysis complete
                await progress_callback({
                    "type": "clip_analysis_complete",
                    "clip_index": i + 1,
                    "total_clips": len(request.clips),
                    "clip_name": Path(video_path).name,
                    "quality_score": analysis_result.final_score,
                    "scene_type": analysis_result.story_arc.scene_classification,
                    "emotional_tone": analysis_result.story_arc.emotional_tone,
                    "message": f"Completed analysis of {Path(video_path).name} (score: {analysis_result.final_score:.2f})"
                })
                
                print(f"✅ Clip description created for {Path(video_path).name}")
            except Exception as e:
                print(f"WARNING:ai_content_selector:Failed to analyze {video_path}: {e}")
                await progress_callback({
                    "type": "clip_analysis_failed",
                    "clip_index": i + 1,
                    "total_clips": len(request.clips),
                    "clip_name": Path(video_path).name,
                    "error": str(e),
                    "message": f"Failed to analyze {Path(video_path).name}: {str(e)}"
                })
                continue
        
        if not clip_descriptions:
            await progress_callback({
                "type": "analysis_failed",
                "message": "No clips could be analyzed for story generation"
            })
            return {"ok": False, "error": "No clips could be analyzed for story generation"}
        
        # Generate story narrative with progress callbacks
        story_narrative = await story_generator.generate_story_narrative(
            clip_descriptions, 
            request.narrative_style, 
            request.target_duration,
            progress_callback
        )
        
        # Send final result
        await progress_callback({
            "type": "story_complete",
            "story_title": story_narrative.story_title,
            "selected_count": len(story_narrative.selected_clips),
            "rejected_count": len(story_narrative.rejected_clips),
            "message": f"Story '{story_narrative.story_title}' completed with {len(story_narrative.selected_clips)} selected clips"
        })
        
        print(f"✅ Generated story: '{story_narrative.story_title}'")
        return {"ok": True, "story_narrative": story_narrative}
        
    except Exception as e:
        print(f"❌ Story narrative generation failed: {e}")
        await manager.broadcast(json.dumps({
            "type": "story_error",
            "error": str(e),
            "message": f"Story generation failed: {str(e)}"
        }))
        return {"ok": False, "error": str(e)}

@app.post("/background/cleanup")
async def cleanup_old_jobs():
    """Clean up old completed jobs"""
    cleaned_count = background_processor.cleanup_old_jobs()
    return {"ok": True, "cleaned_jobs": cleaned_count}

@app.websocket("/ws/live-analysis")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live analysis updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for connection testing
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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
