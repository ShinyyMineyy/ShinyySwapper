"""
Accessory Preservation Module
Detects and preserves glasses, sunglasses, and other accessories during face swap
"""

import cv2
import numpy as np

class AccessoryPreserver:
    def __init__(self):
        pass
    
    def detect_glasses_region(self, img, face_landmarks):
        """
        Detect glasses region using edge detection and color analysis
        Returns mask of glasses area
        """
        try:
            # Get eye region coordinates
            left_eye = face_landmarks[0]
            right_eye = face_landmarks[1]
            
            # Calculate glasses region (expanded eye area)
            eye_center_x = int((left_eye[0] + right_eye[0]) / 2)
            eye_center_y = int((left_eye[1] + right_eye[1]) / 2)
            
            eye_width = int(abs(right_eye[0] - left_eye[0]) * 1.8)
            eye_height = int(eye_width * 0.5)
            
            x1 = max(0, eye_center_x - eye_width // 2)
            y1 = max(0, eye_center_y - eye_height // 2)
            x2 = min(img.shape[1], eye_center_x + eye_width // 2)
            y2 = min(img.shape[0], eye_center_y + eye_height // 2)
            
            # Extract region
            region = img[y1:y2, x1:x2]
            
            # Detect edges (glasses frames have strong edges)
            gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Dilate edges to connect frame parts
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=2)
            
            # Detect dark regions (sunglasses lenses)
            hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
            v_channel = hsv[:, :, 2]
            dark_mask = (v_channel < 80).astype(np.uint8) * 255
            
            # Combine edge and dark detection
            glasses_mask = cv2.bitwise_or(edges, dark_mask)
            
            # Clean up mask
            glasses_mask = cv2.morphologyEx(glasses_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
            glasses_mask = cv2.GaussianBlur(glasses_mask, (5, 5), 0)
            
            # Check if significant glasses detected
            glasses_ratio = np.sum(glasses_mask > 128) / (glasses_mask.shape[0] * glasses_mask.shape[1])
            
            if glasses_ratio < 0.05:  # Less than 5% coverage = no glasses
                return None
            
            # Create full image mask
            full_mask = np.zeros(img.shape[:2], dtype=np.uint8)
            full_mask[y1:y2, x1:x2] = glasses_mask
            
            return full_mask
            
        except Exception as e:
            print(f"Glasses detection failed: {e}")
            return None
    
    def preserve_accessories(self, swapped_result, original_target, target_landmarks):
        """
        Preserve glasses and accessories from original target onto swapped result
        
        Args:
            swapped_result: Face-swapped image
            original_target: Original target image with accessories
            target_landmarks: Target face landmarks
        
        Returns:
            Result with preserved accessories
        """
        # Detect glasses in original target
        glasses_mask = self.detect_glasses_region(original_target, target_landmarks)
        
        if glasses_mask is None:
            return swapped_result
        
        print("Glasses detected - preserving...")
        
        # Normalize mask to 0-1 range
        glasses_mask_norm = glasses_mask.astype(np.float32) / 255.0
        
        # Apply slight blur for smooth blending
        glasses_mask_norm = cv2.GaussianBlur(glasses_mask_norm, (7, 7), 0)
        
        # Create 3-channel mask
        glasses_mask_3ch = cv2.merge([glasses_mask_norm, glasses_mask_norm, glasses_mask_norm])
        
        # Blend: where mask is high, use original target (glasses)
        result = (original_target * glasses_mask_3ch + swapped_result * (1 - glasses_mask_3ch)).astype(np.uint8)
        
        return result
