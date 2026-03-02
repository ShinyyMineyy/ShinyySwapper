# 🚀 QUICK START - Advanced Face Swapper

## ⚡ 3-Step Setup

### Step 1: Install Dependencies (5 minutes)
```bash
pip install -r requirements-advanced.txt
```

### Step 2: Run Application
```bash
START.bat
```

### Step 3: Use It!
- Browser opens automatically → http://127.0.0.1:7861
- Upload images → Click "Swap All Combinations"
- Done! ✅

---

## 🎯 What You Get

### Automatic Features (No Configuration Needed):
- ✅ **Face Parsing** - Precise edge blending
- ✅ **Occluder Handling** - Preserves glasses/accessories
- ✅ **CodeFormer** - Superior face restoration
- ✅ **RestoreFormer** - Texture preservation
- ✅ **Real-ESRGAN** - 2x super resolution
- ✅ **Adaptive Enhancement** - Adjusts to face size

### Video Features:
```bash
python VideoSwapping.py
```
- Place video: `VideoSwapping/data_dst.mp4`
- Place face: `VideoSwapping/data_src.jpg`
- Enable stabilization: `y` ← Prevents flickering!
- Choose: `3` (extract + swap)

---

## 📊 What Changed?

### Old System → New System

| Feature | Before | After |
|---------|--------|-------|
| Edge Quality | Good | Excellent (face parsing) |
| Glasses | Swapped (weird) | Preserved (natural) |
| Face Quality | GFPGAN | CodeFormer (better) |
| Video | Flickering | Smooth (stabilization) |
| Processing | 3-5 sec | 5-8 sec |

---

## 🔥 Pro Tips

1. **First run takes longer** (models download ~1.2GB)
2. **Use GPU** (3-5x faster than CPU)
3. **Enable stabilization for videos** (much smoother)
4. **High-res images = better results** (1024x1024+)
5. **System auto-adjusts quality** based on face size

---

## 📁 Quick Reference

### Input Folders:
```
SinglePhoto/
├── data_src.jpg    ← Your face
└── data_dst.jpg    ← Target image

VideoSwapping/
├── data_src.jpg    ← Your face
└── data_dst.mp4    ← Target video
```

### Output Folders:
```
BatchOutput/        ← Batch results
VideoOutput/        ← Video results
SinglePhoto/output/ ← Single image results
```

---

## 🆘 Troubleshooting

### Models not downloading?
```bash
# Check internet connection
# Or download manually to models/ folder
```

### GPU out of memory?
```json
// Edit config.json
{"processing": {"enable_gpu": false}}
```

### Too slow?
```python
# Disable enhancement
swapper.swap_faces(..., enhance_quality=False)
```

---

## 📖 Full Documentation

- **ADVANCED_FEATURES.md** - Feature details
- **README_ADVANCED.md** - Complete system docs
- **IMPLEMENTATION_SUMMARY.md** - What was added

---

## ✅ That's It!

**You're ready to create professional face swaps!** 🎬

Just run `START.bat` and start swapping! 🚀
