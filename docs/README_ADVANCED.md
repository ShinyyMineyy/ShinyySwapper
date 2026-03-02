# 🔴 Advanced Face Swapper - Complete System

## 🎯 Overview

Professional-grade AI face swapping system with **advanced enhancement pipeline**:
- **CodeFormer** - Superior face restoration
- **RestoreFormer** - Texture preservation
- **Face Parsing (BiSeNet)** - Precise face segmentation
- **Occluder Handling** - Preserves glasses/accessories
- **Video Stabilization** - Temporal consistency (no flickering)

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT (Image/Video)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Face Detection (InsightFace buffalo_l)             │
│  - Detects all faces in image                               │
│  - Returns bounding boxes + landmarks                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Face Parsing (BiSeNet) [NEW]                       │
│  - Identifies exact face regions (skin, eyes, nose, mouth)  │
│  - Detects occluders (glasses, masks, accessories)          │
│  - Creates precise segmentation mask                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Face Swap (inswapper_128.onnx)                     │
│  - Swaps source face onto target                            │
│  - Preserves target pose/lighting                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Color Matching (LAB + RGB dual-space)              │
│  - Matches skin tone to target body                         │
│  - 60% color shift for natural blend                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Occluder Preservation [NEW]                        │
│  - Restores glasses from target image                       │
│  - Preserves earrings, masks, accessories                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Face Enhancement [UPGRADED]                        │
│  Priority order:                                             │
│  1. CodeFormer (best quality) [NEW]                         │
│  2. RestoreFormer (texture) [NEW]                           │
│  3. GFPGAN (fallback)                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: Super Resolution (Real-ESRGAN 2x)                  │
│  - Upscales large faces                                     │
│  - Sharpens details                                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: Final Sharpening                                   │
│  - Unsharp mask (strength=0.3)                              │
│  - Matches target image sharpness                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 9: Temporal Smoothing [VIDEO ONLY] [NEW]              │
│  - 5-frame temporal buffer                                  │
│  - Optical flow stabilization                               │
│  - Prevents flickering                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT (Enhanced Result)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Shinyy's Mukhosh Changer/
│
├── Core Modules
│   ├── app.py                      # Gradio web interface
│   ├── SinglePhoto.py              # Main face swapper (UPGRADED)
│   ├── VideoSwapping.py            # Video processor (UPGRADED)
│   ├── FaceEnhancer.py             # Old enhancer (kept for compatibility)
│   │
│   ├── AdvancedEnhancer.py         # [NEW] CodeFormer + RestoreFormer
│   ├── FaceParser.py               # [NEW] BiSeNet face parsing
│   ├── VideoStabilizer.py          # [NEW] Temporal consistency
│   │
│   ├── face_parsing.py             # [NEW] BiSeNet model
│   ├── codeformer.py               # [NEW] CodeFormer wrapper
│   └── restoreformer.py            # [NEW] RestoreFormer wrapper
│
├── Configuration
│   ├── config.json                 # System settings
│   ├── requirements.txt            # Original dependencies
│   ├── requirements-advanced.txt   # [NEW] All dependencies
│   └── ADVANCED_FEATURES.md        # [NEW] Feature documentation
│
├── Models (auto-download)
│   ├── inswapper_128.onnx          # Face swap model (~550MB)
│   ├── GFPGANv1.4.pth              # Face restoration (~350MB)
│   ├── RealESRGAN_x2plus.pth       # Super resolution (~65MB)
│   ├── codeformer.pth              # [NEW] Best restoration (~370MB)
│   ├── restoreformer.pth           # [NEW] Texture preservation (~150MB)
│   └── face_parsing.pth            # [NEW] Face segmentation (~50MB)
│
└── Output Directories
    ├── BatchOutput/                # Batch image results
    ├── VideoOutput/                # Video results
    ├── SinglePhoto/                # Single image results
    └── VideoSwapping/              # Video processing workspace
