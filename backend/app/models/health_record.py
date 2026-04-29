"""
健康记录模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class HealthRecordType(str, enum.Enum):
    """健康记录类型"""
    BLOOD_PRESSURE = "blood_pressure"
    BLOOD_SUGAR = "blood_sugar"
    HEART_RATE = "heart_rate"
    WEIGHT = "weight"
    TEMPERATURE = "temperature"
    OXYGEN_SATURATION = "oxygen_saturation"
    OTHER = "other"

class HealthRecord(Base):
    """健康记录主表"""
    __tablename__ = "health_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    record_type = Column(Enum(HealthRecordType), nullable=False)
    record_date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text)
    
    # 异常标记
    is_abnormal = Column(Boolean, default=False)
    abnormal_notes = Column(Text)
    
    # 记录来源
    source = Column(String(50))  # manual, device, import
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    patient = relationship("Patient", back_populates="health_records")
    blood_pressure = relationship("BloodPressure", back_populates="health_record", uselist=False)
    blood_sugar = relationship("BloodSugar", back_populates="health_record", uselist=False)
    heart_rate = relationship("HeartRate", back_populates="health_record", uselist=False)
    weight = relationship("Weight", back_populates="health_record", uselist=False)

class BloodPressure(Base):
    """血压记录"""
    __tablename__ = "blood_pressures"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id"), unique=True, nullable=False)
    
    systolic = Column(Integer, nullable=False)  # 收缩压
    diastolic = Column(Integer, nullable=False)  # 舒张压
    pulse = Column(Integer)  # 脉搏
    
    health_record = relationship("HealthRecord", back_populates="blood_pressure")

class BloodSugar(Base):
    """血糖记录"""
    __tablename__ = "blood_sugars"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id"), unique=True, nullable=False)
    
    value = Column(Float, nullable=False)  # 血糖值
    unit = Column(String(10), default="mmol/L")  # 单位
    measurement_time = Column(String(50))  # 测量时间：空腹、餐后1h、餐后2h等
    
    health_record = relationship("HealthRecord", back_populates="blood_sugar")

class HeartRate(Base):
    """心率记录"""
    __tablename__ = "heart_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id"), unique=True, nullable=False)
    
    bpm = Column(Integer, nullable=False)  # 每分钟心跳数
    is_resting = Column(Boolean, default=True)  # 是否静息状态
    
    health_record = relationship("HealthRecord", back_populates="heart_rate")

class Weight(Base):
    """体重记录"""
    __tablename__ = "weights"
    
    id = Column(Integer, primary_key=True, index=True)
    health_record_id = Column(Integer, ForeignKey("health_records.id"), unique=True, nullable=False)
    
    value = Column(Float, nullable=False)  # 体重值(kg)
    height = Column(Float)  # 身高(cm)，用于计算BMI
    bmi = Column(Float)  # BMI指数
    
    health_record = relationship("HealthRecord", back_populates="weight")