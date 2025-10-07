# D:\ArsaWebDeveloper\Project\Vexta\auth\schemas.py

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
   
    email: EmailStr
    password: str

class OTPVerify(BaseModel):
    email: str
    otp: str