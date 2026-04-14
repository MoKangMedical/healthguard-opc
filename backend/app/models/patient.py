"""
患者模型
"""

from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class PatientStatus(str, enum.Enum):
    """患者状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FOLLOW_UP = "follow_up"
    DISCHARGED = "discharged"

class Patient(Base):
    """患者信息表"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # 基本信息
    patient_no = Column(String(50), unique=True, index=True)  # 病历号
    id_card = Column(String(18), unique=True)  # 身份证号
    gender = Column(String(10))  # 性别
    date_of_birth = Column(Date)  # 出生日期
    age = Column(Integer)  # 年龄
    
    # 联系信息
    address = Column(String(500))  # 地址
    emergency_contact = Column(String(100))  # 紧急联系人
    emergency_phone = Column(String(20))  # 紧急联系电话
    
    # 医疗信息
    blood_type = Column(String(10))  # 血型
    allergies = Column(Text)  # 过敏史
    medical_history = Column(Text)  # 病史
    family_history = Column(Text)  # 家族史
    
    # 慢性病标记
    has_diabetes = Column(Boolean, default=False)
    has_hypertension = Column(Boolean, default=False)
    has_heart_disease = Column(Boolean, default=False)
    
    # 状态
    status = Column(Enum(PatientStatus), default=PatientStatus.ACTIVE)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    user = relationship("User", back_populates="patient_profile")
    health_records = relationship("HealthRecord", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")
    medications = relationship("Medication", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_no='{self.patient_no}')>"