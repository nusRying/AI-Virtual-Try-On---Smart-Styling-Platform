import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.core.models import ModelManager
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=== AI Model Weight Setup ===")
    manager = ModelManager()
    
    # 1. Download SAM 2
    try:
        print("\n[1/2] Setting up SAM 2 (Segmentation)...")
        sam2_path = manager.download_sam2()
        print(f"SAM 2 Ready at: {sam2_path}")
    except Exception as e:
        print(f"Error downloading SAM 2: {e}")

    # 2. Download IDM-VTON
    try:
        print("\n[2/2] Setting up IDM-VTON (Virtual Try-On)...")
        print("Note: This is a large download (~20GB). Please ensure you have enough disk space.")
        vton_path = manager.download_idm_vton()
        print(f"IDM-VTON Ready at: {vton_path}")
    except Exception as e:
        print(f"Error downloading IDM-VTON: {e}")

    print("\n=== Setup Complete ===")

if __name__ == "__main__":
    main()
