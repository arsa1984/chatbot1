# services/rag.py
from openai import OpenAI
import os
import json
import ast
import numpy as np
from sqlalchemy.orm import Session
from models import PDFChunk

# کلاینت جدید OpenAI با SDK های >=1.0.0
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str) -> list:
    """
    گرفتن امبدینگ با مدل text-embedding-3-small
    """
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding

def store_chunks(chunks: list, document_name: str, db: Session, user_id: int):
    """
    ذخیره‌ی چانک‌های یک PDF در دیتابیس همراه با شناسه‌ی کاربر.
    """
    for chunk in chunks:
        embedding = get_embedding(chunk)
        chunk_record = PDFChunk(
            filename=document_name,
            chunk=chunk,
            embedding=embedding,   # ستون JSON یا متن؛ SQLAlchemy هندل می‌کند
            user_id=user_id
        )
        db.add(chunk_record)
    db.commit()

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    شباهت کسینوسی بین دو بردار
    """
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def _to_numpy_embedding(value) -> np.ndarray:
    """
    ورودی امبدینگ را (لیست/رشته) به numpy.ndarray (float) تبدیل می‌کند.
    """
    if value is None:
        return np.array([], dtype=float)
    if isinstance(value, (list, tuple)):
        return np.array(value, dtype=float)
    if isinstance(value, str):
        # اگر به صورت رشته ذخیره شده بود؛ اول تلاش JSON، بعد literal_eval برای سازگاری
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = ast.literal_eval(value)
        return np.array(parsed, dtype=float)
    # هر حالت دیگر:
    return np.array(value, dtype=float)

def search_similar_chunks(query: str, db: Session, filename: str, top_k: int = 3) -> list:
    """
    بر اساس امبدینگ پرسش، مشابه‌ترین چانک‌ها را از دیتابیس برمی‌گرداند.
    """
    query_embedding = get_embedding(query)
    query_embedding_np = np.array(query_embedding, dtype=float)

    chunks = db.query(PDFChunk).filter(PDFChunk.filename == filename).all()
    results = []

    for chunk in chunks:
        chunk_embedding_np = _to_numpy_embedding(chunk.embedding)
        if chunk_embedding_np.size == 0:
            continue
        score = cosine_similarity(query_embedding_np, chunk_embedding_np)
        results.append((score, chunk.chunk))

    results.sort(reverse=True, key=lambda x: x[0])
    return [text for _, text in results[:top_k]]

def delete_chunks_by_filename(filename: str, db: Session):
    db.query(PDFChunk).filter(PDFChunk.filename == filename).delete()
    db.commit()

def get_chunks_by_filename(filename: str, db: Session):
    return db.query(PDFChunk).filter(PDFChunk.filename == filename).all()

def answer_question(filename: str, query: str, db: Session) -> str:
    """
    پاسخ به سؤال با استفاده از تمام چانک‌های فایل (بدون رتبه‌بندی).
    """
    chunks = get_chunks_by_filename(filename, db)
    if not chunks:
        return "اطلاعاتی برای پاسخ وجود ندارد."

    context_chunks = [str(chunk.chunk) for chunk in chunks]
    context = "\n\n".join(context_chunks)

    prompt = f"""با استفاده از اطلاعات زیر به سوال پاسخ بده:

{context}

سوال: {query}
پاسخ:"""

    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    content = resp.choices[0].message.content
    if content is None:
        return "پاسخی از مدل دریافت نشد."
    return content.strip()

def generate_answer(query: str, context_chunks: list) -> str:
    """
    پاسخ به سؤال با استفاده از چانک‌های ورودی (رتبه‌بندی‌شده بیرون از این تابع).
    """
    context_chunks_str = [str(chunk) for chunk in context_chunks if chunk is not None]
    context = "\n\n".join(context_chunks_str)

    prompt = f"""با استفاده از اطلاعات زیر به سوال پاسخ بده:

{context}

سوال: {query}
پاسخ:"""

    print("📥 Prompt to OpenAI:", prompt[:500])

    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    print("📤 Raw response:", resp)

    content = resp.choices[0].message.content
    return content.strip() if content else "❗ پاسخ خالی دریافت شد."
