# Chat Application

این یک اپلیکیشن چت است که از FastAPI و OpenAI برای پاسخگویی به کاربران استفاده می‌کند.

## نیازمندی‌ها

- Python 3.8 یا بالاتر
- PostgreSQL
- Docker (اختیاری برای راه‌اندازی ساده‌تر)

## نصب و راه‌اندازی

1. ابتدا virtual environment را ایجاد کنید:
```bash
python -m venv .venv
.\.venv\Scripts\activate  # برای Windows
```

2. نصب dependencies:
```bash
pip install -r requirements.txt
```

3. تنظیمات محیطی:
- فایل `.env` را با این محتوا ایجاد کنید:
```
OPENAI_API_KEY=your_openai_api_key
DB_USER=arsa
DB_PASSWORD=arsakalhor
DB_HOST=db
DB_PORT=5432
DB_NAME=mydb_utf8
```

4. جداول را ایجاد کنید:
```bash
python database.py
```

5. اپلیکیشن را راه‌اندازی کنید:
```bash
uvicorn main:app --reload
```

## استفاده

1. اپلیکیشن در `http://localhost:8000` در دسترس خواهد بود
2. از FastAPI docs در `http://localhost:8000/docs` می‌توانید API endpoints را تست کنید
3. از صفحه اصلی در `http://localhost:8000` می‌توانید با چت ربات صحبت کنید

## ساختار پروژه

- `main.py`: نکات اصلی FastAPI
- `database.py`: تنظیمات دیتابیس
- `models.py`: مدل‌های SQLAlchemy
- `routers/`: روترهای API
- `templates/`: فایل‌های HTML
- `static/`: فایل‌های استاتیک (CSS, JS, و غیره)
