"""
数据导出路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import io

from app.database import get_db
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.models.device import Device
from app.services.auth import get_current_user
from app.services.export_service import ExportService

router = APIRouter()

@router.get("/health-records/{patient_id}")
async def export_health_records(
    patient_id: int,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出健康记录"""
    
    # 权限检查
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出此数据")
    
    service = ExportService(db)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    result = service.export_health_records(patient_id, start_date, end_date, format)
    
    return StreamingResponse(
        io.BytesIO(result['content']),
        media_type=result['content_type'],
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )

@router.get("/medications/{patient_id}")
async def export_medications(
    patient_id: int,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出用药记录"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出此数据")
    
    service = ExportService(db)
    result = service.export_medications(patient_id, format)
    
    return StreamingResponse(
        io.BytesIO(result['content']),
        media_type=result['content_type'],
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )

@router.get("/appointments/{patient_id}")
async def export_appointments(
    patient_id: int,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出预约记录"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出此数据")
    
    service = ExportService(db)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    result = service.export_appointments(patient_id, start_date, end_date, format)
    
    return StreamingResponse(
        io.BytesIO(result['content']),
        media_type=result['content_type'],
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )

@router.get("/device-data/{device_id}")
async def export_device_data(
    device_id: int,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出设备数据"""
    
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or device.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="无权导出此数据")
    
    service = ExportService(db)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    result = service.export_device_data(device_id, start_date, end_date, format)
    
    return StreamingResponse(
        io.BytesIO(result['content']),
        media_type=result['content_type'],
        headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
    )

@router.get("/patient-summary/{patient_id}")
async def export_patient_summary(
    patient_id: int,
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出患者摘要"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导出此数据")
    
    service = ExportService(db)
    
    try:
        result = service.export_patient_summary(patient_id, format)
        
        return StreamingResponse(
            io.BytesIO(result['content']),
            media_type=result['content_type'],
            headers={"Content-Disposition": f"attachment; filename={result['filename']}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/formats")
async def get_export_formats():
    """获取支持的导出格式"""
    return {
        "formats": [
            {"value": "csv", "label": "CSV", "description": "逗号分隔值文件"},
            {"value": "json", "label": "JSON", "description": "JSON 格式"},
            {"value": "xlsx", "label": "Excel", "description": "Excel 电子表格"},
        ]
    }