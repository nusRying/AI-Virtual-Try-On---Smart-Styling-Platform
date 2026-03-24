from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from celery.result import AsyncResult
import os
import uuid
import shutil
import json
from typing import Optional
from backend.tasks import vto_task

app = FastAPI(title="AI Virtual Try-On API (Async)")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for file storage
UPLOAD_DIR = "temp/uploads"
OUTPUT_DIR = "temp/outputs"
GARMENTS_DATA_FILE = "backend/data/garments.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def root():
    return {"message": "AI Virtual Try-On API (Async) is running"}

@app.get("/api/v1/catalog")
async def get_catalog(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1)
):
    """
    Returns a searchable, paginated list of garments.
    """
    try:
        with open(GARMENTS_DATA_FILE, "r") as f:
            garments = json.load(f)
        
        # 1. Filter by query
        if q:
            q = q.lower()
            garments = [
                g for g in garments 
                if q in g["name"].lower() or any(q in tag.lower() for tag in g["tags"])
            ]

        total_count = len(garments)
        
        # 2. Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated_garments = garments[start:end]

        return {
            "garments": paginated_garments,
            "total_count": total_count,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/try-on")
async def try_on_async(
    user_image: UploadFile = File(...),
    garment_id: Optional[str] = Form(None),
    garment_image: Optional[UploadFile] = File(None)
):
    """
    Submits a virtual try-on task.
    Supports either a garment_id from the catalog OR a direct image upload.
    """
    try:
        # 1. Generate unique IDs and paths
        request_id = str(uuid.uuid4())
        user_path = os.path.join(UPLOAD_DIR, f"{request_id}_user.jpg")
        output_path = os.path.join(OUTPUT_DIR, f"{request_id}_result.png")
        garment_path = ""

        # 2. Save user image
        with open(user_path, "wb") as buffer:
            shutil.copyfileobj(user_image.file, buffer)

        # 3. Resolve garment image
        if garment_id:
            # Look up garment in JSON
            with open(GARMENTS_DATA_FILE, "r") as f:
                catalog = json.load(f)
            garment = next((g for g in catalog if g["id"] == garment_id), None)
            
            if not garment:
                raise HTTPException(status_code=404, detail="Garment not found in catalog.")
            
            # Resolve local path from static URL
            # Expected full_image_url: "/static/garments/shirt-1-full.jpg"
            # Local path: "backend/static/garments/shirt-1-full.jpg"
            garment_path = garment["full_image_url"].lstrip("/").replace("static", "backend/static")
            
            if not os.path.exists(garment_path):
                # For this prototype, if image is missing, we use a placeholder or error
                # We'll just use the path and let the task handle existence for now
                pass
        
        elif garment_image:
            garment_path = os.path.join(UPLOAD_DIR, f"{request_id}_garment.jpg")
            with open(garment_path, "wb") as buffer:
                shutil.copyfileobj(garment_image.file, buffer)
        
        else:
            raise HTTPException(status_code=400, detail="Either garment_id or garment_image must be provided.")

        # 4. Trigger the Celery task
        task = vto_task.delay(user_path, garment_path, output_path)

        return JSONResponse({
            "status": "queued",
            "task_id": task.id,
            "message": "VTO task submitted successfully."
        })

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """
    Polls the status of a specific VTO task.
    """
    task_result = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None
    }

    if task_result.status == 'SUCCESS':
        response["result"] = task_result.result
    elif task_result.status == 'FAILURE':
        response["error"] = str(task_result.info)
        
    return JSONResponse(response)

@app.get("/api/v1/results/{filename}")
async def get_vto_result(filename: str):
    """
    Retrieves the actual generated image file.
    """
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Result image not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
