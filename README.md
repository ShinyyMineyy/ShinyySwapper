# Shinyy's Face Swapper

AI-powered face swapping tool with web interface.

## Features
- Image face swapping
- Video face swapping with speed modes
- Multi-face swapping
- Face enhancement (GFPGAN + Real-ESRGAN)

## Google Colab Setup (Recommended)

1. **Upload to GitHub** (exclude models - they're auto-downloaded)
2. **Open `Colab_Setup.ipynb` in Google Colab**
3. **Run all cells** - models download automatically
4. **Access via ngrok URL**

That's it! Models download from public sources automatically.

## Local Setup

1. **Install Python 3.10**
2. **Run:**
   ```bash
   python -m venv .venv1
   .venv1\Scripts\pip.exe install -r config\requirements.txt
   python START.bat
   ```

## Tech Stack
- Flask + CORS
- InsightFace
- ONNX Runtime
- OpenCV
- GFPGAN + Real-ESRGAN
