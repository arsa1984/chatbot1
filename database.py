# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker
# import os
# from dotenv import load_dotenv
# from pathlib import Path


# # بارگذاری متغیرهای محیطی
# load_dotenv()



# print("✅ DB_USER:", os.getenv("DB_USER"))
# print("✅ DB_PASSWORD:", os.getenv("DB_PASSWORD"))
# print("✅ DB_NAME:", os.getenv("DB_NAME"))

# env_path = Path(__file__).parent / ".env"
# load_dotenv(dotenv_path=env_path)

# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
# DB_PORT = os.getenv("DB_PORT", "5432")
# DB_NAME = os.getenv("DB_NAME")

# env_path = Path(__file__).parent / ".env"
# print("📄 env path:", env_path)

# load_dotenv(dotenv_path=env_path)

# if not all([DB_USER, DB_PASSWORD, DB_NAME]):
#     raise RuntimeError("مقادیر DB_USER، DB_PASSWORD و DB_NAME در .env موجود نیستند.")

# DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# try:
#     engine = create_engine(DATABASE_URL)
# except Exception as e:
#     raise RuntimeError(f"Database connection failed: {e}")

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def create_tables():
#     from models import Message, PDFChunk
#     Base.metadata.create_all(bind=engine)

# if __name__ == "__main__":
#     create_tables()



from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path
import urllib.parse

# مسیر فایل .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# دریافت متغیرهای محیطی
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

# encode کردن رمز عبور اگر کاراکترهای خاص دارد
DB_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD)

print("✅ DB_USER:", DB_USER)
print("✅ DB_PASSWORD:", DB_PASSWORD)
print("✅ DB_NAME:", DB_NAME)
print("✅ DB_HOST:", DB_HOST)
print("✅ DB_PORT:", DB_PORT)

# بررسی اینکه متغیرها مقدار دارند
if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    raise RuntimeError("مقادیر DB_USER، DB_PASSWORD و DB_NAME در .env موجود نیستند.")

# ساخت URL اتصال به دیتابیس
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ساخت engine
engine = create_engine(DATABASE_URL)

# ساخت sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# پایه‌ی مدل‌ها
Base = declarative_base()

# تابع برای دریافت session دیتابیس
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# اگر خواستی تو این فایل جدول‌ها رو بسازی
def create_tables():
    from models import Message, PDFChunk  # مدل‌ها رو ایمپورت کن
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

# برای اجرای مستقیم این فایل از خط فرمان
if __name__ == "__main__":
    create_tables()
