"""
预约管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.appointment import Appointment, AppointmentStatus
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", summary="获取预约列表")
async def get_appointments(
    status: Optional[AppointmentStatus] = None,
    days: int = Query(7, ge=1, le=90),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预约列表"""
    query = db.query(Appointment)
    
    # 根据角色过滤
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if patient:
            query = query.filter(Appointment.patient_id == patient.id)
        else:
            return {"appointments": [], "total": 0}
    elif current_user.role == UserRole.DOCTOR:
        query = query.filter(Appointment.doctor_id == current_user.id)
    
    # 按状态过滤
    if status:
        query = query.filter(Appointment.status == status)
    
    # 按日期过滤
    start_date = datetime.now()
    end_date = start_date + timedelta(days=days)
    query = query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    )
    
    total = query.count()
    appointments = query.order_by(Appointment.appointment_date.asc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "appointments": [
            {
                "id": a.id,
                "appointment_no": a.appointment_no,
                "appointment_date": a.appointment_date,
                "department": a.department,
                "appointment_type": a.appointment_type,
                "status": a.status.value,
                "patient_name": a.patient.user.full_name if a.patient and a.patient.user else None,
                "doctor_name": a.doctor.full_name if a.doctor else None,
                "reason": a.reason,
            }
            for a in appointments
        ]
    }

@router.post("/", summary="创建预约")
async def create_appointment(
    patient_id: int,
    doctor_id: int,
    appointment_date: str,
    department: str,
    appointment_type: str,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建预约"""
    # 检查患者是否存在
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    # 检查医生是否存在
    doctor = db.query(User).filter(User.id == doctor_id, User.role == UserRole.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="医生不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权创建此预约")
    
    # 生成预约号
    import random
    appointment_no = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
    
    # 解析日期
    appt_date = datetime.strptime(appointment_date, "%Y-%m-%d %H:%M")
    
    # 检查时间冲突
    existing = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appt_date,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该时间段已被预约")
    
    # 创建预约
    appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_no=appointment_no,
        appointment_date=appt_date,
        department=department,
        appointment_type=appointment_type,
        reason=reason,
        status=AppointmentStatus.PENDING
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return {
        "message": "预约创建成功",
        "appointment_id": appointment.id,
        "appointment_no": appointment.appointment_no,
        "appointment_date": appointment.appointment_date
    }

@router.put("/{appointment_id}/status", summary="更新预约状态")
async def update_appointment_status(
    appointment_id: int,
    new_status: AppointmentStatus,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """更新预约状态"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    appointment.status = new_status
    if notes:
        appointment.notes = notes
    
    db.commit()
    db.refresh(appointment)
    
    return {
        "message": "预约状态更新成功",
        "appointment_id": appointment.id,
        "new_status": new_status.value
    }

@router.delete("/{appointment_id}", summary="取消预约")
async def cancel_appointment(
    appointment_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """取消预约"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="预约不存在")
    
    # 权限检查
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or appointment.patient_id != patient.id:
            raise HTTPException(status_code=403, detail="无权取消此预约")
    
    appointment.status = AppointmentStatus.CANCELLED
    if reason:
        appointment.notes = f"取消原因: {reason}"
    
    db.commit()
    
    return {"message": "预约已取消"}

@router.get("/available-slots", summary="获取可预约时段")
async def get_available_slots(
    doctor_id: int,
    date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取可预约时段"""
    # 检查医生是否存在
    doctor = db.query(User).filter(User.id == doctor_id, User.role == UserRole.DOCTOR).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="医生不存在")
    
    # 解析日期
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    
    # 工作时间：9:00-17:00，每30分钟一个时段
    slots = []
    current_time = datetime.combine(target_date, datetime.min.time().replace(hour=9))
    end_time = datetime.combine(target_date, datetime.min.time().replace(hour=17))
    
    while current_time < end_time:
        # 检查该时段是否已被预约
        existing = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == current_time,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).first()
        
        if not existing:
            slots.append({
                "time": current_time.strftime("%H:%M"),
                "datetime": current_time.isoformat()
            })
        
        current_time += timedelta(minutes=30)
    
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.full_name,
        "date": date,
        "available_slots": slots
    }