# ClipSense - Local Video Highlight Generator

A privacy-first desktop MVP app that automatically creates highlight videos from multiple clips with music overlay. Built with Tauri + React frontend and Python FastAPI backend.

## Features

- 🎬 Drag-drop multiple video clips
- 🎵 Select one music track with **intelligent beat detection**
- ⚡ Auto-generate highlight videos with **perfect musical timing**
- 🎼 **Music start detection** - no more awkward silence
- 🎯 **Bar-synced cuts** - clips start exactly on musical beats
- 🎨 **Visual Intelligence** - smart content selection and quality analysis
- 👥 **Face detection** - prioritize clips with people
- 📊 **Quality scoring** - brightness, contrast, stability analysis
- 🎞️ **Premiere Pro integration** - FCP7 XML export
- 🔒 100% local processing - no cloud, no login
- 🎨 Modern dark UI with Tailwind CSS

## Architecture

- **Frontend**: Tauri + React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI worker with advanced music analysis
- **Media Engine**: FFmpeg + ffprobe CLI calls
- **Beat Detection**: librosa-based tempo and bar detection
- **Visual Intelligence**: OpenCV-based content analysis and quality scoring
- **Communication**: localhost:8123 API calls

## Quick Start

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.8+
- FFmpeg and ffprobe installed on your system
- **librosa** and **soundfile** for advanced music analysis

### FFmpeg Installation

**macOS:**

```bash
# Using Homebrew (recommended)
brew install ffmpeg

# Verify installation
ffmpeg -version
```

**Windows:**

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Restart your terminal/command prompt
5. Verify with: `ffmpeg -version`

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install ffmpeg
ffmpeg -version
```

**Linux (CentOS/RHEL):**

```bash
sudo yum install ffmpeg
# or for newer versions:
sudo dnf install ffmpeg
```

**Linux (Arch):**

```bash
sudo pacman -S ffmpeg
```

**Snap (Universal):**

```bash
sudo snap install ffmpeg
```

### Installation

1. **Clone and setup backend:**

   ```bash
   cd worker
   pip install -r requirements.txt
   ```

2. **Setup frontend:**
   ```bash
   cd app
   pnpm install
   ```

### Development

1. **Start the Python worker:**

   ```bash
   cd worker
   uvicorn main:app --port 8123 --reload
   ```

2. **Start the Tauri app (in new terminal):**

   ```bash
   cd app
   pnpm tauri dev
   ```

3. **Use the app:**
   - Click "Pick Clips" to select multiple video files
   - Click "Pick Music" to select one audio file
   - Click "Auto-Cut" to generate your highlight video
   - The result will be saved and the path displayed

## Project Structure

```
clipsense2/
├── app/                    # Tauri + React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── types/         # TypeScript types
│   │   └── main.tsx       # App entry point
│   ├── src-tauri/         # Tauri configuration
│   └── package.json
├── worker/                 # Python FastAPI backend
│   ├── main.py           # FastAPI app and endpoints
│   ├── simple_beat_detector.py # Music analysis engine
│   ├── video_processor.py # Video processing pipeline
│   ├── fcp7_xml_generator.py # Premiere Pro export
│   ├── timeline.py       # Timeline artifact management
│   ├── config.py         # Configuration settings
│   └── requirements.txt  # Python dependencies
├── tests/                 # Test suite
│   ├── test_autocut_e2e.py # E2E tests
│   ├── e2e_assets.py     # Synthetic media generation
│   ├── conftest.py       # Test configuration
│   └── README.md         # Test documentation
├── shared/                # Shared types/schemas
├── README.md             # This file
├── TECHNICAL_DOCS.md     # Comprehensive technical documentation
├── DEBUG_GUIDE.md        # Debugging and troubleshooting guide
└── CHANGELOG.md          # Version history and changes
```

## 🎵 Advanced Music Features

### Intelligent Beat Detection

ClipSense automatically analyzes your music to create perfectly timed highlights:

- **🎼 Tempo Detection**: Uses librosa to detect BPM with high accuracy
- **🎯 Bar Detection**: Identifies 4/4 time signature and musical bars
- **🎵 Music Start Detection**: Finds when music actually begins (not silence)
- **⚡ Perfect Sync**: Video clips start exactly on musical beats

### Music Analysis Process

1. **Audio Analysis**: Converts music to WAV format for optimal processing
2. **Tempo Estimation**: Uses multiple algorithms to detect BPM (60-200 range)
3. **Beat Tracking**: Identifies individual beats with confidence scoring
4. **Bar Detection**: Groups beats into 4/4 bars for natural cut points
5. **Start Detection**: Finds actual musical content start (not intro silence)
6. **Grid Alignment**: Aligns all timing to a consistent musical grid

### Premiere Pro Integration

Generate professional editing files:

- **FCP7 XML Export**: Import directly into Premiere Pro
- **Timeline Artifacts**: Complete timing data with bar markers
- **Reproducible Edits**: SHA256 hashes for consistent results

## How It Works

ClipSense uses a **two-stage pipeline** for reliable, high-quality video processing:

### Stage 1: Assemble (Fast Proxy)

1. **File Selection**: User selects video clips and music track via file picker
2. **Proxy Creation**: Backend creates 720p proxies for fast processing
3. **Timeline Generation**: Creates deterministic `timeline.json` with precise timecodes
4. **Proxy Output**: Fast preview video (`highlight_proxy.mp4`) for immediate feedback

### Stage 2: Conform (Master Quality)

1. **Timeline Processing**: Uses `timeline.json` to re-render from original sources
2. **Precise Cutting**: Uses `-accurate_seek` for frame-accurate cuts
3. **High Quality**: Re-encodes with better settings (CRF 18, medium preset)
4. **Master Output**: Final high-quality video (`highlight_master.mp4`)

### Timeline Artifacts

Each processing run generates a `timeline.json` file containing:

- **Clip Data**: Array of clips with absolute paths and precise timecodes
- **Metadata**: FPS, target duration, music path, processing flags
- **Hashes**: SHA256 of timeline and source file fingerprints
- **Reproducibility**: Deterministic output for consistent results

Example timeline structure:

```json
{
  "clips": [
    {
      "src": "/absolute/path/clip1.mp4",
      "in": 12.040,
      "out": 17.120
    }
  ],
  "fps": 25,
  "target_seconds": 60,
  "music": "/absolute/path/music.wav",
  "timeline_hash": "abc123...",
  "source_hashes": {...}
}
```

## Requirements

- FFmpeg must be installed and available in PATH
- Supported video formats: MP4, MOV, AVI, MKV
- Supported audio formats: MP3, WAV, M4A, AAC

## Configuration

### Port Configuration

The default port is 8123, but you can change it:

**Backend (Python):**

```bash
# Set environment variable
export WORKER_PORT=8124

