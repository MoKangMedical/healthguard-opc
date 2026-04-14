"""
报表路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services.auth import get_current_user
from app.services.report_service import ReportService

router = APIRouter()

@router.get("/patient/{patient_id}", summary="生成健康报告")
async def generate_report(
    patient_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成健康报告"""
    
    # 权限检查
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此报告")
    
    # 解析日期
    if start_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        start = datetime.now() - timedelta(days=30)
    
    if end_date:
        end = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end = datetime.now()
    
    service = ReportService(db)
    
    try:
        report = service.generate_health_report(patient_id, start, end)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/patient/{patient_id}/weekly", summary="生成周报")
async def generate_weekly_report(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成周报"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此报告")
    
    service = ReportService(db)
    report = service.generate_weekly_report(patient_id)
    return report

@router.get("/patient/{patient_id}/monthly", summary="生成月报")
async def generate_monthly_report(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成月报"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此报告")
    
    service = ReportService(db)
    report = service.generate_monthly_report(patient_id)
    return report

@router.get("/patient/{patient_id}/summary", summary="获取健康摘要")
async def get_health_summary(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取健康摘要（用于仪表盘）"""
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此信息")
    
    service = ReportService(db)
    report = service.generate_weekly_report(patient_id)
    
    return {
        "patient_id": patient_id,
        "summary": report.get("summary", {}),
        "blood_pressure": {
            "status": report.get("blood_pressure", {}).get("status"),
            "average": report.get("blood_pressure", {}).get("average")
        },
        "blood_sugar": {
            "status": report.get("blood_sugar", {}).get("status"),
            "average": report.get("blood_sugar", {}).get("average")
        },
        "medication_adherence": report.get("medications", {}).get("adherence", {}).get("adherence_rate"),
        "recommendations": report.get("recommendations", [])[:3]
    }