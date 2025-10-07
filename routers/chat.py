
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from services.rag import answer_question  # فرض می‌کنیم این فانکشن جواب میده
from database import get_db
from fastapi import Request

router = APIRouter()

class AskRequest(BaseModel):
    filename: str
    question: str

@router.post("/ask", response_model=dict, tags=["chat"], description="Ask a question about a PDF file")
async def ask_question(data: AskRequest, db: Session = Depends(get_db)):
    print("✅ POST /ask دریافت شد!", data)
    try:
        answer = answer_question(data.filename, data.question, db)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ask")
async def ask_get_debug():
    raise HTTPException(status_code=405, detail="Method Not Allowed: Use POST")



