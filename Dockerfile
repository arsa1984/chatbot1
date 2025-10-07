# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

# نصب ابزارهای ضروری برای build پکیج‌ها (مثل psycopg2, tiktoken, ...)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    rustc \
    cargo \
 && rm -rf /var/lib/apt/lists/*

# فقط فایل requirements رو کپی کن
COPY requirements.txt .

# نصب dependency ها در یک لایه جدا
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Runtime ---
FROM python:3.11-slim

WORKDIR /app

# فقط پکیج‌های نصب‌شده رو از استیج قبلی بیار
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# کپی سورس پروژه
COPY . .

EXPOSE 8000

# اجرای Uvicorn بدون reload (production)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
