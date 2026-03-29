from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import shutil
import json
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
except Exception:
    # Handle DLL load errors on Windows
    TORCH_AVAILABLE = False

from typing import Optional, List
from dotenv import load_dotenv
from backend.core.recommendations import RecommendationEngine
from backend.core.reasoner import StylingReasoner
from backend.core.db import init_db, get_db, Garment
from backend.core.storage import storage_provider, temp_storage
from backend.core.vector_db import vector_db
from sqlalchemy.orm import Session
from fastapi import Depends

load_dotenv()

app = FastAPI(title="AI Virtual Try-On API (Async)")

# Initialize DB
init_db()

# Initialize Engines
rec_engine = RecommendationEngine()
styling_reasoner = StylingReasoner()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for file storage
GARMENTS_DATA_FILE = "backend/data/garments.json"

VTO_DEPENDENCY_ERROR = (
    "The try-on worker dependencies are not available. "
    "Install the backend requirements and start Redis/Celery before using try-on endpoints."
)

QUEUE_UNAVAILABLE_ERROR = (
    "Redis is not reachable. Start Redis and the Celery worker before using try-on endpoints."
)

# Serve static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def root():
    return {"message": "AI Virtual Try-On API (Async) is running"}

@app.get("/api/v1/catalog")
async def get_catalog(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1),
    semantic: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Returns a searchable, paginated list of garments.
    Supports both traditional and semantic search.
    """
    try:
        query = db.query(Garment)
        
        # 1. Handle Search
        if q:
            if semantic and vector_db.is_connected:
                # Use vector search
                similar_ids = vector_db.search_similar(query_text=q, limit=50)
                if similar_ids:
                    query = query.filter(Garment.id.in_(similar_ids))
                else:
                    # Fallback if no vector results
                    search = f"%{q.lower()}%"
                    query = query.filter((Garment.name.ilike(search)) | (Garment.tags.ilike(search)))
            else:
                # Traditional keyword search
                search = f"%{q.lower()}%"
                query = query.filter(
                    (Garment.name.ilike(search)) | 
                    (Garment.tags.ilike(search))
                )

        total_count = query.count()
        
        # 2. Paginate
        garments = query.offset((page - 1) * limit).limit(limit).all()

        # 3. Format response
        result = []
        for g in garments:
            result.append({
                "id": g.id,
                "name": g.name,
                "category": g.category,
                "price": g.price,
                "description": g.description,
                "thumbnail_url": g.thumbnail_url,
                "full_image_url": g.full_image_url,
                "tags": g.tags.split(",") if g.tags else [],
                "try_on_count": g.try_on_count
            })

        return {
            "garments": result,
            "total_count": total_count,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/catalog")
async def add_to_catalog(
    name: str = Form(...),
    price: float = Form(...),
    category: str = Form("Shirts"),
    description: str = Form(""),
    tags: str = Form(""),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Allows merchants to add new garments to the catalog.
    """
    try:
        garment_id = f"custom-{str(uuid.uuid4())[:8]}"
        
        # 1. Save the image using storage provider
        key = storage_provider.save_file(image, prefix="garments")
        image_url = storage_provider.get_url(key)
            
        # 2. Update DB
        new_garment = Garment(
            id=garment_id,
            name=name,
            category=category,
            price=price,
            description=description,
            thumbnail_url=image_url,
            full_image_url=image_url,
            tags=tags,
            try_on_count=0
        )
        db.add(new_garment)
        db.commit()
        db.refresh(new_garment)
        
        # 3. Index in vector DB for semantic search
        try:
            vector_db.index_garment(
                garment_id=new_garment.id,
                name=new_garment.name,
                category=new_garment.category,
                tags=new_garment.tags.split(",") if new_garment.tags else [],
                description=new_garment.description
            )
        except Exception as ve:
            print(f"Failed to index in vector DB: {ve}")
            
        return {
            "status": "success", 
            "garment": {
                "id": new_garment.id,
                "name": new_garment.name,
                "price": new_garment.price,
                "tags": new_garment.tags.split(",") if new_garment.tags else []
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/catalog/{garment_id}")
async def delete_from_catalog(garment_id: str, db: Session = Depends(get_db)):
    """
    Removes a garment from the catalog.
    """
    try:
        garment = db.query(Garment).filter(Garment.id == garment_id).first()
        if not garment:
            raise HTTPException(status_code=404, detail="Garment not found.")
            
        # Delete image from storage
        if garment.full_image_url:
            key = garment.full_image_url.replace("/static/", "")
            storage_provider.delete_file(key)

        db.delete(garment)
        db.commit()
            
        return {"status": "success", "message": f"Garment {garment_id} deleted."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

def increment_try_on_count(garment_id: str, db: Session):
    try:
        garment = db.query(Garment).filter(Garment.id == garment_id).first()
        if garment:
            garment.try_on_count += 1
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating metrics: {e}")

def get_vto_task():
    try:
        from backend.tasks import vto_task
        return vto_task
    except ImportError as e:
        raise HTTPException(status_code=503, detail=VTO_DEPENDENCY_ERROR) from e

def ensure_queue_available():
    # Force mock_redis for local testing without actual Redis
    mock_redis = True 
    if mock_redis:
        return # Skip Redis check in mock mode

    try:
        import redis
        from backend.celery_app import redis_url

        client = redis.Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        client.ping()
    except ImportError as e:
        raise HTTPException(status_code=503, detail=VTO_DEPENDENCY_ERROR) from e
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail=QUEUE_UNAVAILABLE_ERROR) from e

def get_async_result(task_id: str):
    try:
        from backend.celery_app import celery_app
        return celery_app.AsyncResult(task_id)
    except ImportError as e:
        raise HTTPException(status_code=503, detail=VTO_DEPENDENCY_ERROR) from e

@app.post("/api/v1/try-on")
async def try_on_async(
    user_image: UploadFile = File(...),
    garment_id: Optional[str] = Form(None),
    garment_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Submits a virtual try-on task.
    Supports either a garment_id from the catalog OR a direct image upload.
    """
    try:
        # 1. Generate unique IDs and storage keys
        request_id = str(uuid.uuid4())
        
        # 2. Save user image using temp storage
        user_key = temp_storage.save_file(user_image, prefix="uploads")
        user_path = temp_storage.get_local_path(user_key)
        
        # Prepare output path in temp storage
        output_filename = f"{request_id}_result.png"
        output_key = f"outputs/{output_filename}"
        output_path = temp_storage.get_local_path(output_key)
        
        garment_path = ""

        # 3. Resolve garment image
        if garment_id:
            increment_try_on_count(garment_id, db)
            # Look up garment in DB
            garment = db.query(Garment).filter(Garment.id == garment_id).first()
            
            if not garment:
                raise HTTPException(status_code=404, detail="Garment not found in catalog.")
            
            # Resolve local path from storage key/URL
            # Assume full_image_url is /static/garments/filename.jpg
            garment_key = garment.full_image_url.replace("/static/", "")
            garment_path = storage_provider.get_local_path(garment_key)
        
        elif garment_image:
            garment_key = temp_storage.save_file(garment_image, prefix="uploads")
            garment_path = temp_storage.get_local_path(garment_key)
        
        else:
            raise HTTPException(status_code=400, detail="Either garment_id or garment_image must be provided.")

        # 4. Trigger the Celery task
        ensure_queue_available()
        
        # In mock/eager mode, we run synchronously to avoid broker dependency
        from backend.celery_app import mock_redis
        if mock_redis:
            task = get_vto_task().apply(args=[user_path, garment_path, output_path])
            return JSONResponse({
                "status": "SUCCESS",
                "task_id": task.id,
                "result": task.result,
                "message": "VTO task completed synchronously (Mock Mode)."
            })
        
        task = get_vto_task().delay(user_path, garment_path, output_path)

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
    ensure_queue_available()
    task_result = get_async_result(task_id)
    
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

@app.get("/api/v1/recommendations/{garment_id}")
async def get_recommendations(garment_id: str, db: Session = Depends(get_db)):
    """
    Returns 'Complete the Look' recommendations using semantic search.
    """
    try:
        # 1. Fetch the original item details
        garment = db.query(Garment).filter(Garment.id == garment_id).first()
        if not garment:
             raise HTTPException(status_code=404, detail="Garment not found.")
             
        # 2. Search for similar/matching items in vector DB
        # We query using the tags and description of the current item
        query_text = f"clothing that matches with {garment.name} {garment.tags} {garment.description}"
        similar_ids = vector_db.search_similar(query_text=query_text, limit=10)
        
        # 3. Fetch matched garments from SQL DB (excluding current item)
        matched_garments = db.query(Garment).filter(
            (Garment.id.in_(similar_ids)) & (Garment.id != garment_id)
        ).all()
        
        # Format for reasoner
        matched_items = []
        for mg in matched_garments:
            matched_items.append({
                "id": mg.id,
                "name": mg.name,
                "category": mg.category,
                "price": mg.price,
                "thumbnail_url": mg.thumbnail_url,
                "tags": mg.tags.split(",") if mg.tags else []
            })
            
        selected_item = {
            "id": garment.id,
            "name": garment.name,
            "category": garment.category,
            "price": garment.price,
            "tags": garment.tags.split(",") if garment.tags else []
        }
        
        # 4. Generate styling tip
        styling_tip = styling_reasoner.generate_styling_tip(selected_item, matched_items)
        
        return {
            "recommendations": matched_items,
            "styling_tip": styling_tip
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/system/status")
async def get_system_status():
    """
    Returns the status of AI models and backend infrastructure.
    """
    try:
        from backend.core.models import ModelManager
        from backend.celery_app import mock_redis
        
        manager = ModelManager()
        model_status = manager.verify_weights()
        
        return {
            "models": model_status,
            "queue": {
                "mode": "mock" if mock_redis else "production",
                "connected": True if mock_redis else False 
            },
            "device": ("cuda" if torch.cuda.is_available() else "cpu") if TORCH_AVAILABLE else "unknown (torch missing)"
        }
    except Exception as e:
        print(f"System status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/system/setup")
async def setup_models(model: str = Query(..., enum=["sam2", "idm_vton", "all"])):
    """
    Triggers the download of AI model weights.
    """
    from backend.core.models import ModelManager
    manager = ModelManager()
    
    try:
        if model == "sam2" or model == "all":
            manager.download_sam2()
        if model == "idm_vton" or model == "all":
            manager.download_idm_vton()
            
        return {"status": "success", "message": f"Successfully triggered download for {model}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/system/cleanup")
async def cleanup_temp_files(max_age_hours: int = Query(24, ge=1)):
    """
    Purges old temporary files from storage.
    """
    try:
        count = temp_storage.purge_old_files(max_age_seconds=max_age_hours * 3600)
        return {"status": "success", "deleted_files": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/results/{filename}")
async def get_vto_result(filename: str):
    """
    Retrieves the actual generated image file.
    """
    file_path = temp_storage.get_local_path(f"outputs/{filename}")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="Result image not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
