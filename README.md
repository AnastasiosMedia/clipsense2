# ClipSense - AI-Powered Video Highlight Generator

A privacy-first desktop application that automatically creates professional highlight videos from multiple clips with intelligent AI analysis and music overlay. Built with Tauri + React frontend and Python FastAPI backend.

## ✨ Current Features

### 🎬 Core Functionality

- **Drag & Drop Interface**: Intuitive file selection for videos and music
- **AI-Powered Analysis**: Intelligent content selection with object detection and emotion analysis
- **Smart Beat Detection**: Perfect musical timing with bar-synced cuts
- **Video Preview**: In-app video player with custom controls and fullscreen support
- **Storyboard Gallery**: Visual timeline with thumbnail previews
- **Professional Export**: High-quality video output with timeline artifacts

### 🤖 AI Intelligence

- **Object Detection**: Identifies wedding rings, cake, dancing, people, and key moments
- **Emotion Analysis**: Detects romantic, joyful, intimate moments in video clips
- **Scene Classification**: Automatically categorizes clips (ceremony, reception, preparation, etc.)
- **Story Arc Creation**: Generates narrative flow and story importance scoring
- **Content Selection**: AI-powered clip selection with detailed reasoning
- **Thumbnail Generation**: Automatic preview thumbnails for all clips

### 🎨 Modern Interface

- **Dark Mode**: Sophisticated dark theme with elegant styling
- **Responsive Design**: Clean, professional UI with smooth animations
- **Real-time Feedback**: Live processing status and progress tracking
- **Toast Notifications**: User-friendly status updates and error handling
- **Custom Branding**: Integrated ClipSense logo and "Upload. Analyze. Create" tagline

### 🔧 Technical Excellence

- **100% Local Processing**: No cloud, no login, complete privacy
- **Two-Stage Pipeline**: Fast proxy generation + high-quality conform
- **FFmpeg Integration**: Professional video processing with frame-accurate cuts
- **Timeline Artifacts**: Reproducible results with SHA256 hashing
- **Premiere Pro Export**: FCP7 XML generation for professional workflows
- **Comprehensive Testing**: Full E2E test suite with synthetic media generation

## 🏗️ Architecture

### Frontend Stack

- **Tauri**: Cross-platform desktop framework
- **React + TypeScript**: Modern component-based UI
- **Tailwind CSS**: Utility-first styling with custom dark theme
- **Vite**: Fast development and build tooling

### Backend Stack

- **Python FastAPI**: High-performance async API server
- **OpenCV**: Computer vision and image processing
- **librosa**: Advanced music analysis and beat detection
- **FFmpeg**: Professional video/audio processing
- **OpenAI Vision**: AI-powered thumbnail analysis (optional)

### Communication

- **REST API**: Clean HTTP endpoints on localhost:8123
- **WebSocket**: Real-time processing updates (planned)
- **File Serving**: Static file serving for thumbnails and videos

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and **pnpm**
- **Python 3.8+** with pip
- **FFmpeg** and **ffprobe** installed
- **librosa** and **soundfile** for music analysis

### FFmpeg Installation

**macOS:**

```bash
brew install ffmpeg
ffmpeg -version
```

**Windows:**

1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart terminal and verify: `ffmpeg -version`

