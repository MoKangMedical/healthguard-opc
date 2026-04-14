"""
API 健康检查和系统信息
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import psutil
import os

from app.database import get_db, engine
from app.config import settings

router = APIRouter()

@router.get("/health", summary="健康检查")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "HealthGuard OPC API",
        "version": settings.VERSION
    }

@router.get("/health/detailed", summary="详细健康检查")
async def detailed_health_check(db: Session = Depends(get_db)):
    """详细的系统健康检查"""
    
    checks = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "disk": "unknown",
        "memory": "unknown"
    }
    
    # 数据库检查
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # 磁盘检查
    try:
        disk = psutil.disk_usage('/')
        checks["disk"] = {
            "status": "healthy" if disk.percent < 90 else "warning",
            "used_percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2)
        }
    except:
        checks["disk"] = "unavailable"
    
    # 内存检查
    try:
        memory = psutil.virtual_memory()
        checks["memory"] = {
            "status": "healthy" if memory.percent < 90 else "warning",
            "used_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2)
        }
    except:
        checks["memory"] = "unavailable"
    
    # 整体状态
    overall_status = "healthy"
    for key, value in checks.items():
        if isinstance(value, str) and "unhealthy" in value:
            overall_status = "unhealthy"
            break
        elif isinstance(value, dict) and value.get("status") == "warning":
            overall_status = "warning"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks": checks
    }

@router.get("/info", summary="系统信息")
async def system_info():
    """获取系统信息"""
    
    return {
        "service": "HealthGuard OPC",
        "version": settings.VERSION,
        "environment": "development" if settings.DEBUG else "production",
        "python_version": os.sys.version,
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@router.get("/stats", summary="系统统计")
async def system_stats(db: Session = Depends(get_db)):
    """获取系统统计信息"""
    
    from app.models.user import User
    from app.models.patient import Patient
    from app.models.device import Device, DeviceStatus
    from app.models.notification import Notification
    
    # 用户统计
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # 患者统计
    total_patients = db.query(Patient).count()
    
    # 设备统计
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == DeviceStatus.ONLINE).count()
    
    # 通知统计
    total_notifications = db.query(Notification).count()
    unread_notifications = db.query(Notification).filter(Notification.is_read == False).count()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "users": {
            "total": total_users,
            "active": active_users
        },
        "patients": {
            "total": total_patients
        },
        "devices": {
            "total": total_devices,
            "online": online_devices,
            "offline": total_devices - online_devices
        },
        "notifications": {
            "total": total_notifications,
            "unread": unread_notifications
        }
    }