import os
import asyncio
import tempfile
import subprocess
from pathlib import Path

# Ensure worker package is importable
import sys
# Ensure parent is importable, then import worker as a package
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Ensure .env is loaded for this script as well
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except Exception:
    pass

from worker.openai_vision import OpenAIVisionClient
from worker.config import Config  # loads .env automatically if present


async def extract_thumbnail(video_path: str) -> str:
    tmpdir = tempfile.mkdtemp(prefix="cs_thumb_test_")
    out = os.path.join(tmpdir, "thumb.jpg")
    cmd = [
        "ffmpeg", "-y",
        "-ss", "0",
        "-i", video_path,
        "-frames:v", "1",
        "-q:v", "2",
        out,
    ]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {stderr.decode('utf-8', errors='ignore')}")
    return out


async def analyze_dir(dir_path: Path, limit: int = 5):
    files = sorted([p for p in dir_path.iterdir() if p.suffix.lower() in {'.mp4', '.mov', '.m4v'}])[:limit]
    if not files:
        raise FileNotFoundError(f"No video files found in {dir_path}")
    print(f"Analyzing {len(files)} clips from {dir_path}...")
    client = OpenAIVisionClient()
    if not client.enabled:
        raise RuntimeError("OpenAI Vision client not enabled (check USE_OPENAI_VISION and OPENAI_API_KEY)")
    for idx, f in enumerate(files, 1):
        thumb = await extract_thumbnail(str(f))
        try:
            res = client.analyze_thumbnail(thumb)
            print(f"[{idx}] {f.name} → {res}")
        finally:
            try:
                os.remove(thumb)
            except Exception:
                pass

async def main():
    project_root = Path(__file__).resolve().parents[1]
    print(f"USE_OPENAI_VISION={Config.USE_OPENAI_VISION}, MODEL={Config.OPENAI_VISION_MODEL}")
    if not Config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set (check your .env)")

    # Default: tests/media/clip1.mp4 single test if no arg
    import sys as _sys
    if len(_sys.argv) > 1:
        dir_arg = Path(_sys.argv[1])
        await analyze_dir(dir_arg, limit=5)
    else:
        candidate = project_root / 'tests' / 'media' / 'clip1.mp4'
        if not candidate.exists():
            raise FileNotFoundError(f"Test clip not found: {candidate}")
        thumb = await extract_thumbnail(str(candidate))
        try:
            client = OpenAIVisionClient()
            if not client.enabled:
                raise RuntimeError("OpenAI Vision client not enabled (check USE_OPENAI_VISION and OPENAI_API_KEY)")
            result = client.analyze_thumbnail(thumb)
            print("Vision result:")
            print(result)
        finally:
            try:
                os.remove(thumb)
            except Exception:
                pass


if __name__ == '__main__':
    asyncio.run(main())


