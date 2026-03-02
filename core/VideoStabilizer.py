import cv2
import numpy as np
from collections import deque

class VideoStabilizer:
    def __init__(self, window_size=7):
        self.window_size = window_size
        self.frame_buffer = deque(maxlen=window_size)
        
    def stabilize_frame(self, frame, bbox):
        """Apply temporal smoothing to reduce flickering"""
        self.frame_buffer.append(frame.copy())
        
        if len(self.frame_buffer) < 3:
            return frame
        
        # Extract face region
        x1, y1, x2, y2 = bbox
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        
        # Temporal averaging on face region
        face_stack = []
        for buffered_frame in self.frame_buffer:
            face_region = buffered_frame[y1:y2, x1:x2]
            face_stack.append(face_region.astype(np.float32))
        
        # Weighted average (center frames have more weight)
        weights = np.array([0.1, 0.2, 0.4, 0.2, 0.1])[:len(face_stack)]
        weights = weights / weights.sum()
        
        stabilized_face = np.zeros_like(face_stack[0])
        for i, face in enumerate(face_stack):
            stabilized_face += face * weights[i]
        
        stabilized_face = stabilized_face.astype(np.uint8)
        
        # Blend back into frame
        result = frame.copy()
        result[y1:y2, x1:x2] = stabilized_face
        
        return result
