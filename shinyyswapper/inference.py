import torch
import cv2
import numpy as np
from model import Generator
from insightface.app import FaceAnalysis
from scipy.ndimage import binary_erosion

class ShinyySwapper:
    def __init__(self, model_path, device='cpu'):
        self.device = device
        self.G = Generator().to(device)
        checkpoint = torch.load(model_path, map_location=device)
        self.G.load_state_dict(checkpoint['G_state'])
        self.G.eval()
        
        self.face_app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=-1, det_size=(640, 640))
    
    def extract_identity(self, img_path):
        img = cv2.imread(img_path)
        faces = self.face_app.get(img)
        if not faces:
            raise ValueError("No face detected in source image")
        return torch.FloatTensor(faces[0].embedding).to(self.device)
    
    def get_extended_bbox(self, bbox, img_shape, scale=2.5):
        """Extend bbox to include full head, hair, neck, ears"""
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        # Extend bbox by scale factor
        new_w, new_h = int(w * scale), int(h * scale)
        new_x1 = max(0, cx - new_w // 2)
        new_y1 = max(0, cy - int(new_h * 0.6))  # More space on top for hair
        new_x2 = min(img_shape[1], cx + new_w // 2)
        new_y2 = min(img_shape[0], cy + int(new_h * 0.5))  # More space below for neck
        
        return new_x1, new_y1, new_x2, new_y2
    
    def create_seamless_mask(self, face_shape, feather=50):
        """Create soft mask for seamless blending"""
        mask = np.ones(face_shape[:2], dtype=np.float32)
        for i in range(feather):
            mask = binary_erosion(mask)
        mask = cv2.GaussianBlur(mask.astype(np.float32), (feather*2+1, feather*2+1), 0)
        return np.stack([mask]*3, axis=-1)
    
    def swap(self, target_path, source_path, output_path):
        # Load images
        target = cv2.imread(target_path)
        target_rgb = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
        
        # Get source identity
        source_id = self.extract_identity(source_path).unsqueeze(0)
        
        # Detect face in target
        faces = self.face_app.get(target)
        if not faces:
            raise ValueError("No face detected in target image")
        
        face = faces[0]
        bbox = face.bbox.astype(int)
        
        # Get extended bbox (includes hair, ears, neck)
        x1, y1, x2, y2 = self.get_extended_bbox(bbox, target_rgb.shape)
        
        # Extract extended region
        face_region = target_rgb[y1:y2, x1:x2]
        face_resized = cv2.resize(face_region, (512, 512))  # Higher resolution
        
        # Normalize
        face_tensor = torch.FloatTensor(face_resized).permute(2, 0, 1).unsqueeze(0) / 127.5 - 1
        face_tensor = face_tensor.to(self.device)
        
        # Generate swapped face with occlusion handling
        with torch.no_grad():
            swapped, occlusion_mask = self.G(face_tensor, source_id)
        
        # Denormalize
        swapped = ((swapped[0].permute(1, 2, 0).cpu().numpy() + 1) * 127.5).astype('uint8')
        swapped = cv2.resize(swapped, (x2 - x1, y2 - y1))
        
        # Get occlusion mask (hair, glasses areas)
        mask_np = occlusion_mask[0, 0].cpu().numpy()
        mask_np = cv2.resize(mask_np, (x2 - x1, y2 - y1))
        mask_np = np.stack([mask_np]*3, axis=-1)
        
        # Smart blending: Only swap visible face, keep hair/glasses from original
        result = target_rgb.copy()
        
        # Blend with occlusion awareness
        blend_mask = self.create_seamless_mask(swapped.shape, feather=80) * mask_np
        result[y1:y2, x1:x2] = (swapped * blend_mask + result[y1:y2, x1:x2] * (1 - blend_mask)).astype('uint8')
        
        # Color correction
        result[y1:y2, x1:x2] = self.match_color(result[y1:y2, x1:x2], target_rgb[y1:y2, x1:x2], mask)
        
        # Save
        result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, result_bgr)
        print(f"Saved result to {output_path}")
    
    def match_color(self, source, target, mask):
        """Match color distribution for seamless blend"""
        for i in range(3):
            source_mean = np.mean(source[:,:,i][mask[:,:,i] > 0.5])
            target_mean = np.mean(target[:,:,i][mask[:,:,i] > 0.5])
            source_std = np.std(source[:,:,i][mask[:,:,i] > 0.5])
            target_std = np.std(target[:,:,i][mask[:,:,i] > 0.5])
            
            source[:,:,i] = np.clip(
                (source[:,:,i] - source_mean) * (target_std / (source_std + 1e-6)) + target_mean,
                0, 255
            ).astype('uint8')
        return source

if __name__ == '__main__':
    swapper = ShinyySwapper('checkpoints/checkpoint_epoch_99.pt')
    swapper.swap('target.jpg', 'source.jpg', 'output.jpg')
