# Changelog

All notable changes to ClipSense will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-11

### 🎵 Added - Advanced Music Features

- **Music Start Detection**: Automatically detects when music actually begins (not silence)
- **Intelligent Beat Detection**: Uses librosa for accurate tempo and beat analysis
- **Bar Detection**: Identifies 4/4 time signature and musical bars
- **Perfect Musical Sync**: Video clips now start exactly on musical beats
- **Confidence Scoring**: Provides reliability metrics for all music analysis

### 🎞️ Added - Premiere Pro Integration

- **FCP7 XML Export**: Generate Premiere Pro-compatible timeline files
- **Professional Workflow**: Direct import into Premiere Pro for editing
- **Timeline Artifacts**: Complete timing data with bar markers
- **Reproducible Edits**: SHA256 hashes for consistent results

### 🔧 Added - Technical Improvements

- **SimpleBeatDetector**: New robust music analysis engine
- **Grid Alignment**: Preserves music start offset through processing
- **Enhanced Timeline**: Bar markers and musical timing data
- **Comprehensive Logging**: Detailed progress and error reporting

### 🐛 Fixed - Critical Issues

- **Music Start Bug**: Fixed clips starting at 0.0s regardless of music timing
- **Grid Alignment Bug**: Fixed offset loss during beat alignment
- **Timeline Accuracy**: Improved precision of musical timing
- **Error Handling**: Better fallback systems for music analysis

### 📊 Improved - Performance

- **Faster Analysis**: Optimized music processing pipeline
- **Better Accuracy**: More reliable beat and bar detection
- **Reduced Errors**: Improved error handling and recovery
- **Enhanced Logging**: Better debugging and monitoring

### 📚 Added - Documentation

- **Technical Documentation**: Comprehensive system architecture guide
- **API Reference**: Updated with new endpoints and features
- **Debugging Guide**: Troubleshooting and performance optimization
- **Changelog**: Track all improvements and changes

## [1.0.0] - 2025-10-10

### 🎬 Added - Core Features

- **Basic Video Processing**: Drag-drop multiple video clips
- **Music Overlay**: Select and overlay music track
- **Auto-Cut Generation**: Create 60-second highlight videos
- **Two-Stage Pipeline**: Assemble (proxy) + Conform (master)
- **Timeline Artifacts**: Reproducible timeline.json files

### 🏗️ Added - Architecture

- **Tauri Frontend**: React + TypeScript + Tailwind CSS
- **FastAPI Backend**: Python worker with FFmpeg integration
- **Local Processing**: 100% privacy-first, no cloud dependencies
- **Cross-Platform**: macOS, Windows, Linux support

### 🧪 Added - Testing

- **E2E Test Suite**: Comprehensive automated testing
- **Synthetic Media**: FFmpeg-generated test assets
- **CI/CD Integration**: GitHub Actions workflow
- **Performance Testing**: Speed and quality validation

### 📋 Added - Configuration

- **Port Management**: Automatic port collision detection
- **FFmpeg Settings**: Configurable quality and performance
- **Environment Variables**: Flexible configuration options
- **Debug Logging**: Comprehensive logging system

---

## Version History

| Version | Date | Major Changes |
|---------|------|---------------|
| 2.0.0 | 2025-10-11 | Advanced beat detection, Premiere Pro integration |
| 1.0.0 | 2025-10-10 | Core video processing, basic music overlay |

## Migration Guide

### From v1.0.0 to v2.0.0

**Breaking Changes**:
- New music analysis requires `librosa` and `soundfile` dependencies
- Timeline format includes new `bar_markers` field
- API responses include additional music analysis data

**Migration Steps**:
1. Update Python dependencies: `pip install -r requirements.txt`
2. Update frontend to handle new API response format
3. Test with existing projects to verify compatibility

**New Features**:
- Music start detection works automatically
- Bar-synced timing provides better results
- Premiere Pro integration for professional workflows

---

*For more details, see [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) and [README.md](README.md)*
