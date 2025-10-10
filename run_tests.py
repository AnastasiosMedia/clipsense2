#!/usr/bin/env python3
"""
ClipSense E2E Test Runner
Comprehensive test runner with setup, execution, and reporting
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a command and handle output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return None

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check FFmpeg
    ffmpeg_result = run_command(["ffmpeg", "-version"], "FFmpeg check", check=False)
    if not ffmpeg_result or ffmpeg_result.returncode != 0:
        print("❌ FFmpeg not found. Please install FFmpeg first.")
        return False
    
    # Check Python
    python_result = run_command([sys.executable, "--version"], "Python check", check=False)
    if not python_result or python_result.returncode != 0:
        print("❌ Python not found.")
        return False
    
    # Check Node.js
    node_result = run_command(["node", "--version"], "Node.js check", check=False)
    if not node_result or node_result.returncode != 0:
        print("❌ Node.js not found. Please install Node.js first.")
        return False
    
    # Check pnpm
    pnpm_result = run_command(["pnpm", "--version"], "pnpm check", check=False)
    if not pnpm_result or pnpm_result.returncode != 0:
        print("❌ pnpm not found. Please install pnpm first.")
        return False
    
    print("✅ All prerequisites met")
    return True

def setup_dependencies():
    """Setup Python and Node.js dependencies"""
    print("📦 Setting up dependencies...")
    
    # Install Python dependencies
    worker_dir = Path("worker")
    if worker_dir.exists():
        result = run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], "Installing Python dependencies", check=False)
        if not result or result.returncode != 0:
            print("⚠️  Python dependencies installation had issues")
    
    # Install Node.js dependencies
    result = run_command(["pnpm", "install"], "Installing Node.js dependencies", check=False)
    if not result or result.returncode != 0:
        print("⚠️  Node.js dependencies installation had issues")
    
    print("✅ Dependencies setup completed")

def generate_test_assets():
    """Generate test assets"""
    print("🎬 Generating test assets...")
    
    # Try Python script first
    result = run_command([sys.executable, "tests/e2e_assets.py"], "Generating test assets (Python)", check=False)
    
    if not result or result.returncode != 0:
        # Fallback to bash script
        print("🔄 Python script failed, trying bash script...")
        result = run_command(["bash", "tests/e2e_assets.sh"], "Generating test assets (Bash)", check=False)
        
        if not result or result.returncode != 0:
            print("❌ Failed to generate test assets")
            return False
    
    # Verify assets were created
    media_dir = Path("tests/media")
    required_files = ["clip1.mp4", "clip2.mp4", "music.wav"]
    
    for filename in required_files:
        if not (media_dir / filename).exists():
            print(f"❌ Test asset missing: {filename}")
            return False
    
    print("✅ Test assets generated successfully")
    return True

def run_tests(verbose=False, ci_mode=False):
    """Run the E2E tests"""
    print("🧪 Running E2E tests...")
    
    # Prepare pytest command
    cmd = [sys.executable, "-m", "pytest", "tests/"]
    
    if verbose:
        cmd.append("-v")
    
    if ci_mode:
        cmd.extend(["-v", "--tb=short"])
    
    # Run tests
    result = run_command(cmd, "Running E2E tests", check=False)
    
    if result and result.returncode == 0:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        if result and result.stdout:
            print("Test output:")
            print(result.stdout)
        if result and result.stderr:
            print("Test errors:")
            print(result.stderr)
        return False

def cleanup():
    """Clean up temporary files"""
    print("🧹 Cleaning up...")
    
    temp_dir = Path("tests/.tmp")
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("✅ Cleanup completed")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="ClipSense E2E Test Runner")
    parser.add_argument("--skip-setup", action="store_true", help="Skip dependency setup")
    parser.add_argument("--skip-assets", action="store_true", help="Skip asset generation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--ci", action="store_true", help="CI mode")
    parser.add_argument("--cleanup", action="store_true", help="Clean up after tests")
    args = parser.parse_args()
    
    print("🎬 ClipSense E2E Test Runner")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            sys.exit(1)
        
        # Setup dependencies
        if not args.skip_setup:
            setup_dependencies()
        
        # Generate test assets
        if not args.skip_assets:
            if not generate_test_assets():
                sys.exit(1)
        
        # Run tests
        if not run_tests(verbose=args.verbose, ci_mode=args.ci):
            sys.exit(1)
        
        # Cleanup
        if args.cleanup:
            cleanup()
        
        elapsed_time = time.time() - start_time
        print(f"🎉 All tests completed successfully in {elapsed_time:.1f} seconds")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
