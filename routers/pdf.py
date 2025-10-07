from fastapi import APIRouter, File, UploadFile, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import fitz  # PyMuPDF
import openai
import os
import numpy as np
from models import PDFChunk, PDFChunkCreate, PDFChunkResponse
from typing import List, Optional, Dict, Any
from database import get_db

router = APIRouter()

# مقدار کلید API اوپن‌ای‌آی از متغیر محیطی خوانده می‌شود
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# تابع تقسیم متن به بخش‌های کوچکتر (بر اساس تعداد کلمات)
def chunk_text(text: str, max_words: int = 500) -> List[str]:
    chunks = []
    words = text.split()
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# محاسبه شباهت کسینوسی دو بردار
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# آپلود فایل PDF و ذخیره embeddingها در دیتابیس
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(..., description="فایل PDF برای آپلود"),
    db: Session = Depends(get_db)
):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="فقط فایل PDF مجاز است")

        # خواندن محتویات فایل
        contents = await file.read()
        temp_path = f"temp_{file.filename}"
        
        # ذخیره موقت فایل
        with open(temp_path, "wb") as f:
            f.write(contents)

        # خواندن متن از فایل PDF
        doc = fitz.open(temp_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        os.remove(temp_path)

        # تقسیم متن به بخش‌های کوچکتر
        chunks = chunk_text(full_text)

        # حذف رکوردهای قبلی این فایل
        db.query(PDFChunk).filter(PDFChunk.filename == file.filename).delete()
        db.commit()

        # ذخیره هر بخش در دیتابیس
        for chunk in chunks:
            response = openai.Embedding.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
            embedding = response["data"][0]["embedding"]

            db_chunk = PDFChunk(
                filename=file.filename,
                chunk=chunk,
                embedding=embedding
            )
            db.add(db_chunk)

        db.commit()

        return {
            "filename": file.filename,
            "total_chunks": len(chunks)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# پرسش و پاسخ از روی متن PDF
@router.post("/ask")
async def ask_pdf(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="سوال نمی‌تواند خالی باشد")

        # ایجاد embedding برای سوال
        question_embedding = openai.Embedding.create(
            input=question,
            model="text-embedding-ada-002"
        )
        question_vector = question_embedding["data"][0]["embedding"]

        # یافتن chunks مشابه
        chunks = db.query(PDFChunk).all()
        if not chunks:
            raise HTTPException(status_code=404, detail="هیچ متنی برای جستجو وجود ندارد")

        # محاسبه شباهت و یافتن نزدیک‌ترین chunks
        similarities = []
        for chunk in chunks:
            similarity = cosine_similarity(question_vector, chunk.embedding)
            similarities.append((chunk, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [chunk.chunk for chunk, _ in similarities[:3]]  # 3 تا chunk نزدیک‌ترین

        # ایجاد پیام برای OpenAI
        prompt = f"""متن مرجع:
{'\n\n'.join(top_chunks)}

سوال:
{question}

لطفاً بر اساس متن مرجع، پاسخ مناسب را بدهید."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "شما یک ربات پشتیبانی هستید که بر اساس متن مرجع پاسخ می‌دهید."},
                {"role": "user", "content": prompt}
            ]
        )

        return {"answer": response["choices"][0]["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# تابع تقسیم متن به بخش‌های کوچکتر (بر اساس تعداد کلمات)
def chunk_text(text, max_words=500):
    chunks = []
    words = text.split()
    current_chunk = []

    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# محاسبه شباهت کسینوسی دو بردار
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

# آپلود فایل PDF و ذخیره embeddingها در دیتابیس
@router.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not file.filename.endswith(".pdf"):
            return {"error": "فقط فایل PDF مجاز است"}

        contents = await file.read()
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        doc = fitz.open(temp_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        os.remove(temp_path)

        chunks = chunk_text(full_text)

        # حذف رکوردهای قبلی این فایل
        db.query(PDFChunk).filter(PDFChunk.filename == file.filename).delete()
        db.commit()

        for chunk in chunks:
            response = openai.Embedding.create(
                input=chunk,
                model="text-embedding-ada-002"
            )
            embedding = response["data"][0]["embedding"]

            db_chunk = PDFChunk(
                filename=file.filename,
                chunk=chunk,
                embedding=embedding
            )
            db.add(db_chunk)

        db.commit()

        return {
            "filename": file.filename,
            "total_chunks": len(chunks)
        }

    except Exception as e:
        return {"error": str(e)}

# پرسش و پاسخ از روی متن PDF
@router.post("/ask-pdf")
async def ask_pdf(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        question = data.get("question")
        if not question:
            return {"error": "سوال نمی‌تواند خالی باشد"}

        # ایجاد embedding برای سوال
        question_embedding = openai.Embedding.create(
            input=question,
            model="text-embedding-ada-002"
        )
        question_vector = question_embedding["data"][0]["embedding"]

        # یافتن chunks مشابه
        chunks = db.query(PDFChunk).all()
        if not chunks:
            return {"error": "هیچ متنی برای جستجو وجود ندارد"}

        # محاسبه شباهت و یافتن نزدیک‌ترین chunks
        similarities = []
        for chunk in chunks:
            similarity = cosine_similarity(question_vector, chunk.embedding)
            similarities.append((chunk, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [chunk.chunk for chunk, _ in similarities[:3]]  # 3 تا chunk نزدیک‌ترین

        # ایجاد پیام برای OpenAI
        prompt = f"""متن مرجع:
{'\n\n'.join(top_chunks)}

سوال:
{question}

لطفاً بر اساس متن مرجع، پاسخ مناسب را بدهید."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "شما یک ربات پشتیبانی هستید که بر اساس متن مرجع پاسخ می‌دهید."},
                {"role": "user", "content": prompt}
            ]
        )

        return {"answer": response["choices"][0]["message"]["content"]}

    except Exception as e:
        return {"error": str(e)}
    user_question = data.get("question")
    filename = data.get("filename")

    if not user_question or not filename:
        return {"error": "سؤال یا نام فایل ارسال نشده"}

    question_embedding = openai.Embedding.create(
        input=user_question,
        model="text-embedding-ada-002"
    ).data[0].embedding

    chunks = db.query(PDFChunk).filter(PDFChunk.filename == filename).all()
    if not chunks:
        return {"error": "برای این فایل داده‌ای وجود ندارد."}

    similarities = []
    for item in chunks:
        sim = cosine_similarity(question_embedding, item.embedding)
        similarities.append((sim, item.chunk))

    similarities.sort(reverse=True)
    top_chunk = similarities[0][1] if similarities else "چیزی پیدا نشد"

    prompt = f"بر اساس این متن پاسخ بده:\n\n{top_chunk}\n\nسؤال: {user_question}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.choices[0].message["content"]}
