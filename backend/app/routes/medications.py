"""
用药管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.medication import Medication, MedicationReminder, ReminderStatus
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role

router = APIRouter()

@router.get("/patient/{patient_id}", summary="获取患者用药列表")
async def get_patient_medications(
    patient_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者用药列表"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此信息")
    
    query = db.query(Medication).filter(Medication.patient_id == patient_id)
    if active_only:
        query = query.filter(Medication.is_active == True)
    
    medications = query.order_by(Medication.created_at.desc()).all()
    
    return {
        "medications": [
            {
                "id": m.id,
                "medication_name": m.medication_name,
                "generic_name": m.generic_name,
                "dosage": m.dosage,
                "frequency": m.frequency,
                "route": m.route,
                "start_date": m.start_date,
                "end_date": m.end_date,
                "remaining": m.remaining,
                "is_active": m.is_active,
                "instructions": m.instructions,
            }
            for m in medications
        ]
    }

@router.post("/", summary="添加用药记录")
async def add_medication(
    patient_id: int,
    medication_name: str,
    dosage: str,
    frequency: str,
    route: str = "口服",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    instructions: Optional[str] = None,
    quantity: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """添加用药记录"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    medication = Medication(
        patient_id=patient_id,
        medication_name=medication_name,
        dosage=dosage,
        frequency=frequency,
        route=route,
        instructions=instructions,
        quantity=quantity,
        remaining=quantity,
        prescribed_by=current_user.id,
        prescription_date=datetime.now(),
        is_active=True
    )
    
    if start_date:
        medication.start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        medication.end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    db.add(medication)
    db.commit()
    db.refresh(medication)
    
    # 创建默认提醒（根据频率）
    create_default_reminders(db, medication)
    
    return {
        "message": "用药记录添加成功",
        "medication_id": medication.id
    }

def create_default_reminders(db: Session, medication: Medication):
    """创建默认用药提醒"""
    # 解析频率
    freq_map = {
        "每日1次": [9],
        "每日2次": [9, 21],
        "每日3次": [8, 14, 20],
        "每日4次": [8, 12, 16, 20],
    }
    
    hours = freq_map.get(medication.frequency, [9])
    
    # 创建未来7天的提醒
    start = medication.start_date or datetime.now()
    for day in range(7):
        for hour in hours:
            reminder_time = (start + timedelta(days=day)).replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            
            if medication.end_date and reminder_time > medication.end_date:
                continue
            
            reminder = MedicationReminder(
                medication_id=medication.id,
                reminder_time=reminder_time,
                scheduled_time=reminder_time,
                status=ReminderStatus.PENDING
            )
            db.add(reminder)
    
    db.commit()

@router.get("/reminders/{patient_id}", summary="获取用药提醒")
async def get_medication_reminders(
    patient_id: int,
    days: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用药提醒"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此信息")
    
    # 获取患者的所有活跃药物
    medications = db.query(Medication).filter(
        Medication.patient_id == patient_id,
        Medication.is_active == True
    ).all()
    
    medication_ids = [m.id for m in medications]
    
    # 获取提醒
    start_time = datetime.now()
    end_time = start_time + timedelta(days=days)
    
    reminders = db.query(MedicationReminder).filter(
        MedicationReminder.medication_id.in_(medication_ids),
        MedicationReminder.reminder_time >= start_time,
        MedicationReminder.reminder_time <= end_time,
        MedicationReminder.status == ReminderStatus.PENDING
    ).order_by(MedicationReminder.reminder_time).all()
    
    return {
        "reminders": [
            {
                "id": r.id,
                "medication_name": r.medication.medication_name,
                "dosage": r.medication.dosage,
                "scheduled_time": r.scheduled_time,
                "status": r.status.value,
            }
            for r in reminders
        ]
    }

@router.put("/reminder/{reminder_id}/acknowledge", summary="确认用药")
async def acknowledge_medication(
    reminder_id: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """确认用药（标记已服药）"""
    reminder = db.query(MedicationReminder).filter(MedicationReminder.id == reminder_id).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    reminder.status = ReminderStatus.ACKNOWLEDGED
    reminder.acknowledged_at = datetime.now()
    if notes:
        reminder.notes = notes
    
    # 更新药物剩余量
    medication = reminder.medication
    if medication.remaining and medication.remaining > 0:
        medication.remaining -= 1
    
    db.commit()
    
    return {"message": "用药已确认"}

@router.put("/{medication_id}/deactivate", summary="停用药物")
async def deactivate_medication(
    medication_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """停用药物"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    
    if not medication:
        raise HTTPException(status_code=404, detail="药物记录不存在")
    
    medication.is_active = False
    medication.end_date = datetime.now()
    
    if reason:
        medication.instructions = f"{medication.instructions}\n停用原因: {reason}" if medication.instructions else f"停用原因: {reason}"
    
    db.commit()
    
    return {"message": "药物已停用"}