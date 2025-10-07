import string
from sqlalchemy import Column, Integer, Text, DateTime, Float, JSON, String
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_reply = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class PDFChunk(Base):
    __tablename__ = "pdf_chunks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    chunk = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)  # برای ذخیره لیست بردارها (vector)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class PDFChunkCreate(BaseModel):
    filename: str = Field(..., description="نام فایل PDF")
    chunk: str = Field(..., description="متن قسمتی از PDF")
    embedding: List[float] = Field(..., description="بردار embedding متن")

    class Config:
        schema_extra = {
            "example": {
                "filename": "example.pdf",
                "chunk": "این یک نمونه متن از فایل PDF است",
                "embedding": [0.1, 0.2, 0.3]
            }
        }

class PDFChunkResponse(BaseModel):
    id: int
    filename: str
    chunk: str
    embedding: List[float]
    created_at: datetime

    class Config:
        from_attributes = True
