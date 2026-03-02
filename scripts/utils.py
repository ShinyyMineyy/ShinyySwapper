"""
ROOP Utility Script
Provides common maintenance and utility functions
"""

import os
import shutil
import argparse

def clean_temp_files():
    """Remove all temporary processing files"""
    temp_dirs = [
        'SinglePhoto/output',
        'SingleSrcMultiDst',
        'MultiSrcSingleDst',
        'MultiSrcMultiDst',
        'CustomSwap',
        'VideoSwapping/video_frames',
        'VideoSwapping/swapped_frames'
    ]
    
    temp_files = [
        'SinglePhoto/data_src.jpg',
        'SinglePhoto/data_dst.jpg',
        'VideoSwapping/data_src.jpg',
        'VideoSwapping/data_dst.mp4',
        'VideoSwapping/output_tmp_output_video.mp4',
        'VideoSwapping/output_with_audio.mp4',
        'project_backup.zip'
    ]
    
    print("Cleaning temporary files...")
    
    for dir_path in temp_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Removed: {dir_path}")
            except Exception as e:
                print(f"✗ Failed to remove {dir_path}: {e}")
    
    for file_path in temp_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Removed: {file_path}")
            except Exception as e:
                print(f"✗ Failed to remove {file_path}: {e}")
    
    print("\nCleanup complete!")

def check_disk_space():
    """Check available disk space"""
    import shutil
    total, used, free = shutil.disk_usage(".")
    
    print("Disk Space Information:")
    print(f"Total: {total // (2**30)} GB")
    print(f"Used:  {used // (2**30)} GB")
    print(f"Free:  {free // (2**30)} GB")
    
    if free < 5 * (2**30):  # Less than 5GB
        print("\n⚠ WARNING: Low disk space! Consider cleaning temp files.")

def create_directories():
    """Create necessary directories"""
    dirs = [
        'SinglePhoto',
        'SinglePhoto/output',
        'VideoSwapping'
    ]
    
    print("Creating directories...")
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ {dir_path}")
    
    print("\nDirectories ready!")

def backup_config():
    """Backup configuration file"""
    if os.path.exists('config.json'):
        import shutil
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'config_backup_{timestamp}.json'
        shutil.copy('config.json', backup_name)
        print(f"✓ Config backed up to: {backup_name}")
    else:
        print("✗ No config.json found to backup")

def show_stats():
    """Show processing statistics"""
    print("ROOP Statistics:")
    print("-" * 40)
    
    # Count output files
    output_dirs = {
        'Single Photos': 'SinglePhoto/output',
        'Video Outputs': 'VideoSwapping'
    }
    
    for name, path in output_dirs.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.mp4'))]
            print(f"{name}: {len(files)} files")
        else:
            print(f"{name}: 0 files")
    
    # Check model
    if os.path.exists('inswapper_128.onnx'):
        size_mb = os.path.getsize('inswapper_128.onnx') / (1024 * 1024)
        print(f"Model file: {size_mb:.1f} MB")
    else:
        print("Model file: Not found")

def main():
    parser = argparse.ArgumentParser(description='ROOP Utility Script')
    parser.add_argument('action', choices=['clean', 'space', 'setup', 'backup', 'stats'],
                       help='Action to perform')
    
    args = parser.parse_args()
    
    print("="*50)
    print("ROOP UTILITY SCRIPT")
    print("="*50 + "\n")
    
    if args.action == 'clean':
        clean_temp_files()
    elif args.action == 'space':
        check_disk_space()
    elif args.action == 'setup':
        create_directories()
    elif args.action == 'backup':
        backup_config()
    elif args.action == 'stats':
        show_stats()
    
    print("\n" + "="*50)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nError: {e}")
