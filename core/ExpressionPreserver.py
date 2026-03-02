"""
Expression Preservation Module
Maintains target's facial expressions (eyes, mouth) during face swap
"""

import cv2
import numpy as np

class ExpressionPreserver:
    def __init__(self):
        pass
    
    def preserve_expression(self, swapped_result, target_img, target_landmarks, blend_strength=0.7):
        """
        Preserve target's facial expression on swapped face
        
        Args:
            swapped_result: Face-swapped image
            target_img: Original target image
            target_landmarks: Target face landmarks
            blend_strength: How much to preserve (0=none, 1=full)
        
        Returns:
            Result with preserved expressions
        """
        
        # Extract eye and mouth regions from target
        left_eye_data = self._extract_eye_region(target_img, target_landmarks, 'left')
        right_eye_data = self._extract_eye_region(target_img, target_landmarks, 'right')
        mouth_data = self._extract_mouth_region(target_img, target_landmarks)
        
        result = swapped_result.copy()
        
        # Blend eyes
        if left_eye_data is not None:
            result = self._blend_region(result, left_eye_data, blend_strength)
        
        if right_eye_data is not None:
            result = self._blend_region(result, right_eye_data, blend_strength)
        
        # Blend mouth (REDUCED strength)
        if mouth_data is not None:
            result = self._blend_region(result, mouth_data, blend_strength * 0.4)  # Very subtle for mouth
        
        return result
    
    def _extract_eye_region(self, img, landmarks, side='left'):
        """Extract eye region with mask"""
        try:
            # Get eye landmarks (InsightFace provides 5 landmarks: 2 eyes, nose, 2 mouth corners)
            if side == 'left':
                eye_center = landmarks[0]  # Left eye
            else:
                eye_center = landmarks[1]  # Right eye
            
            # Create region around eye
            x, y = int(eye_center[0]), int(eye_center[1])
            size = 40  # Eye region size
            
            x1 = max(0, x - size)
            y1 = max(0, y - size)
            x2 = min(img.shape[1], x + size)
            y2 = min(img.shape[0], y + size)
            
            region = img[y1:y2, x1:x2].copy()
            
            # Create elliptical mask for eye
            mask = np.zeros((y2-y1, x2-x1), dtype=np.float32)
            center = (size, size)
            axes = (size-10, size-15)
            cv2.ellipse(mask, center, axes, 0, 0, 360, 1, -1)
            mask = cv2.GaussianBlur(mask, (21, 21), 0)
            
            return (region, mask, (x1, y1, x2, y2))
        except:
            return None
    
    def _extract_mouth_region(self, img, landmarks):
        """Extract mouth region with mask"""
        try:
            # Mouth landmarks (corners)
            mouth_left = landmarks[3]
            mouth_right = landmarks[4]
            
            # Calculate mouth center and size
            mouth_center_x = int((mouth_left[0] + mouth_right[0]) / 2)
            mouth_center_y = int((mouth_left[1] + mouth_right[1]) / 2)
            
            mouth_width = int(abs(mouth_right[0] - mouth_left[0]))
            mouth_height = int(mouth_width * 0.6)
            
            # Create region
            x1 = max(0, mouth_center_x - mouth_width)
            y1 = max(0, mouth_center_y - mouth_height)
            x2 = min(img.shape[1], mouth_center_x + mouth_width)
            y2 = min(img.shape[0], mouth_center_y + mouth_height)
            
            region = img[y1:y2, x1:x2].copy()
            
            # Create elliptical mask for mouth
            mask = np.zeros((y2-y1, x2-x1), dtype=np.float32)
            center = (mouth_width, mouth_height)
            axes = (mouth_width-10, mouth_height-5)
            cv2.ellipse(mask, center, axes, 0, 0, 360, 1, -1)
            mask = cv2.GaussianBlur(mask, (31, 31), 0)
            
            return (region, mask, (x1, y1, x2, y2))
        except:
            return None
    
    def _blend_region(self, base_img, region_data, strength):
        """Blend region onto base image"""
        if region_data is None:
            return base_img
        
        region, mask, (x1, y1, x2, y2) = region_data
        
        # Adjust mask strength
        mask = mask * strength
        mask_3ch = cv2.merge([mask, mask, mask])
        
        # Extract corresponding region from base
        base_region = base_img[y1:y2, x1:x2]
        
        # Blend
        blended_region = (region * mask_3ch + base_region * (1 - mask_3ch)).astype(np.uint8)
        
        # Place back
        result = base_img.copy()
        result[y1:y2, x1:x2] = blended_region
        
        return result
