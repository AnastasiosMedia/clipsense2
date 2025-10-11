# ClipSense Debug Guide

## 🎵 Music Analysis Debugging

### Common Music Issues

#### Music Start Detection Problems

**Symptoms**:

- Video starts with silence despite music having intro
- Bar markers start at 0.0s instead of actual music start
- First clip appears before music begins

**Debug Steps**:

```bash
# Test music analysis directly
curl -X POST http://127.0.0.1:8123/analyze_music \
  -H "Content-Type: application/json" \
  -d '{"music_path": "/path/to/music.wav", "target_duration": 30}'

# Check for music start detection in logs
grep "Music starts at" /path/to/worker/logs
```

**Solutions**:

- Verify audio file format (WAV preferred for analysis)
- Check if music has very quiet intro (below 10% threshold)
- Manually adjust threshold in `simple_beat_detector.py`

#### Beat Detection Inaccuracy

**Symptoms**:

- Clips don't align with musical beats
- Tempo detection seems wrong
- Bar intervals are inconsistent

**Debug Steps**:

```bash
# Check tempo detection
python3 -c "
from worker.simple_beat_detector import SimpleBeatDetector
import asyncio

async def test():
    detector = SimpleBeatDetector()
    result = await detector.analyze_music('/path/music.wav', 30)
    print(f'Tempo: {result[\"tempo\"]}')
    print(f'Confidence: {result[\"confidence\"]}')
    print(f'First bar: {result[\"bar_times\"][0]}')

asyncio.run(test())
"
```

**Solutions**:

- Check if music has tempo changes (not supported yet)
- Verify music is within 60-200 BPM range
- Try different music file if confidence is low

### Music Analysis Logs

**Key Log Messages**:

```
🎵 Detecting musical content start...
🎼 Music starts at: 0.42s
🥁 Estimating tempo...
🎼 Detected tempo: 103.4 BPM
🎯 Generating regular beats...
🎼 Generating bars...
🔧 Aligning beats and bars...
⏰ Adjusted timestamps: +0.42s offset
```

**Error Patterns**:

- `Music start detection failed` → Audio format issue
- `Tempo candidates: [200.0, 200.0, 200.0]` → Detection failed, using fallback
- `Confidence: 0.2` → Low confidence, may need different music

## 🎬 Video Processing Debugging

### Timeline Generation Issues

**Symptoms**:

- Bar markers reset to 0.0 in timeline.json
- Clips don't align with musical timing
- Timeline hash doesn't match expected

**Debug Steps**:

```bash
# Check timeline structure
cat timeline.json | python3 -c "
import sys, json
t = json.load(sys.stdin)
print('Bar markers:', t['bar_markers'][:5])
print('First bar:', t['bar_markers'][0])
print('Tempo:', t['tempo'])
"

# Verify bar marker preservation
grep "Writing timeline with bar markers" /path/to/logs
```

**Solutions**:

- Check if `_align_to_grid` is preserving offset
- Verify music analysis is working correctly
- Ensure bar markers are passed through pipeline

### Video Processing Errors

**Symptoms**:

- FFmpeg errors during processing
- Clips not trimming correctly
- Audio overlay fails

**Debug Steps**:

```bash
# Check FFmpeg installation
ffmpeg -version
ffprobe -version

# Test video file
ffprobe -v quiet -print_format json -show_format -show_streams /path/video.mp4

# Check temporary files
ls -la /tmp/clipsense_*
```

**Common FFmpeg Errors**:

- `No such file or directory` → File path issue
- `Invalid data found` → Corrupted video file
- `Permission denied` → File permission issue

## 🔧 System Debugging

### API Endpoint Issues

**Test All Endpoints**:

```bash
# Health check
curl http://127.0.0.1:8123/ping

# Music analysis
curl -X POST http://127.0.0.1:8123/analyze_music \
  -H "Content-Type: application/json" \
  -d '{"music_path": "/path/music.wav", "target_duration": 30}'

# Auto-cut processing
curl -X POST http://127.0.0.1:8123/autocut \
  -H "Content-Type: application/json" \
  -d '{"clips": ["/path/clip1.mp4"], "music": "/path/music.wav", "target_seconds": 30}'

# FCP7 XML generation
curl -X POST http://127.0.0.1:8123/generate_fcp7_xml \
  -H "Content-Type: application/json" \
  -d '{"timeline_path": "/path/timeline.json"}'
```

### Performance Issues

**Check System Resources**:

