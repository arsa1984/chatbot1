from dotenv import load_dotenv
import os
import psycopg2
from urllib.parse import quote_plus
from pathlib import Path

# بارگذاری متغیرهای محیطی
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# دریافت و encode کردن رمز عبور
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=DB_PASSWORD,
        host="127.0.0.1",
        port="5432"
    )
    print("✅ Connected to database successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
