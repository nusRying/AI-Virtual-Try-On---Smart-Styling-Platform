try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
except Exception:
    TORCH_AVAILABLE = False

import numpy as np
from PIL import Image
import os

from backend.core.preprocessor import Preprocessor

class VTONEngine:
    def __init__(self, model_id="yisol/IDM-VTON", device="cuda", force_real=False):
        """
        Initializes the VTO Engine with the SDXL-based IDM-VTON pipeline.
        """
        self.device = device if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"
        self.model_id = model_id
        
        # Determine if we should use mock mode based on weight availability
        from backend.core.models import ModelManager
        manager = ModelManager()
        weights_status = manager.verify_weights()
        
        # Try to use real mode if weights are there
        self.is_mock = not (weights_status["idm_vton"] or weights_status["sdxl_fallback"] or weights_status["sd15_inpaint"]) or not TORCH_AVAILABLE
        
        print(f"Initializing VTONEngine (Mock={self.is_mock}, ForceReal={force_real}) on {self.device}")
        self.pipeline = None

    def load_pipeline(self):
        """
        Loads the specialized diffusion pipeline if not in mock mode.
        """
        if self.is_mock:
            print("VTONEngine in Mock Mode: Skipping pipeline load.")
            return

        # Clear cache before loading heavy models
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        print(f"Loading AI Diffusion Pipeline...")
        try:
            # We prioritize SD 1.5 Inpainting for 4GB VRAM stability
            sd15_path = "runwayml/stable-diffusion-inpainting"
            
            # Find local path if exists
            manager = ModelManager()
            found_path = sd15_path
            for root, dirs, files in os.walk(manager.cache_dir):
                if "models--runwayml--stable-diffusion-inpainting" in root and "snapshots" in root:
                    snapshots = os.listdir(root)
                    if snapshots:
                        found_path = os.path.join(root, snapshots[0])
                        break

            from diffusers import StableDiffusionInpaintPipeline
            
            print(f"Initializing SD 1.5 from: {found_path}")
            self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                found_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                variant="fp16" if self.device == "cuda" else None,
                use_safetensors=True
            )
            
            if self.device == "cuda":
                # The most aggressive memory saving mode for 4GB VRAM
                self.pipeline.enable_sequential_cpu_offload()
                print("Sequential CPU offloading enabled (Max Memory Savings).")
                
                try:
                    self.pipeline.enable_xformers_memory_efficient_attention()
                except Exception:
                    pass
            else:
                self.pipeline.to("cpu")

            print("Real AI Pipeline (SD 1.5) loaded successfully.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading pipeline: {e}")
            # We don't force mock here, we let it fail or be retried
            print("Pipeline loading failed.")
            raise e

    def run_inference(self, user_image: Image.Image, garment_image: Image.Image, pose_data: list, person_mask: Image.Image):
        """
        Runs the VTO process (Real Diffusion or Smart Mock Masking).
        """
        if self.is_mock:
            print("VTONEngine: Running Smart Mock Masking...")
            # 1. Resize garment to match user photo
            width, height = user_image.size
            garment_resized = garment_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # 2. Use the AI-generated mask to only apply garment to the person's body
            # We soften the mask edges for a more natural transition
            from PIL import ImageFilter
            mask_soft = person_mask.resize((width, height)).filter(ImageFilter.GaussianBlur(radius=3))
            
            # 3. Composite the garment onto the user photo using the mask
            # Result = (Garment * Mask) + (User * (1-Mask))
            smart_output = Image.composite(garment_resized, user_image, mask_soft)
            
            # 4. Optional: Subtle blend to maintain some texture from the original photo
            final_output = Image.blend(smart_output, user_image, alpha=0.1)
            
            return final_output

        print("VTONEngine: Running Real Diffusion Inference (DISABLED due to RAM constraints)...")
        # if self.pipeline is None:
        #    self.load_pipeline()
        
        print("VTONEngine: Falling back to Smart Mock Masking for stability.")
        return self.run_inference(user_image, garment_image, pose_data, person_mask)

if __name__ == "__main__":
    import argparse
    from backend.core.models import ModelManager
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-user", type=str, required=True)
    parser.add_argument("--test-garment", type=str, required=True)
    parser.add_argument("--force-real", action="store_true")
    args = parser.parse_args()
    
    # Locate actual model path in cache
    manager = ModelManager()
    model_path = "yisol/IDM-VTON"
    found = False
    for root, dirs, files in os.walk(manager.cache_dir):
        if "models--yisol--IDM-VTON" in root and "snapshots" in root:
            # Get the first snapshot
            snapshots = os.listdir(root)
            if snapshots:
                model_path = os.path.join(root, snapshots[0])
                found = True
                break
    
    if not found:
        # Try fallback
        for root, dirs, files in os.walk(manager.cache_dir):
            if "models--diffusers--stable-diffusion-xl-1.0-inpainting-0.1" in root and "snapshots" in root:
                snapshots = os.listdir(root)
                if snapshots:
                    model_path = os.path.join(root, snapshots[0])
                    print(f"IDM-VTON not found. Using fallback: {model_path}")
                    found = True
                    break
    
    # 1. Pre-process
    preprocessor = Preprocessor()
    print("Running pre-processor...")
    user_results = preprocessor.process(args.test_user)
    
    pose_data = user_results["pose"]
    mask = user_results["mask"]
    
    if pose_data is None:
        print("Warning: No pose detected in user image. Using mock pose/mask for technical test.")
        # Create a dummy mask (full white)
        user_img = Image.open(args.test_user).convert("RGB")
        mask = Image.new("L", user_img.size, 255)
        pose_data = [] # Dummy pose
    
    # 2. Run Engine
    engine = VTONEngine(model_id=model_path, force_real=args.force_real)
    
    garment_img = Image.open(args.test_garment).convert("RGB")
    user_img = Image.open(args.test_user).convert("RGB")
    
    try:
        output_image = engine.run_inference(
            user_img, 
            garment_img, 
            pose_data, 
            mask
        )
        
        os.makedirs("temp/outputs", exist_ok=True)
        output_image.save("temp/outputs/test_vto_result.png")
        print("Inference completed! Saved to temp/outputs/test_vto_result.png")
    except Exception as e:
        print(f"Error during VTO inference: {e}")
