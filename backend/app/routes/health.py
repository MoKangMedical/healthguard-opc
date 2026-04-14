"""
健康监测路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.health_record import (
    HealthRecord, 
    BloodPressure, 
    BloodSugar, 
    HeartRate, 
    Weight,
    HealthRecordType
)
from app.models.patient import Patient
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role
from app.config import settings

router = APIRouter()

@router.get("/records/{patient_id}", summary="获取健康记录")
async def get_health_records(
    patient_id: int,
    record_type: Optional[HealthRecordType] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者健康记录"""
    # 检查权限
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此记录")
    
    # 查询记录
    query = db.query(HealthRecord).filter(
        HealthRecord.patient_id == patient_id,
        HealthRecord.record_date >= datetime.now() - timedelta(days=days)
    )
    
    if record_type:
        query = query.filter(HealthRecord.record_type == record_type)
    
    records = query.order_by(HealthRecord.record_date.desc()).all()
    
    result = []
    for record in records:
        data = {
            "id": record.id,
            "record_type": record.record_type.value,
            "record_date": record.record_date,
            "is_abnormal": record.is_abnormal,
            "notes": record.notes,
        }
        
        # 获取具体数据
        if record.blood_pressure:
            data["blood_pressure"] = {
                "systolic": record.blood_pressure.systolic,
                "diastolic": record.blood_pressure.diastolic,
                "pulse": record.blood_pressure.pulse,
            }
        if record.blood_sugar:
            data["blood_sugar"] = {
                "value": record.blood_sugar.value,
                "unit": record.blood_sugar.unit,
                "measurement_time": record.blood_sugar.measurement_time,
            }
        if record.heart_rate:
            data["heart_rate"] = {
                "bpm": record.heart_rate.bpm,
                "is_resting": record.heart_rate.is_resting,
            }
        if record.weight:
            data["weight"] = {
                "value": record.weight.value,
                "height": record.weight.height,
                "bmi": record.weight.bmi,
            }
        
        result.append(data)
    
    return {"records": result, "total": len(result)}

@router.post("/blood-pressure", summary="记录血压")
async def record_blood_pressure(
    patient_id: int,
    systolic: int,
    diastolic: int,
    pulse: Optional[int] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """记录血压数据"""
    # 检查权限
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权添加此记录")
    
    # 判断是否异常
    is_abnormal = systolic >= settings.BLOOD_PRESSURE_HIGH or diastolic >= settings.BLOOD_PRESSURE_LOW
    
    # 创建记录
    health_record = HealthRecord(
        patient_id=patient_id,
        record_type=HealthRecordType.BLOOD_PRESSURE,
        record_date=datetime.now(),
        is_abnormal=is_abnormal,
        notes=notes,
        source="manual"
    )
    db.add(health_record)
    db.flush()
    
    blood_pressure = BloodPressure(
        health_record_id=health_record.id,
        systolic=systolic,
        diastolic=diastolic,
        pulse=pulse
    )
    db.add(blood_pressure)
    db.commit()
    
    return {
        "message": "血压记录成功",
        "record_id": health_record.id,
        "is_abnormal": is_abnormal,
        "abnormal_reason": "血压偏高" if systolic >= settings.BLOOD_PRESSURE_HIGH else (f"舒张压偏低 < {settings.BLOOD_PRESSURE_LOW}" if diastolic < settings.BLOOD_PRESSURE_LOW else None)
    }

@router.post("/blood-sugar", summary="记录血糖")
async def record_blood_sugar(
    patient_id: int,
    value: float,
    measurement_time: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """记录血糖数据"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权添加此记录")
    
    is_abnormal = value >= settings.BLOOD_SUGAR_HIGH or value <= settings.BLOOD_SUGAR_LOW
    
    health_record = HealthRecord(
        patient_id=patient_id,
        record_type=HealthRecordType.BLOOD_SUGAR,
        record_date=datetime.now(),
        is_abnormal=is_abnormal,
        notes=notes,
        source="manual"
    )
    db.add(health_record)
    db.flush()
    
    blood_sugar = BloodSugar(
        health_record_id=health_record.id,
        value=value,
        unit="mmol/L",
        measurement_time=measurement_time
    )
    db.add(blood_sugar)
    db.commit()
    
    return {
        "message": "血糖记录成功",
        "record_id": health_record.id,
        "is_abnormal": is_abnormal,
        "abnormal_reason": "血糖偏高" if value >= settings.BLOOD_SUGAR_HIGH else ("血糖偏低" if value <= settings.BLOOD_SUGAR_LOW else None)
    }

@router.post("/heart-rate", summary="记录心率")
async def record_heart_rate(
    patient_id: int,
    bpm: int,
    is_resting: bool = True,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """记录心率数据"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权添加此记录")
    
    is_abnormal = bpm >= settings.HEART_RATE_HIGH or bpm <= settings.HEART_RATE_LOW
    
    health_record = HealthRecord(
        patient_id=patient_id,
        record_type=HealthRecordType.HEART_RATE,
        record_date=datetime.now(),
        is_abnormal=is_abnormal,
        notes=notes,
        source="manual"
    )
    db.add(health_record)
    db.flush()
    
    heart_rate = HeartRate(
        health_record_id=health_record.id,
        bpm=bpm,
        is_resting=is_resting
    )
    db.add(heart_rate)
    db.commit()
    
    return {
        "message": "心率记录成功",
        "record_id": health_record.id,
        "is_abnormal": is_abnormal
    }

@router.get("/statistics/{patient_id}", summary="获取健康统计")
async def get_health_statistics(
    patient_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取健康统计数据"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="患者不存在")
    
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此记录")
    
    from datetime import timedelta
    start_date = datetime.now() - timedelta(days=days)
    
    # 统计各类型记录数量
    records = db.query(HealthRecord).filter(
        HealthRecord.patient_id == patient_id,
        HealthRecord.record_date >= start_date
    ).all()
    
    stats = {
        "total_records": len(records),
        "abnormal_records": sum(1 for r in records if r.is_abnormal),
        "by_type": {},
        "blood_pressure_trend": [],
        "blood_sugar_trend": [],
    }
    
    for record in records:
        rtype = record.record_type.value
        stats["by_type"][rtype] = stats["by_type"].get(rtype, 0) + 1
        
        # 收集趋势数据
        if record.blood_pressure:
            stats["blood_pressure_trend"].append({
                "date": record.record_date.isoformat(),
                "systolic": record.blood_pressure.systolic,
                "diastolic": record.blood_pressure.diastolic,
            })
        if record.blood_sugar:
            stats["blood_sugar_trend"].append({
                "date": record.record_date.isoformat(),
                "value": record.blood_sugar.value,
            })
    
    return stats