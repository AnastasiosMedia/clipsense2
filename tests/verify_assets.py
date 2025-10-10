#!/usr/bin/env python3
"""
Asset Hash Verification Script
Verifies that generated test assets are byte-stable and deterministic
"""

import hashlib
import os
import sys
from pathlib import Path

def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

def get_expected_hashes():
    """Get expected hashes for deterministic assets"""
    # These hashes should be updated when asset generation changes
    return {
        "clip1.mp4": "864aac1b55a4494a6ab67b2dd718065a553dafd3881c663fa03dc259d0612dc4",
        "clip2.mp4": "b2f7a20f2b270d6adcac346303f084cba596aa2ad65b21bcfa9c7ecca288289f",
        "music.wav": "9a2be43b3db400a5fa17a99e108971048ee8c21d0d426e5f0a7a659890cd33b4"
    }

def verify_assets():
    """Verify that all test assets exist and have expected hashes"""
    media_dir = Path("tests/media")
    expected_hashes = get_expected_hashes()
    
    print("🔍 Verifying test asset hashes...")
    
    all_good = True
    
    for filename, expected_hash in expected_hashes.items():
        filepath = media_dir / filename
        
        if not filepath.exists():
            print(f"❌ {filename}: File not found")
            all_good = False
            continue
        
        actual_hash = calculate_file_hash(filepath)
        
        if actual_hash == expected_hash:
            print(f"✅ {filename}: Hash matches")
        else:
            print(f"❌ {filename}: Hash mismatch")
            print(f"   Expected: {expected_hash}")
            print(f"   Actual:   {actual_hash}")
            all_good = False
    
    return all_good

def generate_hashes():
    """Generate current hashes for all test assets"""
    media_dir = Path("tests/media")
    
    print("📊 Generating current asset hashes...")
    
    for filepath in media_dir.glob("*"):
        if filepath.is_file() and filepath.suffix in ['.mp4', '.wav']:
            hash_value = calculate_file_hash(filepath)
            print(f"{filepath.name}: {hash_value}")

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "generate":
        generate_hashes()
    else:
        if verify_assets():
            print("🎉 All asset hashes verified successfully!")
            sys.exit(0)
        else:
            print("❌ Asset hash verification failed!")
            sys.exit(1)

if __name__ == "__main__":
    main()
