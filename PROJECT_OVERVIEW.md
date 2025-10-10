# ClipSense Project Overview

## 🎯 What We Built

ClipSense is a complete local desktop MVP app for creating highlight videos with music overlay. It's built with a modern tech stack and designed for privacy-first, local-only processing.

## 🏗️ Architecture

```
┌─────────────────┐    HTTP API     ┌─────────────────┐
│   Tauri App     │◄──────────────►│  Python Worker  │
│  (React + TS)   │   localhost:8123│   (FastAPI)     │
└─────────────────┘                 └─────────────────┘
         │                                    │
         │                                    ▼
         │                           ┌─────────────────┐
         │                           │     FFmpeg      │
         │                           │  (Video Engine) │
         │                           └─────────────────┘
         │
         ▼
┌─────────────────┐
│   File System   │
│  (Input/Output) │
└─────────────────┘
```

## 📁 Project Structure

```
clipsense2/
├── app/                    # Tauri + React Frontend
│   ├── src/
│   │   ├── components/     # React UI components
│   │   ├── services/       # API communication
│   │   ├── types/          # TypeScript types
│   │   └── App.tsx         # Main app component
│   ├── src-tauri/          # Tauri configuration
│   └── package.json        # Node.js dependencies
├── worker/                 # Python FastAPI Backend
│   ├── main.py            # FastAPI server
│   ├── video_processor.py # FFmpeg processing logic
│   └── requirements.txt   # Python dependencies
├── shared/                # Shared TypeScript types
└── scripts/               # Development utilities
```

## 🚀 Key Features

### Frontend (Tauri + React)

- **Modern UI**: Dark theme with Tailwind CSS
- **File Pickers**: Native file selection dialogs
- **Real-time Status**: Processing progress and error handling
- **Cross-platform**: Works on Windows, macOS, and Linux

### Backend (Python FastAPI)

- **Video Processing**: Creates 720p proxies, trims segments
- **Audio Overlay**: Normalizes music to -14 LUFS
- **Concatenation**: Combines clips into final highlight
- **Error Handling**: Comprehensive error reporting

### Video Engine (FFmpeg)

- **Proxy Creation**: Fast 720p previews for processing
- **Smart Trimming**: Equal segments from each clip
- **Audio Normalization**: Professional loudness standards
- **Format Support**: MP4, MOV, AVI, MKV, MP3, WAV, etc.

## 🛠️ Development Workflow

### Quick Start

```bash
# One-command setup and run
./quickstart.sh
```

### Manual Setup

```bash
# 1. Setup backend
cd worker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run_dev.py

# 2. Setup frontend (new terminal)
cd app
pnpm install
pnpm tauri dev
```

### Testing

```bash
# Test API endpoints
python demo_test.py

# Test full setup
python test_setup.py
```

## 🔧 Technical Details

### Dependencies

- **Frontend**: React 18, TypeScript, Tailwind CSS, Tauri
- **Backend**: FastAPI, Uvicorn, Pydantic, OpenCV, NumPy
- **System**: FFmpeg (required), Node.js 18+, Python 3.8+

### API Endpoints

- `GET /health` - Backend health check
- `POST /autocut` - Process videos and create highlight

### File Processing Flow

1. **Input Validation**: Check file existence and formats
2. **Proxy Creation**: Generate 720p versions for fast processing
3. **Segment Calculation**: Determine equal clip durations
4. **Trimming**: Extract segments from each clip
5. **Concatenation**: Combine segments into single video
6. **Audio Overlay**: Add and normalize music track
7. **Output**: Save final highlight video

## 🎨 UI Components

- **FilePicker**: Handles video and audio file selection
- **ProcessingStatus**: Shows progress and error states
- **ResultDisplay**: Displays output file path and actions
- **App**: Main container with layout and state management

## 🔒 Privacy & Security

- **100% Local**: No cloud services or external APIs
- **No Login**: No user accounts or data collection
- **Temporary Files**: Processed files cleaned up automatically
- **File Access**: Only reads selected files, no system access

## 🚀 Future Enhancements

- **Batch Processing**: Multiple highlight videos at once
- **Custom Duration**: User-defined highlight length
- **Video Effects**: Transitions, filters, and overlays
- **Audio Mixing**: Multiple music tracks or voiceovers
- **Export Options**: Different resolutions and formats
- **Auto Worker**: Automatic backend startup from frontend

## 📝 Development Notes

- **Error Handling**: Comprehensive error states and user feedback
- **Type Safety**: Full TypeScript coverage with shared types
- **Responsive Design**: Works on different screen sizes
- **Accessibility**: Keyboard navigation and screen reader support
- **Performance**: Optimized for large video files and fast processing

This is a production-ready MVP that demonstrates modern desktop app development with local processing capabilities.