```bash
# CPU usage
top -p $(pgrep -f "uvicorn main:app")

# Memory usage
ps aux | grep uvicorn

# Disk space
df -h /tmp
```

**Optimize Settings**:

```python
# In worker/config.py
FFMPEG_PRESET = "ultrafast"  # Faster encoding
FFMPEG_CRF = 28              # Lower quality, faster
```

### Log Analysis

**Backend Logs**:

```bash
# Follow worker logs
tail -f /path/to/worker/logs

# Search for errors
grep -i error /path/to/worker/logs

# Check timing
grep "TIMING" /path/to/worker/logs
```

**Frontend Logs**:

- Open browser developer tools (F12)
- Check Console tab for JavaScript errors
- Check Network tab for API call failures

## 🧪 Test Debugging

### E2E Test Failures

**Run Tests with Verbose Output**:

```bash
# Full test suite
pytest tests/test_autocut_e2e.py -v -s

# Specific test
pytest tests/test_autocut_e2e.py::TestAutoCutE2E::test_autocut_processing -v -s

# With debug logging
ENABLE_TIMING_LOGS=true pytest tests/test_autocut_e2e.py -v -s
```

**Check Test Assets**:

```bash
# Generate test assets
python tests/e2e_assets.py

# Check generated files
ls -la tests/media/
ffprobe tests/media/clip1.mp4
ffprobe tests/media/music.wav
```

### Test Environment Issues

**Common Problems**:

- FFmpeg not in PATH
- Python dependencies missing
- Port conflicts
- File permission issues

**Solutions**:

```bash
# Install dependencies
pip install -r worker/requirements.txt

# Check FFmpeg
which ffmpeg
ffmpeg -version

# Check Python path
python -c "import librosa, soundfile"

# Clean test environment
rm -rf tests/.tmp/
rm -rf /tmp/clipsense_*
```

## 📊 Performance Debugging

### Memory Usage

**Monitor Memory**:

```bash
# Python process memory
ps aux | grep python | grep uvicorn

# System memory
free -h  # Linux
vm_stat  # macOS
```

**Memory Issues**:

- Large video files consuming memory
- Music analysis loading entire audio file
- FFmpeg processes not cleaning up

### Processing Speed

**Timing Analysis**:

```bash
# Enable timing logs
export ENABLE_TIMING_LOGS=true

# Check processing times
grep "TIMING" /path/to/logs
```

**Speed Optimization**:

- Use faster FFmpeg presets
- Reduce video resolution
- Limit music analysis duration
- Process videos in smaller chunks

## 🚨 Emergency Debugging

### Complete System Reset

```bash
# Stop all processes
pkill -f "uvicorn main:app"
pkill -f "tauri dev"

# Clean temporary files
rm -rf /tmp/clipsense_*
rm -rf tests/.tmp/

# Restart worker
cd worker && uvicorn main:app --port 8123 --reload &

# Test basic functionality
curl http://127.0.0.1:8123/ping
```

### Data Recovery

**Timeline Recovery**:

```bash
# Find timeline files
find /tmp -name "timeline.json" -type f

# Check timeline integrity
python3 -c "
import json
with open('timeline.json', 'r') as f:
    t = json.load(f)
print('Valid timeline:', 'clips' in t and 'bar_markers' in t)
"
```

**Video Recovery**:

```bash
# Find output files
find /tmp -name "highlight_*.mp4" -type f

# Check video integrity
ffprobe -v quiet -print_format json -show_format /path/highlight.mp4
```

---

## 📞 Getting Help

### Debug Information to Collect

1. **System Information**:

   - OS version and architecture
   - Python version: `python --version`
   - FFmpeg version: `ffmpeg -version`
   - Node.js version: `node --version`

2. **Error Logs**:

   - Backend logs (terminal output)
   - Frontend logs (browser console)
   - System logs (if applicable)

3. **Test Files**:

   - Sample video and audio files
   - Generated timeline.json
   - Error output from failed operations

4. **Configuration**:
   - Environment variables
   - FFmpeg settings
   - Port configuration

### Common Solutions

| Problem                   | Solution                                 |
| ------------------------- | ---------------------------------------- |
| Music starts at 0.0s      | Check music start detection logs         |
| Clips not synced          | Verify beat detection accuracy           |
| FFmpeg errors             | Check file formats and permissions       |
| API connection failed     | Verify worker is running on correct port |
| Timeline generation fails | Check bar marker preservation            |

---

_For more technical details, see [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)_
