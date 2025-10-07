# D:\ArsaWebDeveloper\Project\Vexta\database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse


env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


DB_USER = os.getenv("DB_USER")
DB_PASSWORD_RAW = os.getenv("DB_PASSWORD")
DB_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD_RAW) if DB_PASSWORD_RAW else None
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("❌ مقادیر محیطی اتصال دیتابیس ناقص است!")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from models import Message, PDFChunk
    from auth.models import User 
    Base.metadata.create_all(bind=engine)
    print("✅ جداول ساخته شدند.")

if __name__ == "__main__":
    create_tables()
