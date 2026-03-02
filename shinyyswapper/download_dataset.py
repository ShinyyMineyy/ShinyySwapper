"""
ShinyySwapper - Automated Dataset Downloader
Gets 80K images for professional training
Run this in Google Colab to download datasets directly to Drive
"""

import os
import shutil
from pathlib import Path
import gdown
import zipfile
from tqdm import tqdm

def download_datasets(output_dir='/content/drive/MyDrive/shinyyswapper_data'):
    """Downloads FFHQ (70k) + CelebA-HQ (10k subset) = 80k images"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("📥 Downloading FFHQ Dataset (70k images)...")
    # FFHQ thumbnails 128x128 (smaller download, will be resized during training)
    ffhq_url = "https://drive.google.com/uc?id=1WocxvZ3N0JZ_O8kU_ALLVoiFRMwrVo7Y"
    ffhq_zip = "/content/ffhq.zip"
    gdown.download(ffhq_url, ffhq_zip, quiet=False)
    
    print("📦 Extracting FFHQ...")
    with zipfile.ZipFile(ffhq_zip, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    os.remove(ffhq_zip)
    
    print("📥 Downloading CelebA-HQ (30k images, using 10k)...")
    # CelebA-HQ from Kaggle mirror
    celeba_url = "https://drive.google.com/uc?id=1badu11NqxGf6qM3PTTooQDJvQbejgbTv"
    celeba_zip = "/content/celeba.zip"
    gdown.download(celeba_url, celeba_zip, quiet=False)
    
    print("📦 Extracting CelebA-HQ...")
    celeba_temp = "/content/celeba_temp"
    with zipfile.ZipFile(celeba_zip, 'r') as zip_ref:
        zip_ref.extractall(celeba_temp)
    os.remove(celeba_zip)
    
    # Copy only first 10k images from CelebA
    celeba_images = sorted(list(Path(celeba_temp).rglob("*.jpg")))[:10000]
    print(f"📋 Copying 10k CelebA images...")
    for img in tqdm(celeba_images):
        shutil.copy(img, output_dir)
    
    shutil.rmtree(celeba_temp)
    
    # Verify count
    total_images = len(list(Path(output_dir).rglob("*.jpg"))) + len(list(Path(output_dir).rglob("*.png")))
    print(f"\n✅ Dataset ready: {total_images} images in {output_dir}")
    print(f"💾 Total size: ~{sum(f.stat().st_size for f in Path(output_dir).rglob('*') if f.is_file()) / 1e9:.1f} GB")
    
    return total_images

if __name__ == '__main__':
    # Install gdown if not available
    os.system('pip install -q gdown')
    
    download_datasets()
