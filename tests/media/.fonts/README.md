# Test Fonts Directory

This directory contains deterministic fonts for cross-platform testing.

## Font Requirements

For deterministic text rendering across different operating systems, we need:

- A consistent font file that works on all platforms
- Fixed font metrics to ensure identical text positioning
- No system font dependencies

## Current Setup

The test scripts use system fonts as fallback, but for production use, consider:

- Bundling a free font like Inter, Roboto, or DejaVu Sans
- Ensuring the font file is included in the repository
- Updating the FFmpeg drawtext commands to use the bundled font

## Font File Location

Expected font file: `tests/media/.fonts/Inter-Regular.ttf`

## Usage in FFmpeg

```bash
drawtext=fontfile='tests/media/.fonts/Inter-Regular.ttf':text='%{eif\\:t\\:d\\:2}':fontsize=24:fontcolor=white:x=10:y=10
```
