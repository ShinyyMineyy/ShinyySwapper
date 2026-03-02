# 🔄 MULTI-ACCOUNT TRAINING WORKFLOW

## Complete Step-by-Step Process

---

## 🎬 FIRST SESSION (Colab Account 1)

### What Happens:

**Step 1: Mount YOUR Google Drive**
```python
drive.mount('/content/drive')
```
- Signs into YOUR personal Google Drive (2TB)
- Creates connection between Colab and Drive

**Step 2: Download 80K Images (ONE TIME ONLY)**
```python
output_dir = '/content/drive/MyDrive/shinyyswapper_data'
# Downloads FFHQ + CelebA-HQ
```
- Downloads 80K images (~20GB)
- Saves to: `YOUR_DRIVE/shinyyswapper_data/`
- Takes 30-60 minutes
- **ONLY HAPPENS ONCE!** (Images stay in Drive forever)

**Step 3: Start Training**
```python
!python train.py
```
- Loads images from Drive
- Starts training from Epoch 0
- Every 500 steps (~30 min), saves checkpoint to Drive:
  - `YOUR_DRIVE/shinyyswapper_checkpoints/checkpoint_epoch_0.pt`
  - Contains: model weights, optimizer state, current progress

**Step 4: Training Runs for ~12 Hours**
- Progress: Epoch 0 → Epoch 12 (example)
- Checkpoints saved:
  - `checkpoint_epoch_0.pt`
  - `checkpoint_epoch_1.pt`
  - `checkpoint_epoch_2.pt`
  - ... up to `checkpoint_epoch_12.pt`

**Step 5: Session Expires**
- Colab disconnects after 12 hours
- Last checkpoint: `checkpoint_epoch_12.pt` (saved in YOUR Drive)
- Training stops

---

## 🔁 SECOND SESSION (Colab Account 2)

### What Happens:

**Step 1: Mount THE SAME Google Drive**
```python
drive.mount('/content/drive')
```
- Different Colab account
- But mounts YOUR SAME Google Drive (2TB)
- Sees all existing files:
  - `shinyyswapper_data/` (80K images already there!)
  - `shinyyswapper_checkpoints/` (12 checkpoints from Account 1)

**Step 2: Skip Download (Images Already Exist)**
- Script checks: "Do images exist in Drive?"
- YES! 80K images already there
- **Skips download** (saves 30-60 minutes!)

**Step 3: Start Training**
```python
!python train.py
```
- Script checks: "Are there checkpoints in Drive?"
- YES! Finds `checkpoint_epoch_12.pt`
- **Automatically loads it:**
  ```python
  checkpoint = torch.load('checkpoint_epoch_12.pt')
  G.load_state_dict(checkpoint['G_state'])
  start_epoch = checkpoint['epoch'] + 1  # = 13
  ```
- **Continues from Epoch 13** (not from scratch!)

**Step 4: Training Continues for ~12 Hours**
- Progress: Epoch 13 → Epoch 25
- New checkpoints saved:
  - `checkpoint_epoch_13.pt`
  - `checkpoint_epoch_14.pt`
  - ... up to `checkpoint_epoch_25.pt`

**Step 5: Session Expires**
- Last checkpoint: `checkpoint_epoch_25.pt`
- Training stops

---

## 🔁 THIRD SESSION (Colab Account 3)

### What Happens:

**Step 1: Mount THE SAME Google Drive**
- Same Drive, sees:
  - `shinyyswapper_data/` (80K images)
  - `shinyyswapper_checkpoints/` (25 checkpoints)

**Step 2: Start Training**
- Finds `checkpoint_epoch_25.pt`
- **Continues from Epoch 26**

**Step 3: Training Continues**
- Progress: Epoch 26 → Epoch 38
- Saves checkpoints up to `checkpoint_epoch_38.pt`

---

## 📊 VISUAL TIMELINE

