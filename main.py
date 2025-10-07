from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import openai
from typing import Dict, Any

from models import Message
from database import get_db
from routers import pdf

# بارگذاری .env
load_dotenv()

# راه‌اندازی FastAPI
app = FastAPI()

# بارگذاری مسیرها
app.include_router(pdf.router)

# استاتیک و قالب‌ها
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# کلید API و مدل
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in .env file")
openai.api_key = OPENAI_API_KEY
OPENAI_MODEL = "gpt-3.5-turbo"


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        message = data.get("message")

        if not message:
            return JSONResponse(status_code=400, content={"error": "پیامی ارسال نشده است."})

        # تماس با OpenAI
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "شما یک ربات پشتیبانی هستید."},
                {"role": "user", "content": message}
            ]
        )
        reply = response["choices"][0]["message"]["content"]

        # ذخیره پیام در دیتابیس
        db_message = Message(user_message=message, bot_reply=reply)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        return {"reply": reply}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/health")
async def health_check():
    """چک کردن وضعیت سرور"""
    return {"status": "healthy"}


@app.post("/api/messages/")
async def create_message(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        message = data.get("message")

        if not message:
            return JSONResponse(status_code=400, content={"error": "پیام نمی‌تواند خالی باشد."})

        db_message = Message(user_message=message)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)

        return JSONResponse(status_code=201, content={"id": db_message.id})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/messages/{message_id}")
async def get_message(message_id: int, db: Session = Depends(get_db)):
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return JSONResponse(status_code=404, content={"error": "پیام یافت نشد."})

        return {"id": message.id, "message": message.user_message, "reply": message.bot_reply}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/messages/")
def get_messages(db: Session = Depends(get_db)):
    messages = db.query(Message).all()
    return {
        "messages": [
            {"id": m.id, "user_message": m.user_message, "bot_reply": m.bot_reply}
            for m in messages
        ]
    }



















