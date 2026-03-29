import os
from backend.celery_app import celery_app
from backend.core.storage import temp_storage

# Lazy initialization inside the worker process
_preprocessor = None
_engine = None

def get_preprocessor():
    global _preprocessor
    if _preprocessor is None:
        print("Initializing Preprocessor for worker...")
        try:
            from backend.core.preprocessor import Preprocessor
        except ImportError as e:
            raise RuntimeError(
                "Preprocessor dependencies are missing. Install the backend AI requirements before running the worker."
            ) from e
        _preprocessor = Preprocessor()
    return _preprocessor

def get_engine():
    global _engine
    if _engine is None:
        print("Initializing VTONEngine for worker...")
        try:
            from backend.core.vton_engine import VTONEngine
        except ImportError as e:
            raise RuntimeError(
                "VTON engine dependencies are missing. Install the backend AI requirements before running the worker."
            ) from e
        _engine = VTONEngine()
    return _engine

@celery_app.task(name="backend.tasks.vto_task")
def vto_task(user_image_path, garment_image_path, output_path):
    """
    Celery task that performs the virtual try-on pipeline.
    """
    try:
        from PIL import Image

        # Load components
        prep = get_preprocessor()
        engine = get_engine()
        
        # 1. Pre-process
        print(f"Task: Pre-processing {user_image_path}...")
        prep_results = prep.process(user_image_path)
        
        if not prep_results["pose"]:
            return {"status": "error", "message": "No pose detected in user image"}
            
        # 2. Run Inference
        print("Task: Running VTO Inference...")
        user_img = Image.open(user_image_path).convert("RGB")
        garment_img = Image.open(garment_image_path).convert("RGB")
        
        output_pil = engine.run_inference(
            user_img,
            garment_img,
            prep_results["pose"],
            prep_results["mask"]
        )
        
        # 3. Save result using temp storage
        filename = os.path.basename(output_path)
        key = temp_storage.save_pil_image(output_pil, filename, prefix="outputs")
        
        # Return the public URL or relative path for the client
        result_url = temp_storage.get_url(key)
        
        print(f"Task completed! Output saved as {key}")
        return {
            "status": "success", 
            "result_url": result_url, 
            "filename": filename,
            "output_path": key # Backwards compatibility
        }
        
    except Exception as e:
        print(f"Task error: {str(e)}")
        return {"status": "error", "message": str(e)}
