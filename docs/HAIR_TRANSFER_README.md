# 💇 Face Swap + Hair Transfer System

## 🎯 Overview

Complete pipeline that combines **face swapping** with **hair transplant**:
1. Extract face from source image
2. Extract hair from target image  
3. Swap face into target
4. Transfer hair onto swapped result
5. Blend seamlessly with color correction

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install torch torchvision opencv-python insightface

# Already installed in your venv
```

### Usage

#### Option 1: Web Interface (Easiest)
```bash
python app.py
```
- Go to "💇 Hair Transfer" tab
- Upload source face image
- Upload target hair image
- Click "🔥 Swap Face + Transfer Hair"

#### Option 2: Command Line
```bash
python FaceSwapHairTransfer.py source_face.jpg target_hair.jpg output.jpg
```

#### Option 3: Python Script
```python
from FaceSwapHairTransfer import FaceSwapHairTransfer

pipeline = FaceSwapHairTransfer()
result = pipeline.process(
    source_face_path="face.jpg",
    target_hair_path="hair.jpg",
    output_path="result.jpg"
)
```

---

## 📊 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT IMAGES                              │
│  Source Face Image          Target Hair Image                │
└─────────────┬───────────────────────┬───────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│  Face Detection         │  │  Hair Segmentation           │
│  (InsightFace)          │  │  (BiSeNet / Color-based)     │
│  - Detect face bbox     │  │  - Extract hair mask         │
│  - Get landmarks        │  │  - Isolate hair pixels       │
└─────────────┬───────────┘  └──────────────┬───────────────┘
              │                               │
              ▼                               │
┌─────────────────────────────────────────────┐              │
│  Face Swap (inswapper)                      │              │
│  - Swap source face → target                │              │
│  - Color matching                           │              │
│  - Enhancement (GFPGAN)                     │              │
└─────────────┬───────────────────────────────┘              │
              │                                              │
              │  ◄───────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Hair Alignment                                              │
│  - Scale hair to match face size                            │
│  - Translate to match face position                         │
│  - Warp transformation                                      │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Color Correction                                            │
│  - Match hair lighting to face                              │
│  - LAB color space adjustment                               │
│  - Preserve hair texture                                    │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│  Seamless Blending                                           │
│  - Poisson blending                                         │
│  - Alpha blending with smooth mask                          │
│  - Edge refinement                                          │
└─────────────┬───────────────────────────────────────────────┘
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT IMAGE                              │
│  Face from source + Hair from target                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Modules

### 1. HairSegmenter.py
**Purpose:** Extract hair region from images

**Features:**
- BiSeNet model for precise segmentation (if available)
- Color-based fallback (HSV thresholding)
- Morphological operations for cleanup
- Smooth edge detection

**Methods:**
```python
segmenter = HairSegmenter()
hair_mask = segmenter.segment_hair(image)
hair_region, mask = segmenter.extract_hair_region(image, hair_mask)
```

### 2. HairTransfer.py
**Purpose:** Transfer hair onto face-swapped image

**Features:**
- Affine transformation for alignment
- Scale and position matching
- LAB color space correction
- Poisson seamless cloning
- Alpha blending fallback

**Methods:**
```python
transfer = HairTransfer()
result = transfer.transfer_hair(
    face_swapped_img, hair_img, hair_mask,
    target_bbox, source_bbox
)
```

### 3. FaceSwapHairTransfer.py
**Purpose:** Complete integrated pipeline

**Features:**
- End-to-end processing
- Batch processing support
- Error handling
- Progress logging

**Methods:**
```python
pipeline = FaceSwapHairTransfer()

# Single image
result = pipeline.process(source, target, output)

# Batch processing
results = pipeline.process_batch(source_list, target_list)
```

---

## 📁 File Structure

```
Shinyy's Mukhosh Changer/
│
├── Core Modules
│   ├── SinglePhoto.py              # Face swapper
│   ├── HairSegmenter.py            # Hair extraction
│   ├── HairTransfer.py             # Hair overlay
│   └── FaceSwapHairTransfer.py     # Integrated pipeline
│
├── UI
│   └── app.py                      # Gradio interface (with Hair Transfer tab)
│
├── Output
│   └── HairTransferOutput/         # Results saved here
│
└── Documentation
    └── HAIR_TRANSFER_README.md     # This file
```

---

## 🎨 Examples

### Example 1: Basic Usage
```python
from FaceSwapHairTransfer import FaceSwapHairTransfer

pipeline = FaceSwapHairTransfer()
result = pipeline.process(
    source_face_path="person_a_face.jpg",
    target_hair_path="person_b_hair.jpg",
    output_path="result.jpg"
)
```

### Example 2: Batch Processing
```python
pipeline = FaceSwapHairTransfer()

sources = ["face1.jpg", "face2.jpg"]
targets = ["hair1.jpg", "hair2.jpg", "hair3.jpg"]