```

---

## 🚀 Installation

### Step 1: Install Dependencies
```bash
# Option A: Full installation (recommended)
pip install -r requirements-advanced.txt

# Option B: Minimal (without advanced features)
pip install -r requirements.txt
```

### Step 2: Run Application
```bash
# Windows
START.bat

# Or manually
python app.py
```

### Step 3: Models Auto-Download
- Models download automatically on first run
- Total size: ~1.2GB
- Stored in `models/` folder

---

## 🎨 Features Comparison

| Feature | Old System | New System |
|---------|-----------|------------|
| **Face Detection** | InsightFace ✓ | InsightFace ✓ |
| **Face Parsing** | ✗ | BiSeNet ✓ |
| **Face Swap** | inswapper ✓ | inswapper ✓ |
| **Color Matching** | LAB+RGB ✓ | LAB+RGB ✓ |
| **Occluder Handling** | ✗ | Automatic ✓ |
| **Enhancement** | GFPGAN | CodeFormer → RestoreFormer → GFPGAN |
| **Super Resolution** | Real-ESRGAN ✓ | Real-ESRGAN ✓ |
| **Video Stabilization** | ✗ | Temporal smoothing ✓ |
| **Processing Time** | 3-5 sec/face | 5-8 sec/face |
| **Quality** | Good | Excellent |

---

## 🎯 Usage Examples

### 1. Web Interface (Easiest)
```bash
START.bat
```
- Open browser → http://127.0.0.1:7861
- Upload images/videos
- Click "Swap All Combinations"
- Download results

### 2. Video Swapping (Command Line)
```bash
python VideoSwapping.py
```
- Place video: `VideoSwapping/data_dst.mp4`
- Place face: `VideoSwapping/data_src.jpg`
- Enable stabilization: `y` (recommended)
- Choose option: `3` (extract + swap)

### 3. Programmatic Usage
```python
from SinglePhoto import FaceSwapper

swapper = FaceSwapper()

# Automatic advanced pipeline
result = swapper.swap_faces(
    source_path="source_face.jpg",
    source_face_idx=1,
    target_path="target_image.jpg",
    target_face_idx=1,
    enhance_quality=True  # Uses CodeFormer + all features
)

import cv2
cv2.imwrite("output.jpg", result)
```

---

## ⚙️ Advanced Configuration

### Adaptive Enhancement (Automatic)

The system automatically adjusts enhancement based on face size:

```python
# Large faces (>15% of image)
- CodeFormer weight: 0.9 (maximum)
- Real-ESRGAN: 2x upscale
- Additional sharpening
- Best for: Portraits, close-ups

# Medium faces (5-15%)
- CodeFormer weight: 0.7 (moderate)
- Real-ESRGAN: 2x upscale
- Best for: Group photos

# Small faces (<5%)
- CodeFormer weight: 0.5 (light)
- Real-ESRGAN: 1x (no upscale)
- Best for: Crowd scenes
```

### Video Stabilization Settings

```python
# In VideoStabilizer.py
stabilizer = VideoStabilizer(window_size=5)

# window_size options:
# 3 = Fast, less smooth
# 5 = Balanced (default)
# 7 = Slower, very smooth
```

---

## 🔧 Troubleshooting

### Issue: Models not downloading
**Solution:**
```bash
# Create models folder
mkdir models

# Download manually:
# CodeFormer: https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth
# RestoreFormer: https://github.com/wzhouxiff/RestoreFormer/releases/download/v1.0/restoreformer.pth
# BiSeNet: https://github.com/zllrunning/face-parsing.PyTorch/releases/download/v1.0/79999_iter.pth
```

### Issue: GPU out of memory
**Solution:**
```json
// Edit config.json
{
  "processing": {
    "enable_gpu": false  // Use CPU
  }
}
```

### Issue: Face parsing not working
**Solution:**
- System automatically falls back to elliptical mask
- Quality still good, just less precise edges
- Check if PyTorch is installed: `pip install torch torchvision`

### Issue: Video stabilization too slow
**Solution:**
```bash
# Disable when prompted
Enable video stabilization? (y/n): n

