from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import io
from PIL import Image
import os
from backend.core.preprocessor import Preprocessor
from backend.core.vton_engine import VTONEngine

app = FastAPI(title="AI Virtual Try-On API")

# Initialize models (in a production scenario, these would be loaded lazily or on startup)
preprocessor = Preprocessor()
engine = VTONEngine()

@app.get("/")
async def root():
    return {"message": "AI Virtual Try-On API is running"}

@app.post("/api/v1/try-on")
async def try_on(
    user_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    """
    Performs a virtual try-on:
    1. Pre-processes the user image (pose + mask).
    2. Runs the VTO inference.
    3. Returns the merged result as a PNG.
    """
    try:
        # Read uploaded files into memory as PIL images
        user_bytes = await user_image.read()
        garment_bytes = await garment_image.read()
        
        user_pil = Image.open(io.BytesIO(user_bytes)).convert("RGB")
        garment_pil = Image.open(io.BytesIO(garment_bytes)).convert("RGB")
        
        # Temporary save to local disk for preprocessor (it currently expects paths)
        os.makedirs("temp", exist_ok=True)
        user_path = "temp/input_user.jpg"
        user_pil.save(user_path)
        
        # 1. Pre-processing (Pose + Mask)
        print("Step 1: Pre-processing...")
        prep_results = preprocessor.process(user_path)
        
        if not prep_results["pose"]:
            raise HTTPException(status_code=400, detail="No pose detected in user image.")
            
        # 2. VTO Inference
        print("Step 2: VTO Inference...")
        output_pil = engine.run_inference(
            user_pil, 
            garment_pil, 
            prep_results["pose"], 
            prep_results["mask"]
        )
        
        # 3. Format result for response
        img_byte_arr = io.BytesIO()
        output_pil.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
        
    except Exception as e:
        print(f"Error in try-on pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
