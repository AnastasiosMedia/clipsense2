"""
Pytest configuration and fixtures for ClipSense E2E tests
"""

import os
import pytest
import subprocess
import time
import requests
import signal
import sys
from pathlib import Path
from typing import Generator, Optional

# Add the worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "worker"))

from ffmpeg_checker import FFmpegChecker

@pytest.fixture(scope="session")
def ffmpeg_available() -> bool:
    """Check if FFmpeg is available, skip tests if not"""
    is_available, _, _ = FFmpegChecker.check_ffmpeg_availability()
    if not is_available:
        pytest.skip("FFmpeg not available - install FFmpeg to run E2E tests")
    return is_available

@pytest.fixture(scope="session")
def test_assets() -> dict:
    """Ensure test assets are generated"""
    media_dir = Path("tests/media")
    base_path = Path(__file__).parent.parent
    required_files = {
        "clip1": str(base_path / "tests" / "media" / "clip1.mp4"),
        "clip2": str(base_path / "tests" / "media" / "clip2.mp4"), 
        "music": str(base_path / "tests" / "media" / "music.wav")
    }
    
    # Check if all files exist
    missing_files = []
    for name, path in required_files.items():
        if not Path(path).exists():
            missing_files.append(name)
    
    if missing_files:
        pytest.skip(f"Test assets missing: {missing_files}. Run 'python tests/e2e_assets.py' first")
    
    return required_files

@pytest.fixture(scope="session")
def worker_port() -> int:
    """Get worker port from environment or use default"""
    return int(os.getenv("WORKER_PORT", "8123"))

@pytest.fixture(scope="session")
def worker_url(worker_port: int) -> str:
    """Get worker base URL"""
    return f"http://127.0.0.1:{worker_port}"

@pytest.fixture(scope="session")
def worker_process(worker_port: int, ffmpeg_available: bool, tmp_root: Path) -> Generator[subprocess.Popen, None, None]:
    """Start the worker process for testing"""
    if not ffmpeg_available:
        pytest.skip("FFmpeg not available")
    
    # Create logs directory
    logs_dir = tmp_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Start the worker process
    worker_dir = Path(__file__).parent.parent / "worker"
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "127.0.0.1",
        "--port", str(worker_port)
    ]
    
    print(f"🚀 Starting worker: {' '.join(cmd)}")
    
    # Set environment variables
    env = os.environ.copy()
    env["CLIPSENSE_TMP_DIR"] = str(tmp_root)
    
    process = subprocess.Popen(
        cmd,
        cwd=worker_dir,
        stdout=open(logs_dir / f"worker_{worker_port}.log", "w"),
        stderr=subprocess.STDOUT,
        text=True,
        env=env
    )
    
    # Wait for worker to start
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"http://127.0.0.1:{worker_port}/ping", timeout=1)
            if response.status_code == 200:
                print(f"✅ Worker started successfully on port {worker_port}")
                break
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        if i == max_retries - 1:
            process.terminate()
            process.wait()
            pytest.fail(f"Worker failed to start on port {worker_port}")
    
    yield process
    
    # Cleanup
    print("🛑 Stopping worker...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()

@pytest.fixture(scope="session")
def tmp_root(worker_port: int) -> Path:
    """Create a unique temp root for this test run"""
    pid = os.getpid()
    worker_id = os.getenv("WORKER_ID", str(worker_port))
    tmp_root = Path("tests/.tmp") / f"run_{pid}_{worker_id}"
    tmp_root.mkdir(parents=True, exist_ok=True)
    return tmp_root.resolve()

@pytest.fixture
def temp_dir(tmp_path_factory, tmp_root: Path) -> Path:
    """Create a temporary directory for test outputs"""
    temp_dir = tmp_path_factory.mktemp("case", base_dir=tmp_root)
    return temp_dir
