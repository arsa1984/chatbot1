# utils/pdf_utils.py
import fitz  # PyMuPDF
from typing import List

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()  # type: ignore
    return text

def chunk_text(text: str, max_tokens: int = 500) -> List[str]:
    import tiktoken  # برای شمارش توکن‌ها بر اساس مدل OpenAI

    tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
    words = text.split()
    chunks = []
    current_chunk = []

    token_count = 0
    for word in words:
        tokens = len(tokenizer.encode(word))
        if token_count + tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            token_count = tokens
        else:
            current_chunk.append(word)
            token_count += tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks
