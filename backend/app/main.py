"""
HealthGuard OPC - 门诊人群健康管理平台
Main Application Entry Point
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List
import uvicorn

from app.config import settings
from app.database import engine, Base, get_db
from app.models import user, patient, health_record, appointment, medication, device, notification
from app.routes import auth, patients, health, appointments, medications, dashboard, devices, notifications, reports
from app.services.auth import create_access_token, get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    print("🚀 HealthGuard OPC 服务启动成功")
    print(f"📊 数据库连接: {settings.DATABASE_URL}")
    print(f"🔗 API 文档: http://localhost:8000/docs")
    yield
    # 关闭时清理资源
    print("👋 HealthGuard OPC 服务关闭")

app = FastAPI(
    title="HealthGuard OPC API",
    description="门诊人群健康管理平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(patients.router, prefix="/api/patients", tags=["患者管理"])
app.include_router(health.router, prefix="/api/health", tags=["健康监测"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["预约管理"])
app.include_router(medications.router, prefix="/api/medications", tags=["用药管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["仪表盘"])
app.include_router(devices.router, prefix="/api/devices", tags=["设备管理"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["通知管理"])
app.include_router(reports.router, prefix="/api/reports", tags=["健康报告"])

@app.get("/", tags=["根路径"])
async def root():
    """API 根路径"""
    return {
        "message": "Welcome to HealthGuard OPC API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "HealthGuard OPC API"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )