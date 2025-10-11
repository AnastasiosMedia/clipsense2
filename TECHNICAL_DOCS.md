# ClipSense Technical Documentation

## 🏗️ System Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tauri App     │    │  FastAPI Worker │    │   FFmpeg Engine │
│   (React/TS)    │◄──►│   (Python)      │◄──►│   (CLI Tools)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  File Picker    │    │ Beat Detection  │    │ Video Processing│
│  UI Components  │    │ Music Analysis  │    │ Audio Overlay   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **User Input** → File selection via Tauri dialogs
2. **Music Analysis** → librosa-based beat detection
3. **Video Processing** → FFmpeg proxy generation
4. **Timeline Creation** → Bar-synced clip timing
5. **Final Render** → High-quality output with music overlay

## 🎵 Music Analysis Engine

### SimpleBeatDetector Class

**Location**: `worker/simple_beat_detector.py`

**Key Methods**:

- `analyze_music()` - Main analysis entry point
- `_find_music_start()` - Detect actual music content start
- `_align_to_grid()` - Align beats to consistent tempo grid

**Process Flow**:

1. **Audio Conversion**: Convert to WAV format for librosa compatibility
2. **Music Start Detection**: Use RMS energy analysis to find content start
3. **Tempo Estimation**: librosa beat tracking with confidence scoring
4. **Beat Generation**: Create regular beats based on detected tempo
5. **Bar Detection**: Group beats into 4/4 bars
6. **Grid Alignment**: Align all timing to preserve music start offset

**Key Features**:

- **Music Start Detection**: Finds when music actually begins (not silence)
- **Offset Preservation**: Maintains music start timing through alignment
- **Confidence Scoring**: Provides reliability metrics for all detections
- **Fallback System**: Graceful degradation if advanced methods fail

### Music Analysis Parameters

```python
# Core settings
sample_rate = 22050      # librosa standard
hop_length = 512         # Analysis hop size
time_signature = 4       # 4/4 time signature
min_tempo = 60           # BPM range
max_tempo = 200

# Music start detection
threshold = max_energy * 0.1  # 10% of max energy
min_start = 0.1              # Minimum start time
max_start = 5.0              # Maximum start time
```

## 🎬 Video Processing Pipeline

### Two-Stage Architecture

**Stage 1: Assemble (Fast Proxy)**

- Create 720p proxies for fast processing
- Generate timeline with bar-synced timing
- Output: `highlight_proxy.mp4` + `timeline.json`

**Stage 2: Conform (Master Quality)**

- Re-render from original sources using timeline
- Use `-accurate_seek` for frame-accurate cuts
- Output: `highlight_master.mp4`

### VideoProcessor Class

**Location**: `worker/video_processor.py`

**Key Methods**:

- `process_highlight()` - Main processing entry point
- `_trim_segments_with_bars()` - Bar-synced clip trimming
- `_generate_timeline_data()` - Create timeline artifacts

**Processing Steps**:

1. **Music Analysis** → Detect tempo, beats, bars
2. **Proxy Creation** → Generate 720p proxies
3. **Bar-Synced Trimming** → Cut clips to musical timing
4. **Concatenation** → Combine clips with music overlay
5. **Timeline Generation** → Create reproducible timeline data

## 📊 Timeline Artifacts

### Timeline Structure

**File**: `timeline.json`

```json
{
  "clips": [
    {
      "src": "/absolute/path/clip1.mp4",
      "in": 12.040,
      "out": 17.120
    }
  ],
  "bar_markers": [0.418, 2.740, 5.062, ...],
  "tempo": 103.4,
  "time_signature": "4/4",
  "fps": 25,
  "target_seconds": 60,
  "music": "/absolute/path/music.wav",
  "timeline_hash": "abc123...",
  "source_hashes": {...},
  "used_beat_snapping": true,
  "used_scene_detect": false
}
```

### Key Features

- **Absolute Paths**: All file paths are absolute for portability
- **Precise Timing**: Timecodes to 3 decimal places
- **Bar Markers**: Musical timing reference points
- **Reproducibility**: SHA256 hashes for consistent results
- **Metadata**: Complete processing information

## 🎞️ Premiere Pro Integration

### FCP7 XML Generator

**Location**: `worker/fcp7_xml_generator.py`

**Features**:

- Generates Final Cut Pro 7 XML format
- Compatible with Premiere Pro import
- Preserves all timing and metadata
- Frame-accurate cuts and transitions

**Usage**:

```python
from fcp7_xml_generator import generate_fcp7_xml

xml_path = generate_fcp7_xml(
    timeline_path="timeline.json",
    output_path="highlight_timeline.xml"
)
```

## 🔧 Configuration System

### Environment Variables

**Backend (Python)**:

```bash
WORKER_PORT=8123              # API server port
CLIPSENSE_TMP_DIR=/tmp/custom # Custom temp directory
ENABLE_TIMING_LOGS=true       # Performance logging
```

**Frontend (React)**:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8123
VITE_ENABLE_DEBUG_LOGS=true
```

### FFmpeg Settings

**Location**: `worker/config.py`

```python
FFMPEG_CRF = 28              # Proxy quality (lower = better)
FFMPEG_PRESET = "ultrafast"  # Encoding speed
FFMPEG_AUDIO_BITRATE = "96k" # Audio quality
```

## 🧪 Testing Framework

### E2E Test Suite

**Location**: `tests/`

**Test Structure**:

- `test_autocut_e2e.py` - Main E2E tests
- `e2e_assets.py` - Synthetic media generation
- `conftest.py` - Test configuration and fixtures

**Test Categories**:

- **Short Tests** (≤20s): Quick validation
- **Long Tests** (≥60s): Comprehensive testing
- **Deterministic**: Fixed seeds for reproducible results

**Running Tests**:

```bash
# Quick test suite
pnpm run test:e2e

