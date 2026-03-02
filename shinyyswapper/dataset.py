import torch
from torch.utils.data import Dataset
import cv2
import numpy as np
from pathlib import Path
import albumentations as A

class FaceSwapDataset(Dataset):
    def __init__(self, data_root, img_size=256):
        self.data_root = Path(data_root)
        self.img_paths = list(self.data_root.rglob("*.jpg")) + list(self.data_root.rglob("*.png"))
        self.img_size = img_size
        
        self.transform = A.Compose([
            A.Resize(img_size, img_size),
            A.HorizontalFlip(p=0.5),
            A.Rotate(limit=15, p=0.3),  # Handle head rotation
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.5),
            A.GaussNoise(p=0.3),
            A.RandomBrightnessContrast(p=0.3),
            A.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
    
    def __len__(self):
        return len(self.img_paths)
    
    def __getitem__(self, idx):
        img = cv2.imread(str(self.img_paths[idx]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Get random pair for swapping
        idx2 = np.random.randint(0, len(self.img_paths))
        img2 = cv2.imread(str(self.img_paths[idx2]))
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
        
        img = self.transform(image=img)['image']
        img2 = self.transform(image=img2)['image']
        
        return {
            'target': torch.FloatTensor(img).permute(2, 0, 1),
            'source': torch.FloatTensor(img2).permute(2, 0, 1),
            'target_path': str(self.img_paths[idx])
        }