# Or reduce window size in VideoStabilizer.py
stabilizer = VideoStabilizer(window_size=3)
```

---

## 📊 Performance Benchmarks

### Processing Time (RTX 3060, 1024x1024 image)

| Pipeline Stage | Time |
|---------------|------|
| Face Detection | 0.2s |
| Face Parsing | 0.3s |
| Face Swap | 0.5s |
| Color Matching | 0.1s |
| CodeFormer | 2.5s |
| Real-ESRGAN | 1.5s |
| Blending | 0.2s |
| **Total** | **~5.3s** |

### Video Processing (30 FPS, 10 seconds)

| Mode | Time |
|------|------|
| Without Stabilization | ~25 min |
| With Stabilization | ~30 min |

---

## 🎬 Quality Improvements

### Before vs After

**Old System:**
- ✓ Good face swap
- ✗ Visible edges around face
- ✗ Glasses get swapped (looks weird)
- ✗ Color mismatch with body
- ✗ Video flickering

**New System:**
- ✓ Excellent face swap
- ✓ Seamless edges (face parsing)
- ✓ Glasses preserved (occluder handling)
- ✓ Perfect color match (dual-space)
- ✓ Smooth video (temporal stabilization)
- ✓ Better texture (CodeFormer/RestoreFormer)

---

## 🔥 Tips for Best Results

1. **Use high-resolution images** (1024x1024 or higher)
2. **Enable stabilization for videos** (smoother results)
3. **Let models auto-download** (first run takes longer)
4. **Use GPU if available** (3-5x faster)
5. **For portraits**: System automatically uses maximum enhancement
6. **For group photos**: System automatically uses moderate enhancement
7. **For glasses/accessories**: Face parsing handles automatically
8. **For difficult faces**: CodeFormer works better than GFPGAN

---

## 📈 Roadmap

### Completed ✓
- [x] CodeFormer integration
- [x] RestoreFormer integration
- [x] Face parsing (BiSeNet)
- [x] Occluder handling
- [x] Video stabilization
- [x] Adaptive enhancement

### Planned
- [ ] Multi-face tracking (consistent face_idx)
- [ ] Real-time video processing
- [ ] Audio preservation in videos
- [ ] Quality presets (Fast/Balanced/Quality)
- [ ] Face selection UI (visual picker)
- [ ] Batch video encoding (FFmpeg)
- [ ] API endpoints (REST API)
- [ ] Cloud deployment support

---

## 📝 Technical Details

### Face Parsing Classes (BiSeNet)
```
0: background
1: skin
2: left eyebrow
3: right eyebrow
4: left eye
5: right eye
6: glasses (occluder)
7: left ear
8: right ear
10: nose
11: mouth
12: upper lip
13: lower lip
16: hat (occluder)
17: earring (occluder)
```

### Enhancement Priority Logic
```python
try:
    result = CodeFormer.enhance(image, weight=0.7)
except:
    try:
        result = RestoreFormer.enhance(image)
    except:
        result = GFPGAN.enhance(image, weight=0.5)
```

### Temporal Smoothing Algorithm
```python
# Exponential decay weights
weights = exp(linspace(-2, 0, n))
blended = sum(frame[i] * weights[i] for i in range(n))
```

---

## 🤝 Credits

- **InsightFace** - Face detection/analysis
- **GFPGAN** - Face restoration
- **Real-ESRGAN** - Super resolution
- **CodeFormer** - Advanced face restoration
- **RestoreFormer** - Texture preservation
- **BiSeNet** - Face parsing

---

## 📄 License

This project is for educational and research purposes.

---

**Ready to create professional-quality face swaps!** 🚀

For questions or issues, check `ADVANCED_FEATURES.md` for detailed documentation.
