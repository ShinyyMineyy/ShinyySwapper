"""
Auto-Installer for ROOP Face Swapper
Automatically checks and installs all required dependencies
"""

import subprocess
import sys
import importlib.util

def is_package_installed(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    print("="*60)
    print("ROOP AUTO-INSTALLER")
    print("="*60)
    print("\nChecking and installing required packages...\n")
    
    # Package mapping: import_name -> pip_package_name
    packages = {
        'numpy': 'numpy>=1.24.0,<2.0.0',
        'cv2': 'opencv-python>=4.8.0',
        'onnxruntime': 'onnxruntime>=1.16.0',
        'sklearn': 'scikit-learn>=1.3.0',
        'skimage': 'scikit-image>=0.21.0',
        'tqdm': 'tqdm>=4.66.0',
        'insightface': 'insightface>=0.7.3',
        'gradio': 'gradio>=4.0.0',
        'PIL': 'Pillow>=10.0.0',
        'rembg': 'rembg>=2.0.50',
        'pooch': 'pooch>=1.7.0'
    }
    
    missing_packages = []
    installed_packages = []
    
    # Check which packages are missing
    for import_name, pip_name in packages.items():
        if is_package_installed(import_name):
            print(f"✓ {import_name:15} - Already installed")
            installed_packages.append(import_name)
        else:
            print(f"✗ {import_name:15} - Missing")
            missing_packages.append(pip_name)
    
    if not missing_packages:
        print("\n" + "="*60)
        print("✓ All packages are already installed!")
        print("="*60)
        return True
    
    # Install missing packages
    print("\n" + "="*60)
    print(f"Installing {len(missing_packages)} missing package(s)...")
    print("="*60 + "\n")
    
    failed = []
    for package in missing_packages:
        if not install_package(package):
            failed.append(package)
    
    # Summary
    print("\n" + "="*60)
    print("INSTALLATION SUMMARY")
    print("="*60)
    print(f"Already installed: {len(installed_packages)}")
    print(f"Newly installed:   {len(missing_packages) - len(failed)}")
    print(f"Failed:            {len(failed)}")
    
    if failed:
        print("\nFailed packages:")
        for pkg in failed:
            print(f"  - {pkg}")
        print("\nTry installing manually:")
        print(f"  pip install {' '.join(failed)}")
        return False
    else:
        print("\n✓ All packages installed successfully!")
        print("="*60)
        return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nPress Enter to exit...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
