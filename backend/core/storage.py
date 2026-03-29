import os
import shutil
import uuid
import time
from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile

class BaseStorage(ABC):
    @abstractmethod
    def save_file(self, file: UploadFile, prefix: str = "") -> str:
        """Saves a file and returns its storage key/path."""
        pass

    @abstractmethod
    def save_pil_image(self, image, filename: str, prefix: str = "") -> str:
        """Saves a PIL Image and returns its storage key/path."""
        pass

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Returns a publicly accessible URL for the storage key."""
        pass

    @abstractmethod
    def get_local_path(self, key: str) -> str:
        """Returns the local file path (if applicable) for the storage key."""
        pass

    @abstractmethod
    def purge_old_files(self, max_age_seconds: int = 86400) -> int:
        """Deletes files older than max_age_seconds. Returns count of deleted files."""
        pass

class LocalStorage(BaseStorage):
    def __init__(self, base_dir: str = "backend/static", base_url: str = "/static"):
        self.base_dir = base_dir
        self.base_url = base_url
        os.makedirs(base_dir, exist_ok=True)

    def save_file(self, file: UploadFile, prefix: str = "") -> str:
        target_dir = os.path.join(self.base_dir, prefix)
        os.makedirs(target_dir, exist_ok=True)
        
        # Generate unique filename to avoid collisions
        ext = os.path.splitext(file.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4()}{ext}"
        key = os.path.join(prefix, unique_name).replace("\\", "/")
        
        full_path = os.path.join(self.base_dir, key)
        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return key

    def save_pil_image(self, image, filename: str, prefix: str = "") -> str:
        target_dir = os.path.join(self.base_dir, prefix)
        os.makedirs(target_dir, exist_ok=True)
        
        key = os.path.join(prefix, filename).replace("\\", "/")
        full_path = os.path.join(self.base_dir, key)
        
        image.save(full_path)
        return key

    def get_url(self, key: str) -> str:
        if not key:
            return ""
        return f"{self.base_url}/{key}"

    def get_local_path(self, key: str) -> str:
        if not key:
            return ""
        return os.path.join(self.base_dir, key)

    def delete_file(self, key: str) -> bool:
        path = self.get_local_path(key)
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
                return True
        return False

    def purge_old_files(self, max_age_seconds: int = 86400) -> int:
        count = 0
        now = time.time()
        
        for root, dirs, files in os.walk(self.base_dir):
            for name in files:
                file_path = os.path.join(root, name)
                if os.path.getmtime(file_path) < now - max_age_seconds:
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        print(f"Error purging {file_path}: {e}")
        
        return count

# Initialize the default storage provider
# For production, this could switch to S3Storage based on env vars
storage_provider = LocalStorage()
temp_storage = LocalStorage(base_dir="temp", base_url="/api/v1/results")
