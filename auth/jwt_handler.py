from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "VEXTA_SECRET_KEY"  # می‌تونه یه رشته تصادفی باشه
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600 # توکن ۱ ساعت اعتبار داره

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt













