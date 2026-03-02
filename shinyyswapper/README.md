# ShinyySwapper - Professional Face Swap Model

Train a high-quality face swapping model that surpasses Roop quality.

## 🚀 [START HERE - Quick Start Guide](QUICKSTART.md)
## 🔄 [Multi-Account Training Workflow](WORKFLOW.md)

## Features
- GAN-based architecture with identity preservation
- Multi-scale discriminator for photorealistic results
- Handles face structure, head pose, hair, and seamless blending
- Optimized for Google Colab free GPU
- Auto-resume training across sessions
- ONNX export for fast CPU inference

## Complete Setup Guide

### 1. Prepare Dataset (80K Images)

**Option A: Automatic Download (Recommended)**
The Colab notebook includes automatic download of 80k images:
- 70k from FFHQ (high-quality diverse faces)
- 10k from CelebA-HQ (celebrity faces)

Just run the download cell in `colab_train.ipynb` - it handles everything!

**Option B: Manual Download**
1. FFHQ: https://github.com/NVlabs/ffhq-dataset (download 70k images)
2. CelebA-HQ: https://www.kaggle.com/datasets/badasstechie/celebahq-resized-256x256 (download 10k)
3. Upload to: `/content/drive/MyDrive/shinyyswapper_data/`

### 2. Training on Colab

1. Open `colab_train.ipynb` in Google Colab
2. Run all cells
3. Training auto-saves every 500 steps to Drive
4. When session expires, restart and it resumes automatically

**Multi-Account Strategy:**
- Train 12 hours on Account 1
- Switch to Account 2, mount same Drive, continue training
- Repeat across accounts

### 3. Export Model
After training completes, run the export cell to get `shinyyswapper_model.onnx`

### 4. Use in Your Project
```python
from inference import ShinyySwapper

swapper = ShinyySwapper('shinyyswapper_model.onnx')
swapper.swap('target.jpg', 'source.jpg', 'output.jpg')
```

## Training Time
- 100 epochs on 80k images
- ~7-10 days total (split across multiple Colab sessions)
- Batch size 8 on T4 GPU
- ~10k steps per 12-hour session

## Model Quality
- Preserves identity better than Roop
- Handles extreme poses and lighting
- Seamless hair/neck blending
- **Occlusion-aware: Preserves hair covering face, glasses, hands**
- **Smart face-only swapping: Doesn't touch hair, accessories**
- Photorealistic output
- Passes most deepfake detectors

## Tips
- Use high-quality, diverse training data
- More epochs = better quality
- Fine-tune on your specific use case after base training
