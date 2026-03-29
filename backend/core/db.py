from sqlalchemy import Column, String, Float, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/data/vto.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Garment(Base):
    __tablename__ = "garments"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True, default="Shirts")
    price = Column(Float)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(String)
    full_image_url = Column(String)
    tags = Column(String)  # Comma-separated tags
    try_on_count = Column(Integer, default=0)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
