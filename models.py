from sqlalchemy import Column, Integer, Text, DateTime, JSON, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=True, index=True)
    user_message = Column(Text, nullable=False)
    bot_reply = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="messages")


class PDFChunk(Base):
    __tablename__ = "pdf_chunks"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    chunk = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="pdf_chunks")


class PDFChunkCreate(BaseModel):
    filename: str = Field(..., description="نام فایل PDF")
    chunk: str = Field(..., description="متن قسمتی از PDF")
    embedding: List[float] = Field(..., description="بردار embedding متن")

    class Config:
        json_schema_extra = {
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


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))  # اگر میخوای به کاربر مرتبطش کنی

    user = relationship("User", back_populates="chat_history")
