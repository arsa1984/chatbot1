# D:\ArsaWebDeveloper\Project\Vexta\auth\routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from . import models, schemas, hashing
from .jwt_handler import create_access_token
from fastapi import APIRouter
from .deps import get_current_user
from fastapi import Depends
from .utils import generate_otp
from utils.email_utils import send_email
from .schemas import OTPVerify




router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/me")
def read_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name
    }
@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")

    if not hashing.Hash.verify(db_user.hashed_password, user.password):
        raise HTTPException(status_code=401, detail="رمز عبور اشتباه است")

    # 🛑 اضافه کردن این بخش
    if not db_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="ایمیل شما تایید نشده. لطفاً کد OTP را وارد کنید."
        )

    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}




@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # آیا ایمیل از قبل ثبت شده؟
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="ایمیل قبلاً ثبت شده")

    # تولید کد OTP
    otp = generate_otp()

    # ساخت کاربر جدید
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashing.Hash.bcrypt(user.password),
        otp_code=otp,
        is_verified=False
        # 👈 هیچ otp_expiry تعریف نمی‌کنیم
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 📧 ارسال ایمیل واقعی (بدون محدودیت زمانی)
    send_email(
        to_email=user.email,
        subject="کد تایید حساب شما",
        body=f"سلام {user.name},\n\nکد تایید شما: {otp}\n\nاین کد بدون محدودیت زمانی معتبر است."
    )

    return {"message": "ثبت‌نام موفق. لطفاً ایمیل خود را بررسی کنید."}



@router.post("/verify-otp")
def verify_otp(data: OTPVerify, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر پیدا نشد")

    if user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="کد وارد شده نادرست است")

    user.is_verified = True
    user.otp_code = None
    db.commit()

    return {"message": "ایمیل شما تایید شد. حالا می‌توانید وارد شوید."}