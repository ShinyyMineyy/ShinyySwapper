"""
LaMa Inpainting Module
Fixes blend edges and artifacts for photorealistic results
"""

import cv2
import numpy as np
import os

try:
    import torch
    from PIL import Image
    LAMA_AVAILABLE = True
except ImportError:
    LAMA_AVAILABLE = False
    print("⚠ LaMa dependencies not available")

class LamaInpainter:
    def __init__(self):
        if not LAMA_AVAILABLE:
            self.model = None
            return
        
        self.device = 'cpu'  # CPU-friendly
        self.model = None
        
        try:
            # Download and load LaMa model
            self._load_model()
            print("✓ LaMa inpainting initialized")
        except Exception as e:
            print(f"⚠ LaMa initialization failed: {e}")
            self.model = None
    
    def _load_model(self):
        """Load LaMa model from torch hub"""
        try:
            # Use simple-lama-inpainting (lightweight wrapper)
            from simple_lama_inpainting import SimpleLama
            self.model = SimpleLama()
            print("✓ LaMa model loaded")
        except:
            print("⚠ Installing simple-lama-inpainting...")
            os.system('pip install simple-lama-inpainting --quiet')
            from simple_lama_inpainting import SimpleLama
            self.model = SimpleLama()
    
    def detect_blend_edges(self, swapped_img, original_img, face_bbox, threshold=20):
        """
        Detect problematic blend edges automatically
        Returns mask of areas that need inpainting
        """
        x1, y1, x2, y2 = face_bbox
        
        # Expand bbox for edge detection
        padding = 40
        x1_pad = max(0, x1 - padding)
        y1_pad = max(0, y1 - padding)
        x2_pad = min(swapped_img.shape[1], x2 + padding)
        y2_pad = min(swapped_img.shape[0], y2 + padding)
        
        # Extract regions
        swapped_region = swapped_img[y1_pad:y2_pad, x1_pad:x2_pad]
        original_region = original_img[y1_pad:y2_pad, x1_pad:x2_pad]
        
        # Calculate difference
        diff = cv2.absdiff(swapped_region, original_region)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Threshold to find problem areas
        _, mask = cv2.threshold(diff_gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Only keep edge pixels (not entire face)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kernel)
        
        # Dilate slightly to cover edge areas
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Create full image mask
        full_mask = np.zeros(swapped_img.shape[:2], dtype=np.uint8)
        full_mask[y1_pad:y2_pad, x1_pad:x2_pad] = mask
        
        return full_mask
    
    def inpaint_edges(self, image, mask):
        """
        Inpaint problematic areas using LaMa
        
        Args:
            image: BGR image (numpy array)
            mask: Binary mask (255 = inpaint, 0 = keep)
        
        Returns:
            Inpainted BGR image
        """
        if self.model is None:
            return image
        
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL
            pil_image = Image.fromarray(image_rgb)
            pil_mask = Image.fromarray(mask)
            
            # Inpaint
            result_pil = self.model(pil_image, pil_mask)
            
            # Convert back to BGR numpy
            result_rgb = np.array(result_pil)
            result_bgr = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
            
            return result_bgr
        
        except Exception as e:
            print(f"Inpainting failed: {e}")
            return image
    
    def refine_swap(self, swapped_img, original_img, face_bbox):
        """
        Complete refinement pipeline:
        1. Detect problem edges
        2. Inpaint them seamlessly
        
        Returns:
            Photorealistic refined image
        """
        if self.model is None:
            return swapped_img
        
        print("Detecting blend edges...")
        mask = self.detect_blend_edges(swapped_img, original_img, face_bbox)
        
        # Check if there are areas to inpaint
        if np.sum(mask) < 500:  # Too small to matter
            print("No significant edges detected")
            return swapped_img
        
        print(f"Inpainting {np.sum(mask > 0)} pixels...")
        refined = self.inpaint_edges(swapped_img, mask)
        
        print("✓ Refinement complete")
        return refined
