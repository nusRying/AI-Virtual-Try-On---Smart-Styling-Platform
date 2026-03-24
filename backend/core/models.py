import os
import torch
from huggingface_hub import hf_hub_download, snapshot_download

class ModelManager:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.getenv("MODEL_CACHE_DIR", "./models/cache/")
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def download_sam2(self, model_id="facebook/sam2-hiera-large"):
        """
        Downloads SAM 2 weights from HuggingFace.
        """
        print(f"Downloading SAM 2 weights from {model_id}...")
        # SAM 2 repo usually contains the .pt checkpoint
        checkpoint_path = hf_hub_download(
            repo_id=model_id,
            filename="sam2_hiera_large.pt",
            cache_dir=self.cache_dir
        )
        return checkpoint_path

    def download_idm_vton(self, repo_id="yisol/IDM-VTON"):
        """
        Downloads the full IDM-VTON model repository.
        This is an SDXL-based model and can be quite large (~15-20GB).
        """
        print(f"Downloading IDM-VTON weights from {repo_id}...")
        # We use snapshot_download to get the entire folder structure (UNet, VAE, etc.)
        model_path = snapshot_download(
            repo_id=repo_id,
            cache_dir=self.cache_dir,
            ignore_patterns=["*.msgpack", "*.bin", "*.h5"] # Optionally ignore non-pytorch weights
        )
        return model_path

    def verify_weights(self):
        """
        Check if the necessary weights are present.
        """
        # This is a simplified check
        sam2_exists = any("sam2_hiera_large.pt" in f for root, dirs, files in os.walk(self.cache_dir) for f in files)
        vton_exists = os.path.exists(os.path.join(self.cache_dir, "models--yisol--IDM-VTON")) or \
                      any("IDM-VTON" in d for root, d, files in os.walk(self.cache_dir) for d in d)
                      
        return {
            "sam2": sam2_exists,
            "idm_vton": vton_exists
        }

def verify_models():
    manager = ModelManager()
    status = manager.verify_weights()
    print(f"SAM 2 Weights: {'FOUND' if status['sam2'] else 'MISSING'}")
    print(f"IDM-VTON Weights: {'FOUND' if status['idm_vton'] else 'MISSING'}")
    
    if not all(status.values()):
        print("\nUse ModelManager.download_sam2() or download_idm_vton() to fetch missing weights.")
    else:
        print("\nAll required model weights are present.")

if __name__ == "__main__":
    verify_models()
