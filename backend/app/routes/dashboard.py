"""
仪表盘路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.patient import Patient, PatientStatus
from app.models.health_record import HealthRecord, HealthRecordType
from app.models.appointment import Appointment, AppointmentStatus
from app.models.medication import Medication, MedicationReminder, ReminderStatus
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role

router = APIRouter()

@router.get("/patient/{patient_id}", summary="患者仪表盘")
async def get_patient_dashboard(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """患者仪表盘数据"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此信息")
    
    now = datetime.now()
    today = now.date()
    
    # 最近的健康记录
    recent_records = db.query(HealthRecord).filter(
        HealthRecord.patient_id == patient_id
    ).order_by(HealthRecord.record_date.desc()).limit(5).all()
    
    # 今日待服药物
    today_medications = db.query(MedicationReminder).join(Medication).filter(
        Medication.patient_id == patient_id,
        Medication.is_active == True,
        MedicationReminder.scheduled_time >= datetime.combine(today, datetime.min.time()),
        MedicationReminder.scheduled_time < datetime.combine(today + timedelta(days=1), datetime.min.time()),
        MedicationReminder.status == ReminderStatus.PENDING
    ).order_by(MedicationReminder.scheduled_time).all()
    
    # 近期预约
    upcoming_appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date >= now,
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).order_by(Appointment.appointment_date.asc()).limit(3).all()
    
    # 异常记录数（近30天）
    abnormal_count = db.query(HealthRecord).filter(
        HealthRecord.patient_id == patient_id,
        HealthRecord.record_date >= now - timedelta(days=30),
        HealthRecord.is_abnormal == True
    ).count()
    
    return {
        "patient_info": {
            "name": patient.user.full_name if patient.user else None,
            "patient_no": patient.patient_no,
            "status": patient.status.value,
        },
        "recent_records": [
            {
                "type": r.record_type.value,
                "date": r.record_date,
                "is_abnormal": r.is_abnormal,
            }
            for r in recent_records
        ],
        "today_medications": [
            {
                "id": m.id,
                "medication_name": m.medication.medication_name,
                "dosage": m.medication.dosage,
                "scheduled_time": m.scheduled_time,
                "status": m.status.value,
            }
            for m in today_medications
        ],
        "upcoming_appointments": [
            {
                "id": a.id,
                "appointment_no": a.appointment_no,
                "appointment_date": a.appointment_date,
                "department": a.department,
                "doctor_name": a.doctor.full_name if a.doctor else None,
                "status": a.status.value,
            }
            for a in upcoming_appointments
        ],
        "statistics": {
            "abnormal_records_30d": abnormal_count,
            "active_medications": db.query(Medication).filter(
                Medication.patient_id == patient_id,
                Medication.is_active == True
            ).count(),
        }
    }

@router.get("/doctor", summary="医生仪表盘")
async def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE]))
):
    """医生仪表盘数据"""
    now = datetime.now()
    today = now.date()
    
    # 今日预约
    today_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == current_user.id,
        Appointment.appointment_date >= datetime.combine(today, datetime.min.time()),
        Appointment.appointment_date < datetime.combine(today + timedelta(days=1), datetime.min.time()),
        Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
    ).order_by(Appointment.appointment_date).all()
    
    # 我的患者数量
    my_patients = db.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == current_user.id
    ).distinct().count()
    
    # 异常患者（近7天有异常记录）
    abnormal_patients = db.query(Patient).join(HealthRecord).filter(
        HealthRecord.record_date >= now - timedelta(days=7),
        HealthRecord.is_abnormal == True
    ).distinct().count()
    
    return {
        "doctor_info": {
            "name": current_user.full_name,
            "role": current_user.role.value,
        },
        "today_appointments": [
            {
                "id": a.id,
                "appointment_no": a.appointment_no,
                "time": a.appointment_date.strftime("%H:%M"),
                "patient_name": a.patient.user.full_name if a.patient and a.patient.user else None,
                "type": a.appointment_type,
                "status": a.status.value,
            }
            for a in today_appointments
        ],
        "statistics": {
            "today_appointments_count": len(today_appointments),
            "my_patients_count": my_patients,
            "abnormal_patients_count": abnormal_patients,
        }
    }

@router.get("/admin", summary="管理员仪表盘")
async def get_admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """管理员仪表盘数据"""
    now = datetime.now()
    today = now.date()
    
    # 总体统计
    total_patients = db.query(Patient).count()
    active_patients = db.query(Patient).filter(Patient.status == PatientStatus.ACTIVE).count()
    total_doctors = db.query(User).filter(User.role == UserRole.DOCTOR).count()
    
    # 今日预约统计
    today_appointments = db.query(Appointment).filter(
        Appointment.appointment_date >= datetime.combine(today, datetime.min.time()),
        Appointment.appointment_date < datetime.combine(today + timedelta(days=1), datetime.min.time())
    ).count()
    
    # 本月健康记录
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_records = db.query(HealthRecord).filter(
        HealthRecord.record_date >= month_start
    ).count()
    
    # 异常率
    total_records = db.query(HealthRecord).filter(
        HealthRecord.record_date >= month_start
    ).count()
    abnormal_records = db.query(HealthRecord).filter(
        HealthRecord.record_date >= month_start,
        HealthRecord.is_abnormal == True
    ).count()
    abnormal_rate = (abnormal_records / total_records * 100) if total_records > 0 else 0
    
    return {
        "statistics": {
            "total_patients": total_patients,
            "active_patients": active_patients,
            "total_doctors": total_doctors,
            "today_appointments": today_appointments,
            "month_records": month_records,
            "abnormal_rate": round(abnormal_rate, 2),
        },
        "recent_alerts": []  # 可以添加异常预警
    }