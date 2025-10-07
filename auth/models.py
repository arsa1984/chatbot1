from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from sqlalchemy import String, Integer, Boolean , DateTime, Column,ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # 👇 فیلدهای مربوط به تایید ایمیل
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    otp_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

    # روابط
    messages = relationship("Message", back_populates="user")
    pdf_chunks = relationship("PDFChunk", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user")