**Linux (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install ffmpeg
ffmpeg -version
```

### Installation & Development

1. **Setup Backend:**

```bash
cd worker
pip install -r requirements.txt
```

2. **Setup Frontend:**

```bash
cd app
pnpm install
```

3. **Start Development:**

```bash
# Terminal 1: Start Python worker
cd worker
uvicorn main:app --port 8123 --reload

# Terminal 2: Start Tauri app
cd app
pnpm tauri dev
```

4. **Use the App:**
   - Drag & drop video clips or click "Pick Clips"
   - Select music track with "Pick Music"
   - Click "Preview Storyboard" for AI analysis
   - Click "Auto-Cut" to generate highlight video
   - Preview results in-app or open file location

## 📁 Project Structure

```
clipsense2/
├── app/                          # Tauri + React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── FilePicker.tsx   # Drag & drop file selection
│   │   │   ├── StoryboardPreview.tsx # AI analysis modal
│   │   │   ├── VideoPreviewModal.tsx # In-app video player
│   │   │   ├── StoryboardGallery.tsx # Visual timeline
│   │   │   └── ProcessingStatus.tsx # Progress tracking
│   │   ├── services/            # API services
│   │   ├── types/               # TypeScript definitions
│   │   └── main.tsx             # App entry point
│   ├── src-tauri/               # Tauri configuration
│   └── public/                  # Static assets (logos, etc.)
├── worker/                      # Python FastAPI backend
│   ├── main.py                  # FastAPI app and endpoints
│   ├── ai_content_selector.py  # AI analysis engine
│   ├── wedding_object_detector.py # Object detection
│   ├── emotion_analyzer.py      # Emotion analysis
│   ├── story_arc_creator.py     # Narrative generation
│   ├── video_processor.py       # Video processing pipeline
│   ├── simple_beat_detector.py  # Music analysis
│   ├── fcp7_xml_generator.py    # Premiere Pro export
│   └── requirements.txt         # Python dependencies
├── tests/                       # Test suite
│   ├── test_autocut_e2e.py      # E2E tests
│   ├── e2e_assets.py           # Synthetic media generation
│   └── conftest.py             # Test configuration
├── shared/                      # Shared types/schemas
└── README.md                    # This file
```

## 🎵 Advanced Music Features

### Intelligent Beat Detection

- **Tempo Detection**: High-accuracy BPM detection (60-200 range)
- **Beat Tracking**: Individual beat identification with confidence scoring
- **Bar Detection**: 4/4 time signature recognition and bar grouping
- **Music Start Detection**: Finds actual musical content start (not silence)
- **Grid Alignment**: Consistent musical timing across all clips

### Music Analysis Process

1. **Audio Conversion**: Convert to WAV for optimal processing
2. **Tempo Estimation**: Multiple algorithms for robust BPM detection
3. **Beat Tracking**: Identify beats with confidence scoring
4. **Bar Detection**: Group beats into musical bars
5. **Start Detection**: Find actual music start (skip intro silence)
6. **Grid Alignment**: Align all timing to musical grid

## 🤖 AI-Powered Content Analysis

### Object Detection

- **Wedding Elements**: Rings, cake, ceremony moments
- **People Detection**: Face counting and confidence scoring
- **Activity Recognition**: Dancing, speeches, key moments
- **Quality Assessment**: Motion, brightness, contrast analysis

### Emotion Analysis

- **Sentiment Detection**: Romantic, joyful, intimate moments
- **Mood Classification**: Emotional tone analysis per clip
- **Story Importance**: Narrative significance scoring
- **Scene Classification**: Ceremony, reception, preparation, etc.

### AI Selection Process

1. **Visual Analysis**: Extract frames and analyze content
2. **Object Detection**: Identify key wedding elements
3. **Emotion Scoring**: Analyze emotional content
4. **Quality Assessment**: Technical quality evaluation
5. **Story Arc**: Generate narrative flow and importance
6. **Selection Reasoning**: AI-powered clip selection with explanations

## 🎬 Video Processing Pipeline

### Two-Stage Architecture

**Stage 1: Assemble (Fast Proxy)**

- Create 720p proxies for fast processing
- Generate deterministic timeline.json
- Fast preview for immediate feedback
- Timeline artifacts for reproducibility

**Stage 2: Conform (Master Quality)**

- Re-render from original sources
- Frame-accurate cuts with -accurate_seek
- High-quality encoding (CRF 18, medium preset)
- Professional-grade output

### Timeline Artifacts

Each processing run generates:

- **Clip Data**: Absolute paths and precise timecodes
- **Metadata**: FPS, duration, music path, processing flags
- **Hashes**: SHA256 fingerprints for reproducibility
- **Reproducibility**: Deterministic output for consistent results

## 🧪 Testing

### Quick Test

```bash
pnpm run test:e2e
```

### Test Options

```bash
# Generate test assets only
pnpm run test:e2e:assets

# Run with CI-friendly output
pnpm run test:e2e:ci

# Run specific test
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_autocut_processing -v
```

## 🔧 Configuration

### Port Configuration

```bash
# Backend
export WORKER_PORT=8123

# Frontend
export VITE_API_BASE_URL=http://127.0.0.1:8123
```

### Performance Tuning

```bash
# FFmpeg settings in worker/config.py
FFMPEG_CRF=18              # Quality (lower = better)
FFMPEG_PRESET=medium       # Speed vs quality
FFMPEG_AUDIO_BITRATE=128k  # Audio quality
```

### Debug Logging

```bash
export VITE_ENABLE_DEBUG_LOGS=true
export ENABLE_TIMING_LOGS=true
```

## 🚀 Future Development Roadmap

### 🎯 Phase 1: Enhanced AI Intelligence (Next 3 months)

#### Visual Intelligence Improvements

- **Advanced Scene Detection**: Better moment identification
- **Facial Recognition**: Identify specific people in clips
- **Action Recognition**: Detect dancing, speeches, key events
- **Quality Enhancement**: Automatic stabilization and color correction

#### AI Model Upgrades

- **Custom Wedding Model**: Train on wedding-specific data
- **Emotion Refinement**: More nuanced emotional analysis
- **Story Arc Enhancement**: Better narrative flow generation
- **Multi-language Support**: International wedding analysis

### 🎯 Phase 2: Professional Features (3-6 months)

#### Advanced Video Processing

- **Smart Transitions**: Crossfades, dissolves, wipes
- **Color Grading**: Automatic color correction and matching
- **Stabilization**: Fix shaky footage automatically
- **Aspect Ratio Handling**: Smart cropping for different formats

#### User Experience

- **Style Presets**: "Romantic", "Energetic", "Cinematic", "Documentary"
- **Manual Override**: User control over AI selections
- **Batch Processing**: Handle multiple projects simultaneously
- **Template System**: Save and reuse successful configurations

### 🎯 Phase 3: Advanced AI & Automation (6-12 months)

#### Next-Gen AI Features

- **Real-time Analysis**: Live video analysis during import
- **Predictive Selection**: Learn from user preferences
- **Multi-modal Analysis**: Combine audio, visual, and metadata
- **Custom AI Training**: User-specific model training

#### Professional Workflow

- **Cloud Sync**: Optional cloud backup and sync
- **Team Collaboration**: Multi-user project sharing
- **API Integration**: Connect with other wedding tools
- **Mobile Companion**: iOS/Android companion app

### 🎯 Phase 4: Platform Expansion (12+ months)

#### Multi-Platform Support

- **Web Version**: Browser-based editing
- **Mobile Apps**: Full-featured mobile applications
- **Cloud Processing**: Optional cloud-based processing
- **Enterprise Features**: Professional studio tools

#### Advanced Features

- **Live Streaming**: Real-time highlight generation
- **VR/AR Support**: Immersive wedding experiences
- **AI Voiceover**: Automatic narration generation
- **Multi-language**: International market support

## 💡 Improvement Ideas

### 🎨 User Experience

- **Drag & Drop Enhancements**: Visual feedback during file selection
- **Preview System**: Real-time preview before final render
- **Undo/Redo**: Full editing history support
- **Keyboard Shortcuts**: Power user efficiency
- **Dark/Light Theme**: User preference options

### 🤖 AI Enhancements

- **Custom Training**: User-specific AI model training
- **Feedback Learning**: Improve from user corrections
- **Multi-language Analysis**: International wedding support
- **Advanced Object Detection**: More wedding-specific elements
- **Emotion Timeline**: Visual emotion progression

### 🎬 Video Features

- **Advanced Transitions**: Professional transition effects
- **Color Grading**: Automatic and manual color correction
- **Audio Enhancement**: Noise reduction and audio balancing
- **Multi-camera Sync**: Handle multiple camera angles
- **Slow Motion**: Intelligent slow-motion effects

### 🔧 Technical Improvements

- **Performance Optimization**: Faster processing and rendering
- **Memory Management**: Better resource utilization
- **Error Recovery**: Robust error handling and recovery
- **Logging System**: Comprehensive debugging and monitoring
- **Plugin Architecture**: Extensible feature system

### 📱 Platform Features

- **Mobile App**: iOS/Android companion applications
- **Web Version**: Browser-based editing interface
- **Cloud Integration**: Optional cloud storage and sync
- **API Access**: Third-party integration capabilities
- **Webhook Support**: Event-driven processing

## 🛠️ Troubleshooting

### Common Issues

**FFmpeg not found:**

```bash
# Verify installation
ffmpeg -version
# Check PATH environment variable
echo $PATH
```

**Port conflicts:**

```bash
# Check port usage
lsof -i :8123  # macOS/Linux
netstat -ano | findstr :8123  # Windows
```

**Backend connection failed:**

```bash
# Verify worker is running
curl http://127.0.0.1:8123/health
# Check worker logs for errors
```

**Video processing fails:**

- Check file permissions and formats
- Ensure sufficient disk space
- Verify FFmpeg installation
- Check system resources (CPU, RAM)

### Debug Information

```bash
# Health check
curl http://127.0.0.1:8123/health

# Check temporary files
ls -la /tmp/clipsense_*  # macOS/Linux
dir %TEMP%\clipsense_*   # Windows
```

## 📚 Documentation

- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Comprehensive technical architecture
- **[DEBUG_GUIDE.md](DEBUG_GUIDE.md)** - Debugging and troubleshooting
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[tests/README.md](tests/README.md)** - Testing documentation

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FFmpeg** for professional video processing
- **OpenCV** for computer vision capabilities
- **librosa** for advanced music analysis
- **Tauri** for cross-platform desktop development
- **React** for modern UI development
- **FastAPI** for high-performance API development

---

**ClipSense** - _Upload. Analyze. Create._ 🎬✨
