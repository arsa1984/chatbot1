
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import Query
from typing import Dict, Any
from models import Message
from database import get_db , engine
from routers import pdf
from routers import chat
from openai import OpenAI
from fastapi.openapi.utils import get_openapi

from auth import models
from auth.routes import router as auth_router


models.Base.metadata.create_all(bind=engine)
# بارگذاری .env
load_dotenv()

# راه‌اندازی FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"]
)


app.include_router(pdf.router, prefix="/api/pdf")
# بارگذاری مسیرها
app.include_router(chat.router, prefix="/api/chat")

app.include_router(auth_router)





app.mount("/static", StaticFiles(directory="static"), name="static")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/api/chat_message")
async def chat_bot(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        message = data.get("message")

        if not message:
            return JSONResponse(status_code=400, content={"error": "پیامی ارسال نشده است."})

        # تماس با OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "شما یک ربات پشتیبانی هستید."},
                {"role": "user", "content": message}
            ]
        )
        reply = response.choices[0].message.content

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




@app.get("/chat-history")
def get_chat_history(filename: str = Query(...), db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.filename == filename).order_by(Message.created_at).all()
    return [
        {
            "user": m.user_message,
            "bot": m.bot_reply,
            "timestamp": m.created_at.isoformat()
        } for m in messages
    ]




def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Vexta API",
        version="1.0.0",
        description="API for authentication and PDF tools",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi









