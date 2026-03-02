# 🚀 HAIR TRANSFER - QUICK START

## ⚡ 3-Step Usage

### Step 1: Prepare Images
- **Source Face**: Image with face you want to use
- **Target Hair**: Image with hair you want to extract

### Step 2: Run
```bash
python FaceSwapHairTransfer.py source_face.jpg target_hair.jpg result.jpg
```

### Step 3: Done!
Result saved to `result.jpg` ✅

---

## 🎨 Web Interface

```bash
python app.py
```
1. Go to "💇 Hair Transfer" tab
2. Upload source face image
3. Upload target hair image
4. Click "🔥 Swap Face + Transfer Hair"
5. Download result!

---

## 📊 What It Does

```
Source Face    Target Hair
    ↓              ↓
    └──────┬───────┘
           ↓
    Face Swap + Hair Transfer
           ↓
    Final Result
    (Face from source + Hair from target)
```

---

## 💡 Examples

### Example 1: Try Different Hairstyles
```bash
python FaceSwapHairTransfer.py my_face.jpg long_hair.jpg result_long.jpg
python FaceSwapHairTransfer.py my_face.jpg short_hair.jpg result_short.jpg
python FaceSwapHairTransfer.py my_face.jpg curly_hair.jpg result_curly.jpg
```

### Example 2: Batch Processing
```python
from FaceSwapHairTransfer import FaceSwapHairTransfer

pipeline = FaceSwapHairTransfer()

faces = ["face1.jpg", "face2.jpg"]
hairs = ["hair1.jpg", "hair2.jpg", "hair3.jpg"]

# Generates 6 combinations
results = pipeline.process_batch(faces, hairs)
```

---

## 🔧 Requirements

✅ Already installed in your system:
- torch
- opencv-python
- insightface
- numpy

No additional setup needed!

---

## 📁 Output

Results saved to:
- `HairTransferOutput/` (batch mode)
- Custom path (single mode)

---

## 🎯 Tips

1. **Best Results:**
   - Use frontal face images
   - Clear hair visibility
   - Similar lighting conditions

2. **Multiple Faces:**
   ```bash
   # Use 2nd face in source, 1st face in target
   python FaceSwapHairTransfer.py face.jpg hair.jpg result.jpg 2 1
   ```

3. **Quality Enhancement:**
   - Automatically applies GFPGAN
   - Color correction included
   - Seamless blending

---

## 🐛 Troubleshooting

**Hair not detected?**
- Use images with visible hair
- Try different lighting

**Misalignment?**
- Ensure faces are clearly visible
- Use frontal images

**Color mismatch?**
- System auto-corrects
- Try similar lighting conditions

---

## 📖 Full Documentation

See `HAIR_TRANSFER_README.md` for:
- Complete API reference
- Technical details
- Advanced usage
- Troubleshooting guide

---

**Ready to transfer hair!** 💇🚀

Just run: `python FaceSwapHairTransfer.py source.jpg target.jpg output.jpg`
