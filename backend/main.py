from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
import os
import uuid
import shutil
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
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "AI Virtual Try-On API (Async) is running"}

@app.post("/api/v1/try-on")
async def try_on_async(
    user_image: UploadFile = File(...),
    garment_image: UploadFile = File(...)
):
    """
    Submits a virtual try-on task to the Celery worker.
    Returns a task_id for polling.
    """
    try:
        # 1. Generate unique IDs and paths
        request_id = str(uuid.uuid4())
        user_path = os.path.join(UPLOAD_DIR, f"{request_id}_user.jpg")
        garment_path = os.path.join(UPLOAD_DIR, f"{request_id}_garment.jpg")
        output_path = os.path.join(OUTPUT_DIR, f"{request_id}_result.png")

        # 2. Save uploaded files to disk
        with open(user_path, "wb") as buffer:
            shutil.copyfileobj(user_image.file, buffer)
        with open(garment_path, "wb") as buffer:
            shutil.copyfileobj(garment_image.file, buffer)

        # 3. Trigger the Celery task
        task = vto_task.delay(user_path, garment_path, output_path)

        return JSONResponse({
            "status": "queued",
            "task_id": task.id,
            "message": "VTO task submitted successfully."
        })

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
