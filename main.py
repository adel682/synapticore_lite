"""
تطبيق FastAPI بسيط لتوليد مخطط OpenAPI
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json

# إنشاء التطبيق
app = FastAPI(
    title="SynaptiCore Lite API",
    version="1.0.0",
    description="API Documentation for SynaptiCore Lite - النسخة المبسطة",
    contact={
        "name": "SynaptiCore Team",
        "email": "support@synapticore.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# النماذج
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class Message(BaseModel):
    message: str
    timestamp: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool = True

# المسارات
@app.get("/", response_model=Message, tags=["الرئيسية"])
async def root():
    """الصفحة الرئيسية للـ API"""
    return {"message": "مرحباً بك في SynaptiCore Lite API"}

@app.get("/health", response_model=HealthResponse, tags=["النظام"])
async def health_check():
    """فحص حالة الخدمة"""
    return {
        "status": "healthy",
        "service": "SynaptiCore Lite",
        "version": "1.0.0"
    }

@app.get("/users", response_model=List[User], tags=["المستخدمون"])
async def get_users():
    """جلب قائمة المستخدمين"""
    # بيانات تجريبية
    return [
        {"id": 1, "username": "user1", "email": "user1@example.com", "full_name": "مستخدم الأول", "is_active": True},
        {"id": 2, "username": "user2", "email": "user2@example.com", "full_name": "مستخدم الثاني", "is_active": True}
    ]

@app.get("/users/{user_id}", response_model=User, tags=["المستخدمون"])
async def get_user(user_id: int):
    """جلب مستخدم محدد"""
    if user_id == 1:
        return {"id": 1, "username": "user1", "email": "user1@example.com", "full_name": "مستخدم الأول", "is_active": True}
    elif user_id == 2:
        return {"id": 2, "username": "user2", "email": "user2@example.com", "full_name": "مستخدم الثاني", "is_active": True}
    else:
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

@app.post("/users", response_model=User, tags=["المستخدمون"])
async def create_user(user: UserBase):
    """إنشاء مستخدم جديد"""
    # محاكاة إنشاء مستخدم
    new_user = User(
        id=3,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True
    )
    return new_user

@app.get("/info", tags=["معلومات"])
async def get_api_info():
    """معلومات عن الـ API"""
    return {
        "name": "SynaptiCore Lite API",
        "version": "1.0.0",
        "description": "API للنسخة المبسطة من SynaptiCore",
        "features": [
            "إدارة المستخدمين",
            "فحص حالة النظام",
            "توثيق تلقائي للـ API"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