# Or create a .env file in worker/ directory
echo "WORKER_PORT=8124" > worker/.env
```

**Frontend (React):**

```bash
# Set environment variable
export VITE_API_BASE_URL=http://127.0.0.1:8124

# Or create a .env file in app/ directory
echo "VITE_API_BASE_URL=http://127.0.0.1:8124" > app/.env
```

### Performance Tuning

**FFmpeg Settings:**

- Proxy quality: Set `FFMPEG_CRF` in `worker/config.py` (lower = better quality, higher = faster)
- Audio bitrate: Set `FFMPEG_AUDIO_BITRATE` in `worker/config.py`
- Preset: Set `FFMPEG_PRESET` (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)

**Debug Logging:**

```bash
# Enable debug logs
export VITE_ENABLE_DEBUG_LOGS=true
export ENABLE_TIMING_LOGS=true
```

## API Reference

### Endpoints

**POST `/autocut`** - Create highlight video (assemble stage)

```json
{
  "clips": ["/path/clip1.mp4", "/path/clip2.mp4"],
  "music": "/path/music.wav",
  "target_seconds": 60
}
```

Response:

```json
{
  "ok": true,
  "proxy_output": "/path/highlight_proxy.mp4",
  "timeline_path": "/path/timeline.json",
  "timeline_hash": "abc123...",
  "proxy_time": 2.5,
  "render_time": 1.2
}
```

**POST `/conform`** - Create master quality video from timeline

```json
{
  "timeline_path": "/path/timeline.json",
  "out": "/path/highlight_master.mp4",
  "music": "/path/music.wav",
  "no_audio": false
}
```

Response:

```json
{
  "ok": true,
  "master_output": "/path/highlight_master.mp4",
  "conform_time": 4.2
}
```

**POST `/analyze_music`** - Analyze music for tempo and beats

```json
{
  "music_path": "/path/music.wav",
  "target_duration": 60
}
```

Response:

```json
{
  "ok": true,
  "tempo": 103.4,
  "beat_times": [0.0, 0.58, 1.16, ...],
  "bar_times": [0.0, 2.32, 4.64, ...],
  "bars_per_minute": 25.8,
  "beats_per_bar": 4,
  "time_signature": "4/4",
  "analysis_duration": 1.5
}
```

**POST `/generate_fcp7_xml`** - Generate Premiere Pro FCP7 XML

```json
{
  "timeline_path": "/path/timeline.json",
  "output_path": "/path/highlight_timeline.xml"
}
```

Response:

```json
{
  "ok": true,
  "xml_path": "/path/highlight_timeline.xml"
}
```

**POST `/analyze_visual`** - Analyze video content for visual quality

```json
{
  "video_path": "/path/video.mp4",
  "sample_rate": 1.0
}
```

Response:

```json
{
  "ok": true,
  "clip_path": "/path/video.mp4",
  "duration": 10.0,
  "face_count": 2,
  "face_confidence": 0.8,
  "motion_score": 0.3,
  "brightness_score": 0.9,
  "contrast_score": 0.7,
  "stability_score": 0.8,
  "overall_quality": 0.75,
  "best_moments": [1.2, 3.4, 5.6],
  "analysis_duration": 1.2
}
```

### Command Line Interface

Process timeline files offline:

```bash
# Basic conform
python -m worker.cli --timeline timeline.json --out output.mp4