```
DAY 1 (Account 1):
├─ Download 80K images → Drive
├─ Train: Epoch 0-12
└─ Save: checkpoint_epoch_12.pt → Drive

DAY 2 (Account 2):
├─ Mount Drive (images already there!)
├─ Load: checkpoint_epoch_12.pt
├─ Train: Epoch 13-25
└─ Save: checkpoint_epoch_25.pt → Drive

DAY 3 (Account 3):
├─ Mount Drive
├─ Load: checkpoint_epoch_25.pt
├─ Train: Epoch 26-38
└─ Save: checkpoint_epoch_38.pt → Drive

... Continue until Epoch 100
```

---

## 🔑 KEY POINTS

### ✅ What Gets Saved to Drive:
1. **Training images** (80K) - Downloaded ONCE, used forever
2. **Checkpoints** (every 500 steps) - Contains ALL training progress
3. **Final model** (after 100 epochs) - Your trained ShinyySwapper

### ✅ What Gets Loaded from Drive:
1. **Training images** - Every session reads from Drive
2. **Latest checkpoint** - Auto-resumes from last saved state

### ✅ What's Automatic:
- Checkpoint saving (every 500 steps)
- Checkpoint loading (finds latest automatically)
- Skipping download if images exist
- Resuming from correct epoch

### ❌ What You DON'T Need to Do:
- ❌ Manually download checkpoints
- ❌ Manually upload checkpoints
- ❌ Tell it which checkpoint to load
- ❌ Re-download images each session
- ❌ Track which epoch you're on

---

## 🎯 SIMPLE WORKFLOW

**Every New Session (Any Account):**
1. Open Colab notebook
2. Mount YOUR Google Drive
3. Run all cells
4. Training auto-continues from where it left off
5. Wait 12 hours
6. Repeat with next account

**That's it!** The code handles everything automatically.

---

## 📁 YOUR GOOGLE DRIVE STRUCTURE

```
Google Drive (2TB)/
└── MyDrive/
    ├── shinyyswapper_data/              [20GB - Downloaded once]
    │   ├── 00001.jpg
    │   ├── 00002.jpg
    │   └── ... (80,000 images)
    │
    ├── shinyyswapper_checkpoints/       [10GB - Grows over time]
    │   ├── checkpoint_epoch_0.pt        [500MB]
    │   ├── checkpoint_epoch_1.pt        [500MB]
    │   ├── checkpoint_epoch_2.pt        [500MB]
    │   └── ... (up to epoch 100)
    │
    └── shinyyswapper_model.onnx         [200MB - Final export]
```

---

## 🔍 HOW TO CHECK PROGRESS

**In Google Drive (from phone/computer):**
1. Open `MyDrive/shinyyswapper_checkpoints/`
2. See latest checkpoint file
3. Filename shows current epoch: `checkpoint_epoch_47.pt` = Epoch 47

**In Colab (while training):**
```
Epoch 47: 100%|██████████| 10000/10000 [2:15:30<00:00]
d_loss: 0.234, g_loss: 1.456, id_loss: 0.123
Saved checkpoint: checkpoint_epoch_47.pt
```

---

## ⚡ QUICK REFERENCE

| Session | Account | Action | Epoch Range |
|---------|---------|--------|-------------|
| 1 | Account 1 | Download images + Train | 0-12 |
| 2 | Account 2 | Load checkpoint + Train | 13-25 |
| 3 | Account 3 | Load checkpoint + Train | 26-38 |
| 4 | Account 1 | Load checkpoint + Train | 39-51 |
| 5 | Account 2 | Load checkpoint + Train | 52-64 |
| 6 | Account 3 | Load checkpoint + Train | 65-77 |
| 7 | Account 1 | Load checkpoint + Train | 78-90 |
| 8 | Account 2 | Load checkpoint + Train | 91-100 |
| 9 | Any | Export model | DONE! |

**Total: ~8-10 sessions across 10-12 days**
