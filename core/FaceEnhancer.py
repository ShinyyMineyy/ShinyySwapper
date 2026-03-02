"""
Face Enhancement Pipeline - GFPGAN + Real-ESRGAN
Makes swapped faces photorealistic
"""

import cv2
import numpy as np
import os
import torch

class FaceEnhancer:
    def __init__(self):
        self.gfpgan = None
        self.realesrgan = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._load_models()
    
    def _load_models(self):
        """Load GFPGAN and Real-ESRGAN models"""
        try:
            from gfpgan import GFPGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            print("Loading enhancement models...")
            
            # GFPGAN for face restoration
            model_path = os.path.join('models', 'GFPGANv1.4.pth')
            os.makedirs('models', exist_ok=True)
            
            if not os.path.exists(model_path):
                print("Downloading GFPGAN model (~350MB)...")
                import urllib.request
                url = 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth'
                urllib.request.urlretrieve(url, model_path)
                print("✓ GFPGAN downloaded")
            
            self.gfpgan = GFPGANer(
                model_path=model_path,
                upscale=1,
                arch='clean',
                channel_multiplier=2,
                bg_upsampler=None,
                device=self.device
            )
            print("✓ GFPGAN loaded")
            
            # Real-ESRGAN for super resolution
            esrgan_model_path = os.path.join('models', 'RealESRGAN_x2plus.pth')
            
            if not os.path.exists(esrgan_model_path):
                print("Downloading Real-ESRGAN model (~65MB)...")
                url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
                urllib.request.urlretrieve(url, esrgan_model_path)
                print("✓ Real-ESRGAN downloaded")
            
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
            
            self.realesrgan = RealESRGANer(
                scale=2,
                model_path=esrgan_model_path,
                model=model,
                tile=400,
                tile_pad=10,
                pre_pad=0,
                half=False,
                device=self.device
            )
            print("✓ Real-ESRGAN loaded")
            
        except Exception as e:
            print(f"⚠ Enhancement models failed to load: {e}")
            print("Continuing without enhancement...")
    
    def enhance_face(self, image, face_bbox=None):
        """
        Enhance face using GFPGAN + Real-ESRGAN pipeline
        Returns photorealistic enhanced image
        """
        if self.gfpgan is None and self.realesrgan is None:
            return image
        
        try:
            # Step 1: GFPGAN face restoration (removes artifacts, enhances details)
            if self.gfpgan is not None:
                _, _, restored_face = self.gfpgan.enhance(
                    image,
                    has_aligned=False,
                    only_center_face=False,
                    paste_back=True,
                    weight=0.5
                )
                image = restored_face
            
            # Step 2: Real-ESRGAN super resolution (sharpens everything)
            if self.realesrgan is not None:
                output, _ = self.realesrgan.enhance(image, outscale=1)
                image = output
            
            return image
            
        except Exception as e:
            print(f"Enhancement failed: {e}")
            return image
    
    def enhance_face_region(self, full_image, face_bbox):
        """
        Enhance only the face region with adaptive quality based on face size
        Larger faces get more aggressive enhancement
        """
        if self.gfpgan is None:
            return full_image
        
        try:
            x1, y1, x2, y2 = face_bbox
            
            # Calculate face size
            face_width = x2 - x1
            face_height = y2 - y1
            face_area = face_width * face_height
            image_area = full_image.shape[0] * full_image.shape[1]
            face_ratio = face_area / image_area
            
            # Adaptive enhancement based on face size
            # Large faces (>15% of image) = aggressive enhancement
            # Medium faces (5-15%) = moderate enhancement  
            # Small faces (<5%) = light enhancement
            
            if face_ratio > 0.15:
                # LARGE FACE - Maximum quality enhancement
                print(f"Large face detected ({face_ratio*100:.1f}% of image) - Applying maximum enhancement")
                enhancement_weight = 0.8  # Strong GFPGAN
                upscale_factor = 2  # 2x upscaling
                padding = 80
            elif face_ratio > 0.05:
                # MEDIUM FACE - Moderate enhancement
                print(f"Medium face detected ({face_ratio*100:.1f}% of image) - Applying moderate enhancement")
                enhancement_weight = 0.6
                upscale_factor = 2
                padding = 60
            else:
                # SMALL FACE - Light enhancement
                print(f"Small face detected ({face_ratio*100:.1f}% of image) - Applying light enhancement")
                enhancement_weight = 0.4
                upscale_factor = 1
                padding = 50
            
            # Add padding
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(full_image.shape[1], x2 + padding)
            y2 = min(full_image.shape[0], y2 + padding)
            
            # Extract face region
            face_region = full_image[y1:y2, x1:x2].copy()
            original_face = face_region.copy()
            
            # Step 1: GFPGAN face restoration with adaptive weight
            _, _, enhanced_face = self.gfpgan.enhance(
                face_region,
                has_aligned=False,
                only_center_face=True,
                paste_back=True,
                weight=enhancement_weight
            )
            
            # Step 2: Real-ESRGAN super resolution (for large faces)
            if self.realesrgan is not None and upscale_factor > 1:
                enhanced_face, _ = self.realesrgan.enhance(enhanced_face, outscale=upscale_factor)
                # Resize back to original size
                enhanced_face = cv2.resize(enhanced_face, (x2-x1, y2-y1), interpolation=cv2.INTER_LANCZOS4)
            
            # Step 3: Additional sharpening for large faces
            if face_ratio > 0.15:
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                enhanced_face = cv2.filter2D(enhanced_face, -1, kernel * 0.3)
            
            # Blend back into full image with smooth mask
            result = full_image.copy()
            
            # Create smooth blend mask
            mask = np.ones((y2-y1, x2-x1), dtype=np.float32)
            feather = 25 if face_ratio > 0.15 else 20
            mask = cv2.GaussianBlur(mask, (feather*2+1, feather*2+1), 0)
            mask_3ch = cv2.merge([mask, mask, mask])
            
            # Blend
            blended = (enhanced_face * mask_3ch + original_face * (1 - mask_3ch)).astype(np.uint8)
            result[y1:y2, x1:x2] = blended
            
            return result
            
        except Exception as e:
            print(f"Region enhancement failed: {e}")
            import traceback
            traceback.print_exc()
            return full_image