# Override music
python -m worker.cli --timeline timeline.json --out output.mp4 --music new_music.wav

# Video only (no audio)
python -m worker.cli --timeline timeline.json --out output.mp4 --no-audio

# Custom temp directory
python -m worker.cli --timeline timeline.json --out output.mp4 --temp-dir /tmp/custom
```

## Testing

### Quick Test

Run the complete E2E test suite:

```bash
pnpm run test:e2e
```

This will:

1. Generate synthetic test media using FFmpeg
2. Start the Python worker
3. Run comprehensive tests including timeline and conform stages
4. Clean up temporary files

### Test Options

```bash
# Generate test assets only
pnpm run test:e2e:assets

# Run tests with CI-friendly output
pnpm run test:e2e:ci

# Run specific test
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_autocut_processing -v

# Test timeline generation
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_timeline_generation -v

# Test conform stage
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_conform_stage -v
```

### Test Documentation

See [tests/README.md](tests/README.md) for detailed testing information including:

- Test structure and coverage
- Debugging failed tests
- Performance expectations
- CI/CD integration

## Troubleshooting

### System Verification

Run the built-in test script:

```bash
python test_setup.py
```

### Common Issues

**FFmpeg not found:**

- Ensure FFmpeg is installed and in PATH: `ffmpeg -version`
- Check installation instructions above for your platform
- Restart the worker after installing FFmpeg

**Port already in use:**

- The worker will automatically try ports 8123, 8124, 8125
- Check what's using the port: `lsof -i :8123` (macOS/Linux) or `netstat -ano | findstr :8123` (Windows)
- Kill the process or change the port configuration

**Backend connection failed:**

- Ensure the Python worker is running: `cd worker && python run_dev.py`
- Check the worker logs for errors
- Verify the API URL in frontend configuration

**Video processing fails:**

- Check file permissions for video/audio files
- Ensure supported formats: MP4, MOV, AVI, MKV for video; MP3, WAV, M4A, AAC for audio
- Check available disk space (processing creates temporary files)
- Look for detailed error messages in the UI or worker logs

**Performance issues:**

- Use faster FFmpeg presets (ultrafast, superfast)
- Reduce video resolution or quality settings
- Close other resource-intensive applications
- Check system resources (CPU, RAM, disk space)

### Debug Information

**Worker Health Check:**

```bash
curl http://127.0.0.1:8123/health
```

**Check Temporary Files:**

- macOS/Linux: `/tmp/clipsense_*`
- Windows: `%TEMP%\clipsense_*`

**Log Locations:**

- Frontend: Browser console (F12)
- Backend: Terminal output where worker is running

## 📚 Documentation Quick Reference

### Core Documentation

- **[README.md](README.md)** - This file, getting started and basic usage
- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Comprehensive technical architecture
- **[DEBUG_GUIDE.md](DEBUG_GUIDE.md)** - Debugging and troubleshooting
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Key Files

- **`worker/simple_beat_detector.py`** - Music analysis engine
- **`worker/video_processor.py`** - Video processing pipeline
- **`worker/fcp7_xml_generator.py`** - Premiere Pro export
- **`tests/test_autocut_e2e.py`** - E2E test suite

### Quick Commands

```bash
# Start development
cd worker && uvicorn main:app --port 8123 --reload &
cd app && pnpm tauri dev

