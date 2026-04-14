"""
患者管理路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.patient import Patient, PatientStatus
from app.models.user import User, UserRole
from app.services.auth import get_current_user, require_role

router = APIRouter()

@router.get("/", summary="获取患者列表")
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[PatientStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者列表"""
    query = db.query(Patient)
    
    # 根据角色过滤
    if current_user.role == UserRole.PATIENT:
        query = query.filter(Patient.user_id == current_user.id)
    
    # 按状态过滤
    if status:
        query = query.filter(Patient.status == status)
    
    total = query.count()
    patients = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "patients": [
            {
                "id": p.id,
                "patient_no": p.patient_no,
                "full_name": p.user.full_name if p.user else None,
                "gender": p.gender,
                "age": p.age,
                "status": p.status.value,
                "has_diabetes": p.has_diabetes,
                "has_hypertension": p.has_hypertension,
            }
            for p in patients
        ]
    }

@router.get("/{patient_id}", summary="获取患者详情")
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取患者详情"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="患者不存在"
        )
    
    # 权限检查
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此患者信息"
        )
    
    return {
        "id": patient.id,
        "patient_no": patient.patient_no,
        "user": {
            "id": patient.user.id,
            "full_name": patient.user.full_name,
            "email": patient.user.email,
            "phone": patient.user.phone,
        },
        "gender": patient.gender,
        "date_of_birth": patient.date_of_birth,
        "age": patient.age,
        "blood_type": patient.blood_type,
        "allergies": patient.allergies,
        "medical_history": patient.medical_history,
        "has_diabetes": patient.has_diabetes,
        "has_hypertension": patient.has_hypertension,
        "has_heart_disease": patient.has_heart_disease,
        "status": patient.status.value,
        "created_at": patient.created_at,
    }

@router.post("/", summary="创建患者档案")
async def create_patient(
    user_id: int,
    patient_no: str,
    gender: str,
    date_of_birth: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """创建患者档案"""
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查是否已有档案
    existing = db.query(Patient).filter(Patient.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户已有患者档案"
        )
    
    # 创建患者
    from datetime import datetime
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    today = datetime.now().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    patient = Patient(
        user_id=user_id,
        patient_no=patient_no,
        gender=gender,
        date_of_birth=dob,
        age=age,
        status=PatientStatus.ACTIVE
    )
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    return {
        "message": "患者档案创建成功",
        "patient_id": patient.id,
        "patient_no": patient.patient_no
    }

@router.put("/{patient_id}", summary="更新患者信息")
async def update_patient(
    patient_id: int,
    allergies: Optional[str] = None,
    medical_history: Optional[str] = None,
    has_diabetes: Optional[bool] = None,
    has_hypertension: Optional[bool] = None,
    has_heart_disease: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.DOCTOR, UserRole.NURSE, UserRole.ADMIN]))
):
    """更新患者信息"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="患者不存在"
        )
    
    # 更新字段
    if allergies is not None:
        patient.allergies = allergies
    if medical_history is not None:
        patient.medical_history = medical_history
    if has_diabetes is not None:
        patient.has_diabetes = has_diabetes
    if has_hypertension is not None:
        patient.has_hypertension = has_hypertension
    if has_heart_disease is not None:
        patient.has_heart_disease = has_heart_disease
    
    db.commit()
    db.refresh(patient)
    
    return {"message": "患者信息更新成功"}