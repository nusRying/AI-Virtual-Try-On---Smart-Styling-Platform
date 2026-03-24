import os
from PIL import Image
from backend.celery_app import celery_app
from backend.core.preprocessor import Preprocessor
from backend.core.vton_engine import VTONEngine

# Lazy initialization inside the worker process
_preprocessor = None
_engine = None

def get_preprocessor():
    global _preprocessor
    if _preprocessor is None:
        print("Initializing Preprocessor for worker...")
        _preprocessor = Preprocessor()
    return _preprocessor

def get_engine():
    global _engine
    if _engine is None:
        print("Initializing VTONEngine for worker...")
        _engine = VTONEngine()
    return _engine

@celery_app.task(name="backend.tasks.vto_task")
def vto_task(user_image_path, garment_image_path, output_path):
    """
    Celery task that performs the virtual try-on pipeline.
    """
    try:
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
        
        # 3. Save result
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_pil.save(output_path)
        
        print(f"Task completed! Output saved to {output_path}")
        return {"status": "success", "output_path": output_path}
        
    except Exception as e:
        print(f"Task error: {str(e)}")
        return {"status": "error", "message": str(e)}