# Run tests
pnpm run test:e2e

# Check system health
curl http://127.0.0.1:8123/ping

# Analyze music
curl -X POST http://127.0.0.1:8123/analyze_music \
  -H "Content-Type: application/json" \
  -d '{"music_path": "/path/music.wav", "target_duration": 30}'
```

### Common Issues

| Issue                 | Quick Fix                                |
| --------------------- | ---------------------------------------- |
| Music starts at 0.0s  | Check music start detection logs         |
| Clips not synced      | Verify beat detection accuracy           |
| FFmpeg errors         | Check file formats and permissions       |
| API connection failed | Verify worker is running on correct port |

## 🚀 Future Development Roadmap

### 🎯 Current State Analysis

**✅ What's Working Well:**

- Robust beat detection with music start detection
- Perfect bar-synced video timing
- Premiere Pro integration (FCP7 XML)
- Two-stage pipeline (assemble + conform)
- Comprehensive testing suite
- Professional-quality output

### 🚀 Next Level Opportunities

#### 1. 🎨 Visual Intelligence & Scene Detection

**Impact: HIGH | Effort: MEDIUM**

- **Smart Scene Detection**: Analyze video content to find the most interesting moments (faces, action, emotion)
- **Content-Aware Cuts**: Cut on visual beats (camera movements, subject changes) not just musical beats
- **Emotion Detection**: Prioritize clips with smiles, laughter, key moments
- **Quality Scoring**: Rank clips by visual quality (stability, lighting, composition)

#### 2. 🎵 Advanced Music Analysis

**Impact: HIGH | Effort: MEDIUM**

- **Dynamic Tempo Detection**: Handle tempo changes within songs
- **Genre-Specific Timing**: Different cut patterns for different music styles
- **Energy Mapping**: Match high-energy video to high-energy music sections
- **Key Detection**: Musical key changes for dramatic effect

#### 3. 🎬 Professional Video Features

**Impact: HIGH | Effort: MEDIUM-HIGH**

- **Transitions**: Smart crossfades, dissolves, wipes between clips
- **Color Grading**: Automatic color correction and style matching
- **Stabilization**: Fix shaky footage automatically
- **Aspect Ratio Handling**: Smart cropping for different output formats

#### 4. 🤖 AI-Powered Content Selection

**Impact: VERY HIGH | Effort: HIGH**

- **Face Recognition**: Prioritize clips with specific people
- **Object Detection**: Find clips with wedding rings, cake, dancing
- **Sentiment Analysis**: Detect emotional moments
- **Story Arc**: Create narrative flow (ceremony → reception → party)

#### 5. 🎛️ User Control & Customization

**Impact: MEDIUM | Effort: MEDIUM**

- **Style Presets**: "Romantic", "Energetic", "Cinematic", "Documentary"
- **Manual Override**: Let users adjust timing, select specific clips
- **Preview System**: Real-time preview before final render
- **Batch Processing**: Handle multiple projects at once

### 🎯 Recommended Next Steps

**Phase 1: Smart Scene Detection**

- Analyze each video clip for interesting moments
- Score clips by visual quality and content
- Cut to the best moments within each bar interval
- Add face detection to prioritize people

**Phase 2: Content-Aware Timing**

- Match visual energy to musical energy
- Add transitions between clips
- Implement basic color correction

**Why Start with Visual Intelligence:**

- **Immediate Impact**: Videos will look much more professional
- **Builds on Existing**: Enhances our current beat detection
- **User Value**: Clear improvement in output quality
- **Technical Feasibility**: We can use OpenCV + existing Python stack
