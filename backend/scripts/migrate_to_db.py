import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.db import SessionLocal, Garment, init_db

GARMENTS_JSON = "backend/data/garments.json"

def migrate():
    print("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    
    if not os.path.exists(GARMENTS_JSON):
        print(f"No JSON found at {GARMENTS_JSON}. Skipping migration.")
        return

    with open(GARMENTS_JSON, "r") as f:
        garments_data = json.load(f)

    print(f"Found {len(garments_data)} items in JSON. Migrating...")
    
    for item in garments_data:
        # Check if already exists
        existing = db.query(Garment).filter(Garment.id == item["id"]).first()
        if existing:
            print(f"Item {item['id']} already in DB. Skipping.")
            continue
            
        new_garment = Garment(
            id=item["id"],
            name=item["name"],
            category=item.get("category", "Shirts"),
            price=item["price"],
            description=item.get("description", ""),
            thumbnail_url=item["thumbnail_url"],
            full_image_url=item["full_image_url"],
            tags=",".join(item.get("tags", [])),
            try_on_count=item.get("try_on_count", 0)
        )
        db.add(new_garment)
    
    db.commit()
    db.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
