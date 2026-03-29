import os
import weaviate
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class VectorDB:
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = api_key or os.getenv("WEAVIATE_API_KEY")
        
        # Lazy initialize CLIP model
        self._model = None
        
        self.client = None
        self.is_connected = False
        
        try:
            # Weaviate v4 uses a different initialization
            host = self.url.split("//")[-1].split(":")[0]
            try:
                port = int(self.url.split(":")[-1].split("/")[0])
            except:
                port = 8080

            self.client = weaviate.connect_to_custom(
                http_host=host,
                http_port=port,
                http_secure=self.url.startswith("https"),
                grpc_host=host,
                grpc_port=50051,
                grpc_secure=self.url.startswith("https"),
                auth_credentials=weaviate.auth.AuthApiKey(api_key=self.api_key) if self.api_key else None
            )
            self.is_connected = self.client.is_live()
            if self.is_connected:
                self._setup_schema()
        except Exception as e:
            print(f"Weaviate connection failed: {e}. Running in mock/disabled mode.")

    @property
    def model(self):
        if self._model is None:
            print("Loading CLIP model for embeddings...")
            self._model = SentenceTransformer('clip-ViT-B-32')
        return self._model

    def _setup_schema(self):
        try:
            from weaviate.classes.config import Property, DataType
            
            if not self.client.collections.exists("Garment"):
                self.client.collections.create(
                    name="Garment",
                    properties=[
                        Property(name="garment_id", data_type=DataType.TEXT),
                        Property(name="name", data_type=DataType.TEXT),
                        Property(name="category", data_type=DataType.TEXT),
                        Property(name="tags", data_type=DataType.TEXT_ARRAY),
                        Property(name="description", data_type=DataType.TEXT)
                    ]
                )
        except Exception as e:
            print(f"Schema setup failed: {e}")

    def index_garment(self, garment_id: str, name: str, category: str, tags: List[str], description: str, image_path: str = None):
        if not self.is_connected:
            return
            
        # Generate embedding
        text_to_embed = f"{name} {category} {' '.join(tags)} {description}"
        vector = self.model.encode(text_to_embed).tolist()
        
        try:
            garments = self.client.collections.get("Garment")
            garments.data.insert(
                properties={
                    "garment_id": garment_id,
                    "name": name,
                    "category": category,
                    "tags": tags,
                    "description": description
                },
                vector=vector,
                uuid=weaviate.util.generate_uuid5(garment_id)
            )
        except Exception as e:
            print(f"Failed to insert {garment_id}: {e}")

    def search_similar(self, query_text: str = None, query_image_path: str = None, limit: int = 5) -> List[str]:
        if not self.is_connected:
            return []
            
        if query_text:
            vector = self.model.encode(query_text).tolist()
        else:
            return []
            
        try:
            garments = self.client.collections.get("Garment")
            results = garments.query.near_vector(
                near_vector=vector,
                limit=limit,
                return_properties=["garment_id"]
            )
            
            return [obj.properties["garment_id"] for obj in results.objects]
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def close(self):
        if self.client:
            self.client.close()

# Singleton instance
vector_db = VectorDB()
