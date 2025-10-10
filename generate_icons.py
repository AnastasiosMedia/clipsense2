#!/usr/bin/env python3
"""
Simple icon generator for ClipSense
Creates basic placeholder icons for Tauri
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with the ClipSense logo"""
    # Create a new image with a dark background
    img = Image.new('RGBA', (size, size), (30, 41, 59, 255))  # gray-800
    draw = ImageDraw.Draw(img)
    
    # Draw a simple "C" for ClipSense
    margin = size // 8
    draw.arc([margin, margin, size-margin, size-margin], 0, 270, fill=(14, 165, 233, 255), width=size//8)  # primary-500
    
    # Add a small dot to represent the "clip"
    dot_size = size // 16
    dot_x = size - margin - dot_size
    dot_y = margin + dot_size
    draw.ellipse([dot_x, dot_y, dot_x + dot_size, dot_y + dot_size], fill=(14, 165, 233, 255))
    
    # Save the icon
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all required icon sizes"""
    icon_dir = "app/src-tauri/icons"
    os.makedirs(icon_dir, exist_ok=True)
    
    # Generate different sizes
    sizes = [32, 128, 256, 512]
    
    for size in sizes:
        filename = f"{icon_dir}/{size}x{size}.png"
        create_icon(size, filename)
    
    # Create 2x version for retina
    create_icon(256, f"{icon_dir}/128x128@2x.png")
    
    # Create ICO file for Windows
    img_32 = Image.open(f"{icon_dir}/32x32.png")
    img_32.save(f"{icon_dir}/icon.ico", format='ICO', sizes=[(32, 32), (16, 16)])
    
    # Create ICNS file for macOS (simplified - just copy the 512x512)
    img_512 = Image.open(f"{icon_dir}/512x512.png")
    img_512.save(f"{icon_dir}/icon.icns", format='ICNS')
    
    print("✅ All icons generated successfully!")

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw
        main()
    except ImportError:
        print("❌ PIL (Pillow) not found. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"])
        print("✅ Pillow installed. Run the script again.")
