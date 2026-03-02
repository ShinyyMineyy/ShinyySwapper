"""
ShinyySwapper - Automated Dataset Downloader (Kaggle Version)
Gets 80K images for professional training
Run this in Google Colab to download datasets directly to Drive
"""

import os
import shutil
from pathlib import Path
from tqdm import tqdm

def download_datasets(output_dir='/content/drive/MyDrive/shinyyswapper_data'):
    """Downloads FFHQ (70k) + CelebA-HQ (10k subset) = 80k images from Kaggle"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("📥 Downloading FFHQ Dataset (70k images) from Kaggle...")
    os.system('kaggle datasets download -d denislukovnikov/ffhq256 -p /content --unzip')
    
    print("📦 Moving FFHQ images...")
    ffhq_path = Path('/content/ffhq256')
    if ffhq_path.exists():
        for img in tqdm(list(ffhq_path.rglob('*.png')) + list(ffhq_path.rglob('*.jpg'))):
            shutil.copy(img, output_dir)
        shutil.rmtree(ffhq_path)
    
    print("📥 Downloading CelebA-HQ (30k images, using 10k) from Kaggle...")
    os.system('kaggle datasets download -d badasstechie/celebahq-resized-256x256 -p /content --unzip')
    
    print("📦 Copying 10k CelebA images...")
    celeba_temp = Path('/content/celeba_hq_256')
    if not celeba_temp.exists():
        celeba_temp = Path('/content')
    
    celeba_images = sorted(list(celeba_temp.rglob("*.jpg")))[:10000]
    for img in tqdm(celeba_images, desc='Copying CelebA'):
        shutil.copy(img, output_dir)
    
    # Cleanup
    if Path('/content/celeba_hq_256').exists():
        shutil.rmtree('/content/celeba_hq_256')
    
    # Verify count
    total_images = len(list(Path(output_dir).rglob("*.jpg"))) + len(list(Path(output_dir).rglob("*.png")))
    print(f"\n✅ Dataset ready: {total_images} images in {output_dir}")
    print(f"💾 Total size: ~{sum(f.stat().st_size for f in Path(output_dir).rglob('*') if f.is_file()) / 1e9:.1f} GB")
    
    return total_images

if __name__ == '__main__':
    # Install kaggle if not available
    os.system('pip install -q kaggle')
    
    download_datasets()
