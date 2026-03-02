"""
ROOP Installation Test Script
Run this to verify your installation is working correctly
"""

import sys
import os

def test_python_version():
    print("Testing Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def test_imports():
    print("\nTesting required packages...")
    packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'gradio': 'gradio',
        'insightface': 'insightface',
        'onnxruntime': 'onnxruntime',
        'sklearn': 'scikit-learn',
        'skimage': 'scikit-image',
        'tqdm': 'tqdm',
        'PIL': 'Pillow'
    }
    
    all_ok = True
    for module, package in packages.items():
        try:
            __import__(module)
            print(f"✓ {package} - OK")
        except ImportError:
            print(f"✗ {package} - MISSING")
            all_ok = False
    
    return all_ok

def test_gpu():
    print("\nTesting GPU availability...")
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        if 'CUDAExecutionProvider' in providers:
            print("✓ GPU (CUDA) - Available")
            return True
        else:
            print("⚠ GPU (CUDA) - Not available (CPU mode will be used)")
            return False
    except Exception as e:
        print(f"⚠ Could not check GPU: {e}")
        return False

def test_model_file():
    print("\nTesting model file...")
    if os.path.exists('inswapper_128.onnx'):
        size_mb = os.path.getsize('inswapper_128.onnx') / (1024 * 1024)
        print(f"✓ inswapper_128.onnx found ({size_mb:.1f} MB)")
        return True
    else:
        print("⚠ inswapper_128.onnx not found (will auto-download on first run)")
        return False

def test_face_analysis():
    print("\nTesting face analysis models...")
    try:
        from insightface.app import FaceAnalysis
        print("Initializing face analysis (this may take a moment)...")
        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=-1, det_size=(640, 640))
        print("✓ Face analysis models - OK")
        return True
    except Exception as e:
        print(f"✗ Face analysis failed: {e}")
        return False

def test_config():
    print("\nTesting configuration...")
    if os.path.exists('config.json'):
        try:
            import json
            with open('config.json', 'r') as f:
                config = json.load(f)
            print("✓ config.json - OK")
            return True
        except Exception as e:
            print(f"⚠ config.json exists but has errors: {e}")
            return False
    else:
        print("⚠ config.json not found (defaults will be used)")
        return False

def main():
    print("="*60)
    print("ROOP FACE SWAPPER - INSTALLATION TEST")
    print("="*60)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Required Packages", test_imports()))
    results.append(("GPU Support", test_gpu()))
    results.append(("Model File", test_model_file()))
    results.append(("Configuration", test_config()))
    results.append(("Face Analysis", test_face_analysis()))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    critical_tests = ["Python Version", "Required Packages", "Face Analysis"]
    critical_passed = all(passed for name, passed in results if name in critical_tests)
    
    for name, passed in results:
        status = "✓ PASS" if passed else ("✗ FAIL" if name in critical_tests else "⚠ WARN")
        print(f"{name:.<40} {status}")
    
    print("="*60)
    
    if critical_passed:
        print("\n✓ Installation is working! You can run: python app.py")
        return 0
    else:
        print("\n✗ Installation has issues. Please run setup.bat again.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
