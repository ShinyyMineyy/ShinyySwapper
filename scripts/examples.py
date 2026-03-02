"""
Example Script - Using ROOP Programmatically

This script shows how to use ROOP face swapper in your own Python code
without the Gradio UI.
"""

import cv2
import os
from SinglePhoto import FaceSwapper

def simple_face_swap_example():
    """
    Basic example: Swap faces between two images
    """
    print("Example 1: Simple Face Swap")
    print("-" * 40)
    
    # Initialize the face swapper
    print("Initializing face swapper...")
    swapper = FaceSwapper()
    
    # Define paths
    source_path = "path/to/source_face.jpg"  # Replace with your image
    target_path = "path/to/target_image.jpg"  # Replace with your image
    output_path = "output_swapped.jpg"
    
    # Check if files exist
    if not os.path.exists(source_path):
        print(f"Error: Source image not found: {source_path}")
        return
    
    if not os.path.exists(target_path):
        print(f"Error: Target image not found: {target_path}")
        return
    
    try:
        # Perform face swap
        print("Swapping faces...")
        result = swapper.swap_faces(
            source_path=source_path,
            source_face_idx=1,  # First face in source
            target_path=target_path,
            target_face_idx=1,  # First face in target
            swap_hair=False  # Set to True for hair transplant
        )
        
        # Save result
        cv2.imwrite(output_path, result)
        print(f"✓ Success! Result saved to: {output_path}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

def batch_face_swap_example():
    """
    Advanced example: Swap one face onto multiple images
    """
    print("\nExample 2: Batch Face Swap")
    print("-" * 40)
    
    swapper = FaceSwapper()
    
    source_path = "path/to/source_face.jpg"
    target_folder = "path/to/target_images/"
    output_folder = "batch_output/"
    
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all images in target folder
    target_images = [f for f in os.listdir(target_folder) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"Found {len(target_images)} target images")
    
    for i, target_file in enumerate(target_images, 1):
        target_path = os.path.join(target_folder, target_file)
        output_path = os.path.join(output_folder, f"swapped_{target_file}")
        
        try:
            print(f"Processing {i}/{len(target_images)}: {target_file}...", end=" ")
            
            result = swapper.swap_faces(
                source_path=source_path,
                source_face_idx=1,
                target_path=target_path,
                target_face_idx=1
            )
            
            cv2.imwrite(output_path, result)
            print("✓")
            
        except Exception as e:
            print(f"✗ Error: {e}")

def custom_config_example():
    """
    Example: Using custom configuration
    """
    print("\nExample 3: Custom Configuration")
    print("-" * 40)
    
    # Custom configuration
    config = {
        "detection_size": [320, 320],  # Smaller = faster but less accurate
        "face_analysis_model": "buffalo_l",
        "enable_gpu": True,
        "gpu_id": 0
    }
    
    # Initialize with custom config
    swapper = FaceSwapper(config=config)
    
    print("Face swapper initialized with custom config")
    print(f"Detection size: {config['detection_size']}")
    print(f"GPU enabled: {config['enable_gpu']}")

def count_faces_example():
    """
    Example: Count faces in an image
    """
    print("\nExample 4: Count Faces")
    print("-" * 40)
    
    from insightface.app import FaceAnalysis
    
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(640, 640))
    
    image_path = "path/to/image.jpg"
    
    if os.path.exists(image_path):
        img = cv2.imread(image_path)
        faces = app.get(img)
        print(f"Found {len(faces)} face(s) in the image")
        
        for i, face in enumerate(faces, 1):
            bbox = face.bbox.astype(int)
            print(f"Face {i}: Position ({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})")
    else:
        print(f"Image not found: {image_path}")

def main():
    """
    Run all examples
    """
    print("="*50)
    print("ROOP FACE SWAPPER - EXAMPLE SCRIPTS")
    print("="*50)
    print("\nNote: Update the file paths in this script before running!")
    print()
    
    # Uncomment the examples you want to run:
    
    # simple_face_swap_example()
    # batch_face_swap_example()
    # custom_config_example()
    # count_faces_example()
    
    print("\n" + "="*50)
    print("Examples complete!")
    print("="*50)

if __name__ == "__main__":
    main()
