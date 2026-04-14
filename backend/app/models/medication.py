"""
用药管理模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class ReminderStatus(str, enum.Enum):
    """提醒状态"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    MISSED = "missed"

class Medication(Base):
    """药物/处方表"""
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # 药物信息
    medication_name = Column(String(200), nullable=False)
    generic_name = Column(String(200))  # 通用名
    brand_name = Column(String(200))  # 商品名
    
    # 用药信息
    dosage = Column(String(100))  # 剂量，如 "500mg"
    frequency = Column(String(100))  # 频率，如 "每日3次"
    route = Column(String(50))  # 用药途径，如 "口服"
    
    # 处方信息
    prescribed_by = Column(Integer, ForeignKey("users.id"))  # 开药医生
    prescription_date = Column(DateTime(timezone=True))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # 用量信息
    quantity = Column(Integer)  # 总量
    remaining = Column(Integer)  # 剩余量
    
    # 用药说明
    instructions = Column(Text)  # 用药说明
    side_effects = Column(Text)  # 副作用
    precautions = Column(Text)  # 注意事项
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    patient = relationship("Patient", back_populates="medications")
    reminders = relationship("MedicationReminder", back_populates="medication")

class MedicationReminder(Base):
    """用药提醒表"""
    __tablename__ = "medication_reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)
    
    # 提醒信息
    reminder_time = Column(DateTime(timezone=True), nullable=False)
    scheduled_time = Column(DateTime(timezone=True))  # 计划用药时间
    
    # 状态
    status = Column(Enum(ReminderStatus), default=ReminderStatus.PENDING)
    
    # 记录
    acknowledged_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    medication = relationship("Medication", back_populates="reminders")