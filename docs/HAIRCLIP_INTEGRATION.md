# 🎨 HairCLIP Integration Guide

## 📦 Setup

### Step 1: Clone Repositories
```bash
python setup_hairclip.py
```

This will:
- Clone `change-hairstyle-ai` from GitHub
- Clone `HairCLIPv2` from GitHub
- Install dependencies
- Create integration wrapper

### Step 2: Verify Installation
```bash
python -c "from HairCLIPIntegration import HairCLIPIntegration; print('✓ HairCLIP ready')"
```

---

## 🚀 Usage

### Option 1: Standard Pipeline (No HairCLIP)
```bash
python EnhancedHairPipeline.py --source face.jpg --target hair.jpg --output result.jpg
```

### Option 2: With HairCLIP Text Editing
```bash
python EnhancedHairPipeline.py \
    --source face.jpg \
    --target hair.jpg \
    --output result.jpg \
    --use-hairclip \
    --prompt "long curly blonde hair"
```

### Option 3: Python API
```python
from EnhancedHairPipeline import EnhancedHairPipeline

pipeline = EnhancedHairPipeline()

# Standard
result = pipeline.process_standard("face.jpg", "hair.jpg", "result.jpg")

# With HairCLIP
result = pipeline.process_with_hairclip(
    "face.jpg", "hair.jpg", "result.jpg",
    hair_text_prompt="short wavy hair"
)
```

---

## 🎯 Features

### Standard Pipeline
1. Face swap (inswapper)
2. Hair segmentation (BiSeNet/color-based)
3. Hair transfer (alignment + blending)
4. Color correction
5. Seamless blending

### Enhanced with HairCLIP
1. Face swap
2. Hair segmentation
3. **HairCLIP text-based editing** ← NEW
4. Hair transfer
5. Color correction
6. Seamless blending

---

## 📊 HairCLIP Capabilities

### Text Prompts
```python
# Change hair length
"long hair"
"short hair"
"shoulder-length hair"

# Change hair style
"curly hair"
"straight hair"
"wavy hair"

# Change hair color
"blonde hair"
"brown hair"
"red hair"
"black hair"

# Combinations
"long curly blonde hair"
"short straight black hair"
```

### Style Transfer
```python
# Transfer hair style from one image to another
pipeline.hairclip.transfer_hair_style(source_img, target_img)
```

---

## 🔧 Architecture

```
EnhancedHairPipeline
├── FaceSwapper (inswapper)
├── HairSegmenter (BiSeNet)
├── HairTransfer (alignment + blending)
└── HairCLIPIntegration (optional)
    ├── change-hairstyle-ai
    └── HairCLIPv2
```

---

## 📁 Directory Structure

```
Shinyy's Mukhosh Changer/
├── external/
│   ├── change-hairstyle-ai/     ← Cloned repo
│   └── HairCLIPv2/               ← Cloned repo
│
├── setup_hairclip.py             ← Setup script
├── HairCLIPIntegration.py        ← Wrapper (auto-generated)
├── EnhancedHairPipeline.py       ← Main pipeline
│
└── models/
    └── hairclip/                 ← Models (auto-download)
```

---

## 🎨 Examples

### Example 1: Basic Hair Transfer
```bash
python EnhancedHairPipeline.py \
    --source my_face.jpg \
    --target celebrity_hair.jpg \
    --output result.jpg
```

### Example 2: Text-Based Hair Editing
```bash
python EnhancedHairPipeline.py \
    --source my_face.jpg \
    --target any_image.jpg \
    --output result.jpg \
    --use-hairclip \
    --prompt "long wavy red hair"
```

### Example 3: Batch Processing
```python
from EnhancedHairPipeline import EnhancedHairPipeline

pipeline = EnhancedHairPipeline()

prompts = [
    "long straight hair",
    "short curly hair",
    "shoulder-length wavy hair"
]

for i, prompt in enumerate(prompts):
    result = pipeline.process_with_hairclip(
        "face.jpg", "hair.jpg", f"result_{i}.jpg",
        hair_text_prompt=prompt
    )
```

---

## 🔬 Technical Details

### HairCLIP Models
- **CLIP**: Text-image embedding
- **StyleGAN2**: Hair generation
- **Face Parsing**: Hair segmentation
- **Mapper Network**: Latent space manipulation

### Processing Flow
```
Input Image
    ↓
Face Detection
    ↓
Face Swap
    ↓
Hair Segmentation
    ↓
[Optional] HairCLIP Editing ← Text prompt
    ↓
Hair Alignment
    ↓
Color Correction
    ↓
Poisson Blending
    ↓
Output Image
```

---

## 🐛 Troubleshooting

### Issue: Repos not cloned
```bash
python setup_hairclip.py
```

### Issue: Import errors
```bash
pip install clip-by-openai ftfy regex
```

### Issue: CUDA out of memory
```python
# Use CPU mode
pipeline = EnhancedHairPipeline()
pipeline.hairclip.device = 'cpu'
```

### Issue: HairCLIP not working
```bash
# Fallback to standard pipeline
python EnhancedHairPipeline.py --source face.jpg --target hair.jpg
```

---

## 📊 Performance

### Standard Pipeline
- Processing time: ~6-10s per image
- Memory: ~2GB GPU / 4GB CPU

### With HairCLIP
- Processing time: ~15-20s per image
- Memory: ~4GB GPU / 8GB CPU
- First run: +model download time

---

## 🎯 Use Cases

1. **Virtual Hair Try-On**
   - Try different hairstyles with text prompts
   - No need for reference images

2. **Face Swap + Hair Editing**
   - Swap face and edit hair simultaneously
   - Full control over final appearance

3. **Hair Style Transfer**
   - Extract hair style from one image
   - Apply to another face

4. **Creative Editing**
   - Experiment with different looks
   - Generate variations quickly

---

## 📝 API Reference

### EnhancedHairPipeline

```python
class EnhancedHairPipeline:
    def process_standard(source, target, output):
        """Standard pipeline without HairCLIP"""
    
    def process_with_hairclip(source, target, output, hair_text_prompt):
        """Enhanced pipeline with HairCLIP text editing"""
```

### HairCLIPIntegration

```python
class HairCLIPIntegration:
    def edit_hair(image, text_prompt):
        """Edit hair using text description"""
    
    def transfer_hair_style(source_img, target_img):
        """Transfer hair style between images"""
    
    def extract_hair_latent(image):
        """Extract hair latent code"""
```

---

## 🤝 Credits

- **change-hairstyle-ai**: https://github.com/Pwntus/change-hairstyle-ai
- **HairCLIPv2**: https://github.com/wty-ustc/HairCLIPv2
- **CLIP**: OpenAI
- **StyleGAN2**: NVIDIA

---

## 📄 License

This integration is for educational and research purposes.

---

**Ready to use HairCLIP!** 🚀

Run: `python setup_hairclip.py` to get started!