# Generates 6 combinations (2 faces × 3 hairs)
results = pipeline.process_batch(sources, targets)
```

### Example 3: Custom Settings
```python
result = pipeline.process(
    source_face_path="face.jpg",
    target_hair_path="hair.jpg",
    output_path="result.jpg",
    source_face_idx=1,      # First face in source
    target_face_idx=1,      # First face in target
    enhance_quality=True    # Apply GFPGAN
)
```

---

## 🔬 Technical Details

### Hair Segmentation Methods

#### Method 1: BiSeNet (Best Quality)
- Uses face parsing model
- 19-class segmentation
- Hair class = 17
- Requires model file (~50MB)

#### Method 2: Color-Based (Fallback)
- HSV color space
- Dark region detection (black/brown hair)
- Morphological operations
- Works without model

### Alignment Algorithm

```python
# Calculate scale
scale = (source_face_size / target_face_size)

# Calculate translation
tx = source_center_x - target_center_x * scale
ty = source_center_y - target_center_y * scale

# Transformation matrix
M = [[scale, 0, tx],
     [0, scale, ty]]

# Apply
aligned = cv2.warpAffine(hair, M, output_size)
```

### Color Correction

```python
# Convert to LAB
hair_lab = cv2.cvtColor(hair, cv2.COLOR_BGR2LAB)
target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB)

# Match L channel (lightness)
ratio = target_L_mean / hair_L_mean
hair_lab[:,:,0] *= ratio

# Convert back
corrected = cv2.cvtColor(hair_lab, cv2.COLOR_LAB2BGR)
```

### Blending Methods

#### Poisson Blending (Primary)
```python
result = cv2.seamlessClone(
    hair_img, base_img, mask,
    center, cv2.NORMAL_CLONE
)
```

#### Alpha Blending (Fallback)
```python
mask_3ch = cv2.merge([mask, mask, mask])
result = hair * mask_3ch + base * (1 - mask_3ch)
```

---

## ⚙️ Configuration

### Hair Segmentation Settings
```python
# In HairSegmenter.py

# Color-based thresholds
lower_dark = np.array([0, 0, 0])
upper_dark = np.array([180, 255, 100])

# Morphological kernel size
kernel_size = (15, 15)

# Gaussian blur for smoothing
blur_size = (21, 21)
```

### Blending Settings
```python
# In HairTransfer.py

# Mask dilation iterations
dilation_iterations = 2

# Gaussian blur for mask
blur_kernel = (31, 31)

# Lightness adjustment limits
min_ratio = 0.7
max_ratio = 1.3
```

---

## 🐛 Troubleshooting

### Issue: Hair not detected
**Solution:**
- Use images with clear hair visibility
- Adjust color thresholds in HairSegmenter
- Try different lighting conditions

### Issue: Misalignment
**Solution:**
- Ensure faces are clearly visible
- Use frontal face images
- Check face detection bbox

### Issue: Color mismatch
**Solution:**
- Increase color correction strength
- Match lighting conditions
- Use similar image qualities

### Issue: Blending artifacts
**Solution:**
- Increase mask blur size
- Use Poisson blending (automatic)
- Refine hair mask edges

---

## 📊 Performance

### Processing Time (per image)
- Hair segmentation: ~0.5s
- Face swap: ~5-8s
- Hair transfer: ~1s
- **Total: ~6-10s**

### Quality Factors
- ✅ Face detection accuracy
- ✅ Hair segmentation precision
- ✅ Alignment accuracy
- ✅ Color matching quality
- ✅ Blending seamlessness

---

## 🎯 Use Cases

1. **Virtual Hairstyle Try-On**
   - Try different hairstyles on your face
   - Preview before actual haircut

2. **Photo Editing**
   - Swap faces while keeping original hair
   - Create composite portraits

3. **Entertainment**
   - Face swap with hair transplant
   - Create funny combinations

4. **Research**
   - Face attribute transfer
   - Hairstyle analysis

---

## 🔮 Future Improvements

- [ ] Real-time processing
- [ ] Hair color editing
- [ ] Hair style transfer (curly ↔ straight)
- [ ] Multiple hair regions
- [ ] 3D hair modeling
- [ ] Video support
- [ ] Mobile app

---

## 📝 API Reference

### FaceSwapHairTransfer

```python
class FaceSwapHairTransfer:
    def __init__(self):
        """Initialize pipeline with all modules"""
    
    def process(self, source_face_path, target_hair_path, 
                output_path=None, source_face_idx=1, 
                target_face_idx=1, enhance_quality=True):
        """
        Process single image pair
        
        Args:
            source_face_path: Path to source face image
            target_hair_path: Path to target hair image
            output_path: Where to save result
            source_face_idx: Which face in source (1-indexed)
            target_face_idx: Which face in target (1-indexed)
            enhance_quality: Apply GFPGAN enhancement
        
        Returns:
            numpy.ndarray: Final result image
        """
    
    def process_batch(self, source_faces, target_hairs, 
                     output_dir="HairTransferOutput"):
        """
        Process multiple combinations
        
        Args:
            source_faces: List of source image paths
            target_hairs: List of target image paths
            output_dir: Output directory
        
        Returns:
            list: Paths to generated images
        """
```

---

## 🤝 Credits

- **InsightFace** - Face detection
- **inswapper** - Face swapping
- **BiSeNet** - Face parsing (optional)
- **OpenCV** - Image processing
- **GFPGAN** - Face enhancement

---

## 📄 License

This project is for educational and research purposes.

---

**Ready to swap faces and transfer hair!** 🚀💇

For questions or issues, check the main README or create an issue.