# All tests
pnpm run test:e2e:all

# Specific test
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_autocut_processing -v
```

## 🐛 Debugging Guide

### Common Issues

**Music Start Detection Fails**:

- Check audio file format (WAV preferred)
- Verify librosa can load the file
- Check RMS energy levels in audio

**Beat Detection Inaccurate**:

- Verify tempo is within 60-200 BPM range
- Check for tempo changes in music
- Review confidence scores in logs

**Video Processing Errors**:

- Verify FFmpeg installation and PATH
- Check file permissions and formats
- Review FFmpeg error messages

**Timeline Generation Issues**:

- Check bar markers alignment
- Verify music start offset preservation
- Review timeline.json structure

### Debug Commands

```bash
# Check system health
curl http://127.0.0.1:8123/ping

# Analyze music file
curl -X POST http://127.0.0.1:8123/analyze_music \
  -H "Content-Type: application/json" \
  -d '{"music_path": "/path/music.wav", "target_duration": 30}'

# Check temporary files
ls -la /tmp/clipsense_*

# View timeline data
cat timeline.json | python3 -m json.tool
```

### Log Analysis

**Backend Logs**:

- Music analysis progress
- Beat detection results
- Video processing steps
- Error messages and stack traces

**Frontend Logs**:

- API call status
- File selection events
- UI state changes
- Error handling

## 📈 Performance Optimization

### Processing Speed

**Proxy Generation**:

- Use faster FFmpeg presets (`ultrafast`, `superfast`)
- Reduce proxy resolution (720p default)
- Lower CRF values for speed

**Music Analysis**:

- Limit analysis duration for long tracks
- Use mono audio for beat detection
- Cache analysis results when possible

**Memory Usage**:

- Process videos in chunks
- Clean up temporary files
- Monitor memory usage during processing

### Quality vs Speed Trade-offs

| Setting   | Speed      | Quality    | Use Case       |
| --------- | ---------- | ---------- | -------------- |
| ultrafast | ⭐⭐⭐⭐⭐ | ⭐⭐       | Quick previews |
| superfast | ⭐⭐⭐⭐   | ⭐⭐⭐     | Development    |
| fast      | ⭐⭐⭐     | ⭐⭐⭐⭐   | Production     |
| medium    | ⭐⭐       | ⭐⭐⭐⭐⭐ | Final output   |

## 🔄 Development Workflow

### Code Organization

```
worker/
├── main.py                 # FastAPI app and endpoints
├── simple_beat_detector.py # Music analysis engine
├── video_processor.py      # Video processing pipeline
├── fcp7_xml_generator.py  # Premiere Pro export
├── timeline.py            # Timeline artifact management
├── config.py              # Configuration settings
└── requirements.txt       # Python dependencies
```

### Adding New Features

1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Implement Changes**: Follow existing code patterns
3. **Add Tests**: Update test suite for new functionality
4. **Update Documentation**: Modify README and technical docs
5. **Test Thoroughly**: Run full E2E test suite
6. **Commit Changes**: Use descriptive commit messages
7. **Create PR**: Document changes and test results

### Code Standards

**Python**:

- Use type hints for all functions
- Follow PEP 8 style guidelines
- Add docstrings for all public methods
- Use async/await for I/O operations

**JavaScript/TypeScript**:

- Use TypeScript for type safety
- Follow React best practices
- Use Tailwind CSS for styling
- Implement proper error handling

## 🚀 Future Enhancements

### Planned Features

#### Phase 1: Visual Intelligence (Recommended Next)
**Impact: HIGH | Effort: MEDIUM**

- **Smart Scene Detection**: OpenCV-based content analysis
- **Face Detection**: Prioritize clips with people
- **Quality Scoring**: Stability, lighting, composition metrics
- **Content-Aware Cuts**: Visual beats + musical beats

**Technical Implementation**:
```python
# New module: worker/visual_analyzer.py
class VisualAnalyzer:
    def analyze_clip(self, video_path: str) -> Dict[str, float]:
        # Face detection, motion analysis, quality scoring
        pass
    
    def find_best_moments(self, clip_path: str, duration: float) -> List[float]:
        # Find most interesting moments within duration
        pass
```

#### Phase 2: Advanced Music Analysis
**Impact: HIGH | Effort: MEDIUM**

- **Dynamic Tempo**: Handle tempo changes within songs
- **Genre Detection**: Different cut patterns per music style
- **Energy Mapping**: Match visual energy to musical energy
- **Key Detection**: Musical key changes for dramatic effect

#### Phase 3: Professional Video Features
**Impact: HIGH | Effort: MEDIUM-HIGH**

- **Transitions**: Smart crossfades, dissolves, wipes
- **Color Grading**: Automatic color correction
- **Stabilization**: Fix shaky footage
- **Aspect Ratio Handling**: Smart cropping

#### Phase 4: AI-Powered Content Selection
**Impact: VERY HIGH | Effort: HIGH**

- **Face Recognition**: Specific people prioritization
- **Object Detection**: Wedding rings, cake, dancing
- **Sentiment Analysis**: Emotional moment detection
- **Story Arc**: Narrative flow creation

### Technical Debt

- [ ] Add comprehensive error handling
- [ ] Implement caching for music analysis
- [ ] Add performance monitoring
- [ ] Create automated testing for edge cases
- [ ] Add support for more audio formats
- [ ] Implement visual analysis caching
- [ ] Add GPU acceleration for video processing
- [ ] Create plugin system for custom analyzers

---

_Last Updated: October 11, 2025_
_Version: 2.0.0 (Advanced Beat Detection)_
