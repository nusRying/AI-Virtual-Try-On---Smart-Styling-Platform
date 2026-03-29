import os
import sys
import requests
import uuid
from PIL import Image
from io import BytesIO

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.db import SessionLocal, Garment, init_db
from backend.core.vector_db import vector_db

# High quality Unsplash source images for different categories
GARMENT_SOURCES = {
    "Shirts": [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?q=80&w=800", # White Tee
        "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?q=80&w=800", # Pattern Shirt
        "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?q=80&w=800", # Flannel
        "https://images.unsplash.com/photo-1598033129183-c4f50c7176c8?q=80&w=800", # Black Shirt
        "https://images.unsplash.com/photo-1620012253295-c05718565d6d?q=80&w=800", # White Oxford
        "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?q=80&w=800", # Denim Shirt
        "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?q=80&w=800", # Black Tee
        "https://images.unsplash.com/photo-1581655353564-df123a1eb820?q=80&w=800", # Polo
    ],
    "Pants": [
        "https://images.unsplash.com/photo-1473966968600-fa804b869a1a?q=80&w=800", # Chinos
        "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?q=80&w=800", # Jeans
        "https://images.unsplash.com/photo-1517445312882-bc9910d016b7?q=80&w=800", # Cargo
        "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?q=80&w=800", # Linen Pants
    ],
    "Shoes": [
        "https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=800", # White Sneakers
        "https://images.unsplash.com/photo-1531310197839-ccf54634509e?q=80&w=800", # Brown Loafers
        "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?q=80&w=800", # Chelsea Boots
        "https://images.unsplash.com/photo-1560769629-975ec94e6a86?q=80&w=800", # Athletic
    ]
}

def download_and_save(url, filename):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content)).convert("RGB")
            # Resize to standard 800x1200 for VTO consistency
            img = img.resize((800, 1200), Image.Resampling.LANCZOS)
            
            path = os.path.join("backend/static/garments", filename)
            img.save(path, "JPEG", quality=90)
            return f"/static/garments/{filename}"
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def expand():
    db = SessionLocal()
    init_db()
    
    print("Expanding catalog with high-quality images...")
    
    items_added = 0
    for category, urls in GARMENT_SOURCES.items():
        for i, url in enumerate(urls):
            item_id = f"hq-{category.lower()}-{i+1}"
            
            # Check if exists
            existing = db.query(Garment).filter(Garment.id == item_id).first()
            if existing:
                continue
                
            filename = f"{item_id}.jpg"
            stored_url = download_and_save(url, filename)
            
            if stored_url:
                new_item = Garment(
                    id=item_id,
                    name=f"Premium {category[:-1] if category.endswith('s') else category} Vol.{i+1}",
                    category=category,
                    price=45.0 + (i * 15),
                    description=f"High-quality {category.lower()} for professional virtual try-on.",
                    thumbnail_url=stored_url,
                    full_image_url=stored_url,
                    tags=f"{category.lower()},premium,style-{i}",
                    try_on_count=0
                )
                db.add(new_item)
                db.commit()
                
                # Index in vector DB
                try:
                    if vector_db.is_connected:
                        print(f"Indexing {new_item.id}...")
                        vector_db.index_garment(
                            garment_id=new_item.id,
                            name=new_item.name,
                            category=new_item.category,
                            tags=new_item.tags.split(","),
                            description=new_item.description
                        )
                except Exception as e:
                    print(f"Vector indexing failed for {new_item.id}: {e}")
                    
                items_added += 1
                print(f"Added: {new_item.name}")

    print(f"Catalog expanded by {items_added} items.")
    db.close()

if __name__ == "__main__":
    expand()
