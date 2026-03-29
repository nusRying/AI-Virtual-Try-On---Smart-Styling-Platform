import os
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
except Exception:
    TORCH_AVAILABLE = False

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
        Check if the necessary weights are present by looking for key config files.
        """
        sam2_exists = False
        vton_exists = False
        
        # 1. Check SAM 2
        for root, dirs, files in os.walk(self.cache_dir):
            if "sam2_hiera_large.pt" in files:
                sam2_exists = True
                break
        
        # 2. Check for SDXL Inpaint Fallback
        sdxl_fallback_exists = False
        for root, dirs, files in os.walk(self.cache_dir):
            if "models--diffusers--stable-diffusion-xl-1.0-inpainting-0.1" in root and "snapshots" in root:
                # We found a snapshot folder, check if it has unet and vae
                snapshot_root = root
                if "unet" in dirs and "vae" in dirs:
                    # Check for actual weights
                    unet_weight = os.path.join(snapshot_root, "unet", "diffusion_pytorch_model.safetensors")
                    vae_weight = os.path.join(snapshot_root, "vae", "diffusion_pytorch_model.safetensors")
                    if os.path.exists(unet_weight) and os.path.exists(vae_weight):
                        sdxl_fallback_exists = True
                        break

        # 3. Check for SD 1.5 Inpaint (Efficiency Model)
        sd15_exists = False
        for root, dirs, files in os.walk(self.cache_dir):
            if "models--runwayml--stable-diffusion-inpainting" in root and "snapshots" in root:
                if "unet" in dirs and "vae" in dirs:
                    sd15_exists = True
                    break

        return {
            "sam2": sam2_exists,
            "idm_vton": vton_exists,
            "sdxl_fallback": sdxl_fallback_exists,
            "sd15_inpaint": sd15_exists
        }

def verify_models():
    manager = ModelManager()
    status = manager.verify_weights()
    print(f"SAM 2 Weights: {'FOUND' if status['sam2'] else 'MISSING'}")
    print(f"IDM-VTON Weights: {'FOUND' if status['idm_vton'] else 'MISSING'}")
    print(f"SDXL Fallback Weights: {'FOUND' if status['sdxl_fallback'] else 'MISSING'}")
    print(f"SD 1.5 Efficiency Weights: {'FOUND' if status['sd15_inpaint'] else 'MISSING'}")
    
    if status['idm_vton'] or status['sdxl_fallback'] or status['sd15_inpaint']:
        print("\nReady for Real Diffusion Inference.")
    else:
        print("\nReal Diffusion models are missing. Using Mock Mode.")

if __name__ == "__main__":
    verify_models()
