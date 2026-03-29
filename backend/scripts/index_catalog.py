import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.db import SessionLocal, Garment
from backend.core.vector_db import vector_db

def index_existing_catalog():
    """
    Fetches all garments from the SQL database and indexes them in Weaviate.
    """
    db = SessionLocal()
    try:
        garments = db.query(Garment).all()
        print(f"Found {len(garments)} garments to index...")
        
        if not vector_db.is_connected:
            print("Error: Weaviate is not connected. Start Weaviate first.")
            return

        for g in garments:
            print(f"Indexing: {g.name} ({g.id})")
            vector_db.index_garment(
                garment_id=g.id,
                name=g.name,
                category=g.category,
                tags=g.tags.split(",") if g.tags else [],
                description=g.description or ""
            )
            
        print("Catalog indexing complete!")
    except Exception as e:
        print(f"Indexing error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    index_existing_catalog()
