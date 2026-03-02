"""
Sharp Face Swapper - NO BLUR, Maximum Detail
Preserves target resolution perfectly
"""

import cv2
import insightface
from insightface.app import FaceAnalysis
import os
import numpy as np
import urllib.request
import sys

try:
    from gfpgan import GFPGANer
    GFPGAN_AVAILABLE = True
except ImportError:
    GFPGAN_AVAILABLE = False
    print("⚠ GFPGAN not available (optional enhancement)")

try:
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False
    print("⚠ Real-ESRGAN not available (optional full image enhancement)")

class SharpFaceSwapper:
    def __init__(self, config=None):
        if config is None:
            config = {"detection_size": [640, 640], "face_analysis_model": "buffalo_l", "enable_gpu": True, "gpu_id": 0}
        
        ctx_id = config.get("gpu_id", 0) if config.get("enable_gpu", True) else -1
        
        try:
            self.app = FaceAnalysis(name=config.get("face_analysis_model", "buffalo_l"))
            det_size = tuple(config.get("detection_size", [640, 640]))
            self.app.prepare(ctx_id=ctx_id, det_size=det_size)
            print(f"Face analysis initialized (GPU: {ctx_id >= 0})")
        except Exception as e:
            print(f"Warning: GPU initialization failed, falling back to CPU: {e}")
            self.app = FaceAnalysis(name=config.get("face_analysis_model", "buffalo_l"))
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
        
        model_path = config.get("model_name", "inswapper_128.onnx")
        try:
            self.swapper = insightface.model_zoo.get_model(model_path, download=True, download_zip=True)
            print("Swapper model loaded successfully")
        except Exception as e:
            print(f"Error loading swapper model: {e}")
            raise
        
        # Initialize GFPGAN enhancer
        self.enhancer = None
        if GFPGAN_AVAILABLE:
            try:
                print("Loading GFPGAN enhancement model...")
                model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
                os.makedirs(model_dir, exist_ok=True)
                
                model_path = os.path.join(model_dir, 'GFPGANv1.4.pth')
                
                # Auto-download if not exists
                if not os.path.exists(model_path):
                    print("Downloading GFPGAN model (first time only, ~350MB)...")
                    url = 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth'
                    urllib.request.urlretrieve(url, model_path)
                    print("✓ GFPGAN model downloaded")
                
                self.enhancer = GFPGANer(
                    model_path=model_path,
                    upscale=1,
                    arch='clean',
                    channel_multiplier=2,
                    bg_upsampler=None
                )
                print("✓ GFPGAN enhancer initialized")
            except Exception as e:
                print(f"⚠ GFPGAN enhancer failed: {e}")
                self.enhancer = None
        else:
            print("⚠ GFPGAN not installed - enhancement disabled")
        
        # Initialize Real-ESRGAN for full image enhancement
        self.full_enhancer = None
        if REALESRGAN_AVAILABLE:
            try:
                print("Loading Real-ESRGAN full image enhancer...")
                model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
                model_path = os.path.join(model_dir, 'RealESRGAN_x2plus.pth')
                
                if not os.path.exists(model_path):
                    print("Downloading Real-ESRGAN model (first time only, ~65MB)...")
                    url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
                    try:
                        urllib.request.urlretrieve(url, model_path)
                        print("✓ Real-ESRGAN model downloaded")
                    except Exception as download_error:
                        print(f"⚠ Failed to download Real-ESRGAN model: {download_error}")
                        self.full_enhancer = None
                        return
                
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
                self.full_enhancer = RealESRGANer(
                    scale=2,
                    model_path=model_path,
                    model=model,
                    tile=400,
                    tile_pad=10,
                    pre_pad=0,
                    half=False
                )
                print("✓ Real-ESRGAN full image enhancer initialized")
            except Exception as e:
                print(f"⚠ Real-ESRGAN failed: {e}")
                self.full_enhancer = None
        else:
            print("⚠ Real-ESRGAN not installed - full image enhancement disabled")
        
        # Initialize Face Parser (keep for future use)
        self.parser = None
    
    def _detect_open_mouth(self, face_obj, img, bbox):
        """Detect if mouth is open showing teeth"""
        try:
            kps = face_obj.kps
            mouth_left = kps[3]
            mouth_right = kps[4]
            nose = kps[2]
            
            # Calculate mouth opening (vertical distance)
            mouth_height = abs(mouth_left[1] - mouth_right[1])
            mouth_width = np.linalg.norm(mouth_right - mouth_left)
            
            # If mouth height is significant relative to width, mouth is open
            mouth_ratio = mouth_height / (mouth_width + 1e-6)
            
            is_open = mouth_ratio > 0.15
            
            if is_open:
                # Extract mouth region for teeth preservation
                x1, y1, x2, y2 = bbox
                mouth_center_y = int((mouth_left[1] + mouth_right[1]) / 2)
                mouth_center_x = int((mouth_left[0] + mouth_right[0]) / 2)
                
                # Define mouth region (wider area to capture teeth)
                mouth_h = int((y2 - y1) * 0.25)
                mouth_w = int((x2 - x1) * 0.4)
                
                my1 = max(0, mouth_center_y - mouth_h // 2)
                my2 = min(img.shape[0], mouth_center_y + mouth_h // 2)
                mx1 = max(0, mouth_center_x - mouth_w // 2)
                mx2 = min(img.shape[1], mouth_center_x + mouth_w // 2)
                
                return True, (mx1, my1, mx2, my2)
            
            return False, None
        except:
            return False, None
    
    def _preserve_teeth(self, swapped_img, original_img, mouth_bbox):
        """Preserve original teeth from target image"""
        mx1, my1, mx2, my2 = mouth_bbox
        
        # Extract mouth regions
        original_mouth = original_img[my1:my2, mx1:mx2].copy()
        swapped_mouth = swapped_img[my1:my2, mx1:mx2].copy()
        
        # Create mask for teeth (detect bright pixels in mouth region)
        gray_orig = cv2.cvtColor(original_mouth, cv2.COLOR_BGR2GRAY)
        gray_swap = cv2.cvtColor(swapped_mouth, cv2.COLOR_BGR2GRAY)
        
        # Teeth are typically brighter than surrounding skin
        _, teeth_mask = cv2.threshold(gray_orig, 180, 255, cv2.THRESH_BINARY)
        
        # Refine mask - remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        teeth_mask = cv2.morphologyEx(teeth_mask, cv2.MORPH_CLOSE, kernel)
        teeth_mask = cv2.morphologyEx(teeth_mask, cv2.MORPH_OPEN, kernel)
        
        # Blur mask for smooth blending
        teeth_mask = cv2.GaussianBlur(teeth_mask, (15, 15), 5)
        teeth_mask = teeth_mask.astype(np.float32) / 255.0
        
        # Only preserve if significant teeth detected
        if np.sum(teeth_mask > 0.3) > 100:
            teeth_mask_3ch = cv2.merge([teeth_mask, teeth_mask, teeth_mask])
            
            # Blend original teeth back
            blended_mouth = (original_mouth * teeth_mask_3ch + swapped_mouth * (1 - teeth_mask_3ch)).astype(np.uint8)
            
            # Apply color correction to match swapped face skin tone
            blended_mouth = self.match_colors_subtle(blended_mouth, swapped_mouth)
            
            # Place back into swapped image
            result = swapped_img.copy()
            result[my1:my2, mx1:mx2] = blended_mouth
            return result
        
    
    def _detect_pose(self, face_obj):
        """Detect face pose angle (yaw, pitch, roll) to identify extreme angles"""
        try:
            # InsightFace provides pose estimation through landmarks
            kps = face_obj.kps
            
            # Calculate yaw (left-right rotation) from eye positions
            left_eye = kps[0]
            right_eye = kps[1]
            nose = kps[2]
            
            # Eye distance
            eye_distance = np.linalg.norm(right_eye - left_eye)
            
            # Distance from nose to eye center
            eye_center = (left_eye + right_eye) / 2
            nose_to_center = nose[0] - eye_center[0]
            
            # Estimate yaw angle (simplified)
            yaw = np.arctan2(nose_to_center, eye_distance) * 180 / np.pi * 2
            
            # Calculate pitch (up-down rotation) from nose and mouth positions
            mouth_center = (kps[3] + kps[4]) / 2
            nose_to_mouth_y = mouth_center[1] - nose[1]
            
            # Estimate pitch angle
            pitch = np.arctan2(nose_to_mouth_y - eye_distance * 0.5, eye_distance) * 180 / np.pi
            
            # Detect extreme pose (threshold: 30 degrees)
            is_extreme = abs(yaw) > 30 or abs(pitch) > 30
            
            return {
                'yaw': yaw,
                'pitch': pitch,
                'is_extreme': is_extreme
            }
        except:
            return {'yaw': 0, 'pitch': 0, 'is_extreme': False}
    
    def _detect_gender(self, face_obj):
        """Detect if face is male based on InsightFace gender attribute"""
        try:
            # InsightFace provides gender: 0=female, 1=male
            if hasattr(face_obj, 'gender'):
                return face_obj.gender == 1
            # Fallback: assume male if gender not available
            return False
        except:
            return False
    
    def _match_lighting_enhanced(self, source_region, target_region):
        """Enhanced lighting match for male faces (includes slight color adjustment)"""
        source_lab = cv2.cvtColor(source_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Match L (lightness) channel fully
        src_mean_l, src_std_l = cv2.meanStdDev(source_lab[:,:,0])
        tgt_mean_l, tgt_std_l = cv2.meanStdDev(target_lab[:,:,0])
        
        if src_std_l > 0.1:
            source_lab[:,:,0] = ((source_lab[:,:,0] - src_mean_l) * (tgt_std_l / src_std_l)) + tgt_mean_l
        
        # Slight color adjustment for better blending (20% for males)
        for i in [1, 2]:
            src_mean = np.mean(source_lab[:,:,i])
            tgt_mean = np.mean(target_lab[:,:,i])
            shift = (tgt_mean - src_mean) * 0.2
            source_lab[:,:,i] = source_lab[:,:,i] + shift
        
        source_lab = np.clip(source_lab, 0, 255)
        return cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def _match_lighting_only(self, source_region, target_region):
        """Match only lighting/brightness, preserve source colors completely"""
        source_lab = cv2.cvtColor(source_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Only match L (lightness) channel, keep A and B (color) unchanged
        src_mean_l, src_std_l = cv2.meanStdDev(source_lab[:,:,0])
        tgt_mean_l, tgt_std_l = cv2.meanStdDev(target_lab[:,:,0])
        
        if src_std_l > 0.1:
            source_lab[:,:,0] = ((source_lab[:,:,0] - src_mean_l) * (tgt_std_l / src_std_l)) + tgt_mean_l
        
        source_lab = np.clip(source_lab, 0, 255)
        return cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def match_skin_color_advanced(self, swapped_face_region, target_body_region, face_mask=None):
        """Advanced skin color matching - transfers target body skin tone to swapped face"""
        # Convert to LAB color space for better skin tone control
        face_lab = cv2.cvtColor(swapped_face_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        body_lab = cv2.cvtColor(target_body_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        body_l_mean, body_l_std = cv2.meanStdDev(body_lab[:,:,0])
        body_a_mean, body_a_std = cv2.meanStdDev(body_lab[:,:,1])
        body_b_mean, body_b_std = cv2.meanStdDev(body_lab[:,:,2])
        
        face_l_mean, face_l_std = cv2.meanStdDev(face_lab[:,:,0])
        face_a_mean, face_a_std = cv2.meanStdDev(face_lab[:,:,1])
        face_b_mean, face_b_std = cv2.meanStdDev(face_lab[:,:,2])
        
        # STRONG color transfer - 100% for all channels
        if face_l_std > 0.1:
            face_lab[:,:,0] = ((face_lab[:,:,0] - face_l_mean) * (body_l_std / face_l_std)) + body_l_mean
        else:
            face_lab[:,:,0] = body_l_mean
        
        if face_a_std > 0.1:
            face_lab[:,:,1] = ((face_lab[:,:,1] - face_a_mean) * (body_a_std / face_a_std)) + body_a_mean
        else:
            face_lab[:,:,1] = body_a_mean
        
        if face_b_std > 0.1:
            face_lab[:,:,2] = ((face_lab[:,:,2] - face_b_mean) * (body_b_std / face_b_std)) + body_b_mean
        else:
            face_lab[:,:,2] = body_b_mean
        
        face_lab = np.clip(face_lab, 0, 255)
        return cv2.cvtColor(face_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def match_colors_subtle(self, source_region, target_region):
        """Subtle color matching to preserve source identity"""
        # Convert to LAB color space
        source_lab = cv2.cvtColor(source_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Match only lightness (L channel) more aggressively, keep color identity
        src_mean_l, src_std_l = cv2.meanStdDev(source_lab[:,:,0])
        tgt_mean_l, tgt_std_l = cv2.meanStdDev(target_lab[:,:,0])
        
        if src_std_l > 0.1:
            source_lab[:,:,0] = ((source_lab[:,:,0] - src_mean_l) * (tgt_std_l / src_std_l)) + tgt_mean_l
        
        # Very subtle color matching (A and B channels) - only 30% shift
        for i in [1, 2]:
            src_mean = np.mean(source_lab[:,:,i])
            tgt_mean = np.mean(target_lab[:,:,i])
            shift = (tgt_mean - src_mean) * 0.3
            source_lab[:,:,i] = source_lab[:,:,i] + shift
        
        source_lab = np.clip(source_lab, 0, 255)
        return cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    
    def match_colors_precise(self, source_region, target_region):
        """Match colors precisely to target body skin tone"""
        # Convert to LAB color space for better skin tone matching
        source_lab = cv2.cvtColor(source_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target_region, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Match each channel with stronger emphasis on L (lightness) for skin tone
        for i in range(3):
            src_mean, src_std = cv2.meanStdDev(source_lab[:,:,i])
            tgt_mean, tgt_std = cv2.meanStdDev(target_lab[:,:,i])
            
            if src_std > 0.1:
                # Stronger color matching for better skin tone blend
                source_lab[:,:,i] = ((source_lab[:,:,i] - src_mean) * (tgt_std / src_std)) + tgt_mean
        
        # Additional skin tone adjustment in RGB space
        source_lab = np.clip(source_lab, 0, 255)
        matched = cv2.cvtColor(source_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        
        # Fine-tune skin tones by blending with target color statistics
        matched_float = matched.astype(np.float32)
        target_float = target_region.astype(np.float32)
        
        # Calculate color shift for better body match
        for c in range(3):
            src_mean = np.mean(matched_float[:,:,c])
            tgt_mean = np.mean(target_float[:,:,c])
            shift = tgt_mean - src_mean
            matched_float[:,:,c] = matched_float[:,:,c] + (shift * 0.6)  # 60% shift for natural blend
        
        matched_float = np.clip(matched_float, 0, 255)
        return matched_float.astype(np.uint8)
    
    def create_sharp_mask(self, face_box, img_shape, feather=35, parsed_mask=None):
        """Create mask with sharp center, soft edges - extended for full face coverage"""
        x1, y1, x2, y2 = face_box
        h, w = y2-y1, x2-x1
        
        if parsed_mask is not None and parsed_mask.shape == (h, w):
            mask = np.zeros(img_shape[:2], dtype=np.float32)
            mask[y1:y2, x1:x2] = parsed_mask
            return mask
        
        # Expanded elliptical mask for more face coverage
        mask = np.zeros(img_shape[:2], dtype=np.float32)
        center = ((x1 + x2) // 2, (y1 + y2) // 2)
        # Increased axes by 30% for wider coverage
        axes = (int((x2 - x1) * 0.65), int((y2 - y1) * 0.95))
        
        cv2.ellipse(mask, center, axes, 0, 0, 360, 1, -1)
        
        # Apply large Gaussian blur for seamless blending
        mask = cv2.GaussianBlur(mask, (feather*2+1, feather*2+1), feather//2)
        
        return mask
    
    def sharpen_image(self, img, strength=0.5):
        """Sharpen without artifacts"""
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) * strength
        sharpened = cv2.filter2D(img, -1, kernel)
        return cv2.addWeighted(img, 0.7, sharpened, 0.3, 0)
    
    def swap_faces(self, source_path, source_face_idx, target_path, target_face_idx, enhance_quality=True, enhance_full_image=False):
        """Sharp face swapping - NO BLUR, preserves resolution"""
        print("\n=== Sharp Face Swap (No Blur) ===")
        
        source_img = cv2.imread(source_path)
        target_img = cv2.imread(target_path)

        if source_img is None or target_img is None:
            raise ValueError("Could not read one or both images")

        source_faces = self.app.get(source_img)
        target_faces = self.app.get(target_img)

        print(f"Detected {len(source_faces)} face(s) in source, {len(target_faces)} face(s) in target")

        source_faces = sorted(source_faces, key=lambda x: x.bbox[0])
        target_faces = sorted(target_faces, key=lambda x: x.bbox[0])

        if len(source_faces) < source_face_idx or source_face_idx < 1:
            raise ValueError(f"Source image contains {len(source_faces)} faces, but requested face {source_face_idx}. Try using a clearer image with visible faces.")
        if len(target_faces) < target_face_idx or target_face_idx < 1:
            raise ValueError(f"Target image contains {len(target_faces)} faces, but requested face {target_face_idx}. Try using a clearer image with visible faces.")

        source_face = source_faces[source_face_idx - 1]
        target_face = target_faces[target_face_idx - 1]
        
        # Check face quality
        src_bbox = source_face.bbox.astype(int)
        tgt_bbox = target_face.bbox.astype(int)
        src_size = (src_bbox[2] - src_bbox[0]) * (src_bbox[3] - src_bbox[1])
        tgt_size = (tgt_bbox[2] - tgt_bbox[0]) * (tgt_bbox[3] - tgt_bbox[1])
        
        print(f"Source face size: {src_size}px², Target face size: {tgt_size}px²")
        
        if src_size < 2500 or tgt_size < 2500:
            print("⚠ Warning: Face is very small, quality may be reduced. Try using higher resolution images.")
        
        # Detect face pose/angle
        pose_info = self._detect_pose(target_face)
        is_extreme_pose = pose_info['is_extreme']
        
        if is_extreme_pose:
            print(f"Extreme pose detected (yaw: {pose_info['yaw']:.1f}°, pitch: {pose_info['pitch']:.1f}°) - using adaptive processing...")
        
        # Detect open mouth and preserve teeth if needed
        has_open_mouth, mouth_bbox = self._detect_open_mouth(target_face, target_img, tgt_bbox)
        if has_open_mouth:
            print("Open mouth detected - preserving original teeth...")
        
        print("Swapping face (high resolution)...")
        try:
            # Try standard API (InSwapper, SimSwap) - 3 args + paste_back
            result = self.swapper.get(target_img, target_face, source_face, paste_back=True)
        except TypeError as e:
            try:
                # Try without paste_back (GHOST, FaceDancer) - 3 args
                result = self.swapper.get(target_img, target_face, source_face)
            except TypeError:
                # Try BlendSwap API - only 2 args (img, face)
                # BlendSwap swaps all faces in the image
                result = self.swapper.get(target_img, source_face)
        
        # Detect if source is male (based on face analysis)
        is_male = self._detect_gender(source_face)
        if is_male:
            print("Male face detected - applying enhanced processing...")
        
        # SKIP expression and accessory preservation to maintain source identity
        # Only apply enhancement and minimal post-processing
        
        # Get bbox (may be expanded for full head)
        bbox = target_face.bbox.astype(int)
        x1, y1, x2, y2 = bbox
        
        if enhance_quality:
            # Process ENTIRE image to eliminate any visible boundaries
            x1_pad = 0
            y1_pad = 0
            x2_pad = result.shape[1]
            y2_pad = result.shape[0]
            
            face_region = result.copy()
            target_region = target_img.copy()
            
            # Step 1: Face Parsing for precise mask
            parsed_mask = None
            occluder_mask = None
            if self.parser is not None:
                print("Parsing face regions...")
                parsed_mask = self.parser.parse_face(result, bbox)
                occluder_mask = self.parser.get_occluder_mask(target_img, bbox)
            
            # Step 2: Minimal color adjustment - preserve source face structure
            print("Adjusting colors...")
            face_region = self.match_colors_subtle(face_region, target_region)
            
            # Step 3: Light sharpening to preserve details
            print("Sharpening...")
            face_region = self.sharpen_image(face_region, strength=0.7)
            
            # Step 4: Precise blending with moderate feather for sharp face structure
            print("Blending...")
            if is_extreme_pose:
                feather_size = 45
            else:
                feather_size = 40
            
            sharp_mask = self.create_sharp_mask(
                (x1, y1, x2, y2),
                face_region.shape, 
                feather=feather_size,
                parsed_mask=None
            )
            
            sharp_mask_3ch = cv2.merge([sharp_mask, sharp_mask, sharp_mask])
            blended = (face_region * sharp_mask_3ch + target_region * (1 - sharp_mask_3ch)).astype(np.uint8)
            
            # Additional minimal edge smoothing
            edge_mask = (np.abs(sharp_mask - 0.5) < 0.3).astype(np.float32)
            if np.any(edge_mask > 0):
                smoothed = cv2.bilateralFilter(blended, 7, 50, 50)
                edge_mask_3ch = np.stack([edge_mask, edge_mask, edge_mask], axis=2)
                blended = (smoothed * edge_mask_3ch + blended * (1 - edge_mask_3ch)).astype(np.uint8)
            
            # Step 5: SKIP occluder preservation to maintain source face
            # if occluder_mask is not None:
            #     print("Preserving accessories...")
            #     occluder_mask_3ch = cv2.merge([occluder_mask, occluder_mask, occluder_mask])
            #     blended = np.where(occluder_mask_3ch > 0, target_region, blended)
            
            result = blended
        
        # Preserve teeth if mouth was open
        if has_open_mouth and mouth_bbox is not None:
            print("Restoring original teeth...")
            result = self._preserve_teeth(result, target_img, mouth_bbox)
        
        # Apply Real-ESRGAN full image enhancement FIRST if requested
        if enhance_full_image and self.full_enhancer is not None:
            print("Enhancing full image with Real-ESRGAN (2x upscale)...")
            try:
                result, _ = self.full_enhancer.enhance(result, outscale=2)
                print("✓ Full image enhancement complete (2x resolution)")
            except Exception as e:
                print(f"⚠ Full image enhancement failed: {e}")
        
        # Apply GFPGAN face enhancement SECOND if enabled
        if enhance_quality and self.enhancer is not None:
            print("Enhancing face with GFPGAN...")
            try:
                _, _, result = self.enhancer.enhance(
                    result,
                    has_aligned=False,
                    only_center_face=False,
                    paste_back=True
                )
                print("✓ Face enhancement complete")
            except Exception as e:
                print(f"⚠ Face enhancement failed: {e}")
        
        print("=== Sharp Face Swap Complete ===\n")
        return result
    
    def detect_all_faces(self, image_path):
        """Detect all faces in image and return face info with crops"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Could not read image")
        
        faces = self.app.get(img)
        faces = sorted(faces, key=lambda x: x.bbox[0])  # Sort left to right
        
        face_data = []
        for idx, face in enumerate(faces):
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Crop face with padding
            pad = 20
            x1_pad = max(0, x1 - pad)
            y1_pad = max(0, y1 - pad)
            x2_pad = min(img.shape[1], x2 + pad)
            y2_pad = min(img.shape[0], y2 + pad)
            
            face_crop = img[y1_pad:y2_pad, x1_pad:x2_pad]
            
            face_data.append({
                'index': idx + 1,
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'crop': face_crop
            })
        
        return face_data, img

FaceSwapper = SharpFaceSwapper
