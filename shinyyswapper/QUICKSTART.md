# 🚀 SHINYYSWAPPER - QUICK START GUIDE

## Step 1: Upload Files to GitHub (5 minutes)

1. Create a new GitHub repository (public or private)
2. Upload these files from your project:
   - `train.py`
   - `model.py`
   - `dataset.py`
   - `inference.py`
   - `requirements.txt`
   - `colab_train.ipynb`

## Step 2: Open Google Colab (2 minutes)

1. Go to: https://colab.research.google.com
2. Click: **File → Upload notebook**
3. Upload `colab_train.ipynb` OR
4. Click: **File → Open notebook → GitHub** and paste your repo URL

## Step 3: Start Training (Click & Go!)

### First Time Setup:

**Cell 1: Mount Google Drive**
```python
from google.colab import drive
drive.mount('/content/drive')
```
- Click ▶️ Run
- Sign in with your Google account
- Allow access

**Cell 2: Install Dependencies**
```python
!pip install -q torch torchvision opencv-python insightface onnxruntime-gpu albumentations kornia lpips facexlib gfpgan gdown scipy
```
- Click ▶️ Run
- Wait 2-3 minutes

**Cell 3: Download 80K Images** (AUTOMATIC!)
```python
# This downloads FFHQ + CelebA-HQ automatically
```
- Click ▶️ Run
- Wait 30-60 minutes (downloads 80K images to your Drive)
- ☕ Take a break!

**Cell 4: Clone Your Code**
```python
!git clone https://github.com/YOUR_USERNAME/ShinyySwapper.git /content/shinyyswapper
%cd /content/shinyyswapper
```
- Replace `YOUR_USERNAME` with your GitHub username
- Click ▶️ Run

**Cell 5: Check GPU**
```python
!nvidia-smi
```
- Click ▶️ Run
- Should show: Tesla T4 (free GPU)

**Cell 6: START TRAINING!** 🎉
```python
!python train.py
```
- Click ▶️ Run
- Training begins!
- Auto-saves every 500 steps to your Drive

## Step 4: Monitor Progress

Watch the output:
```
Epoch 0: 100%|██████████| 10000/10000 [2:15:30<00:00]
d_loss: 0.234, g_loss: 1.456, id_loss: 0.123
Saved checkpoint: checkpoint_epoch_0.pt
```

## Step 5: Switch Accounts (After ~12 hours)

When Colab disconnects:

1. **Open new Colab account** (different Gmail)
2. **Mount YOUR SAME Google Drive** (your 2TB Drive)
3. **Run all cells again**
4. Training **auto-resumes** from last checkpoint!

Repeat across multiple accounts for 10-12 days.

## Step 6: Export Model (After Training)

**Cell 7: Export to ONNX**
```python
# Run this cell after 100 epochs complete
```
- Click ▶️ Run
- Downloads `shinyyswapper_model.onnx` to your Drive

## Step 7: Use Your Model

Download `shinyyswapper_model.onnx` from Drive, then:

```python
from inference import ShinyySwapper

swapper = ShinyySwapper('shinyyswapper_model.onnx')
swapper.swap('target.jpg', 'source.jpg', 'output.jpg')
```

---

## 📊 Timeline

| Day | Action |
|-----|--------|
| Day 0 | Upload to GitHub, start Colab, download dataset |
| Day 1-10 | Training (switch accounts every 12hrs) |
| Day 11 | Export model, test results |
| Day 12+ | Use in your face swap project! |

---

## ⚠️ Troubleshooting

**"No GPU available"**
- Go to: Runtime → Change runtime type → GPU → T4

**"Session expired"**
- Normal! Just restart and run all cells again
- Training resumes automatically

**"Out of memory"**
- Reduce batch_size in train.py (line 89): `'batch_size': 2`

**"No faces detected"**
- Make sure images contain clear, visible faces
- Remove corrupted images from dataset

---

## 🎯 You're Ready!

Just follow the cells in order. The notebook does everything automatically!
