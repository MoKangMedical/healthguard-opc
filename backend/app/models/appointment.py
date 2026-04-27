"""
预约管理模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class AppointmentStatus(str, enum.Enum):
    """预约状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class Appointment(Base):
    """预约表"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 关联
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 预约信息
    appointment_no = Column(String(50), unique=True, index=True)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)  # 预约时长(分钟)
    
    # 预约类型
    department = Column(String(100))  # 科室
    appointment_type = Column(String(50))  # 初诊、复诊、检查等
    
    # 状态
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.PENDING)
    
    # 详细信息
    reason = Column(Text)  # 预约原因
    symptoms = Column(Text)  # 症状描述
    notes = Column(Text)  # 备注
    
    # 提醒设置
    reminder_sent = Column(Boolean, default=False)
    reminder_time = Column(DateTime(timezone=True))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="doctor_appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, no='{self.appointment_no}')>"