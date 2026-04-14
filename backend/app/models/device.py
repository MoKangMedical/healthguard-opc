"""
设备管理模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class DeviceType(str, enum.Enum):
    """设备类型"""
    BLOOD_PRESSURE = "blood_pressure"      # 血压计
    BLOOD_SUGAR = "blood_sugar"            # 血糖仪
    HEART_RATE = "heart_rate"              # 心率监测器
    WEIGHT_SCALE = "weight_scale"          # 体重秤
    PULSE_OXIMETER = "pulse_oximeter"      # 血氧仪
    THERMOMETER = "thermometer"            # 体温计
    ECG = "ecg"                            # 心电图仪
    WEARABLE = "wearable"                  # 智能穿戴设备
    OTHER = "other"                        # 其他

class DeviceStatus(str, enum.Enum):
    """设备状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class ConnectionType(str, enum.Enum):
    """连接方式"""
    BLUETOOTH = "bluetooth"                # 蓝牙
    WIFI = "wifi"                          # WiFi
    USB = "usb"                            # USB
    SERIAL = "serial"                      # 串口
    API = "api"                            # API接口
    GATEWAY = "gateway"                    # 网关

class Device(Base):
    """设备表"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 设备信息
    device_sn = Column(String(100), unique=True, index=True, nullable=False)  # 序列号
    device_name = Column(String(200), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    brand = Column(String(100))            # 品牌
    model = Column(String(100))            # 型号
    
    # 连接信息
    connection_type = Column(Enum(ConnectionType), nullable=False)
    connection_config = Column(JSON)       # 连接配置 (IP、端口、MAC地址等)
    
    # 状态
    status = Column(Enum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_online = Column(DateTime(timezone=True))
    
    # 关联患者
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    
    # 设备能力
    capabilities = Column(JSON)            # 支持的测量类型
    
    # 固件信息
    firmware_version = Column(String(50))
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    patient = relationship("Patient", back_populates="devices")
    data_records = relationship("DeviceDataRecord", back_populates="device")
    
    def __repr__(self):
        return f"<Device(sn='{self.device_sn}', type='{self.device_type}')>"

class DeviceDataRecord(Base):
    """设备数据记录表"""
    __tablename__ = "device_data_records"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # 原始数据
    raw_data = Column(JSON, nullable=False)  # 设备返回的原始数据
    
    # 解析后的数据
    data_type = Column(String(50))         # 数据类型
    parsed_data = Column(JSON)             # 解析后的结构化数据
    
    # 数据质量
    quality = Column(String(20))           # good, warning, error
    error_message = Column(Text)
    
    # 时间戳
    measured_at = Column(DateTime(timezone=True), nullable=False)  # 测量时间
    received_at = Column(DateTime(timezone=True), server_default=func.now())  # 接收时间
    
    # 关系
    device = relationship("Device", back_populates="data_records")
    patient = relationship("Patient")
    
    def __repr__(self):
        return f"<DeviceDataRecord(device_id={self.device_id}, type='{self.data_type}')>"

class DeviceCommand(Base):
    """设备命令表（用于下发指令）"""
    __tablename__ = "device_commands"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    # 命令信息
    command = Column(String(100), nullable=False)  # 命令类型
    params = Column(JSON)                          # 命令参数
    
    # 状态
    status = Column(String(20), default="pending")  # pending, sent, success, failed
    result = Column(JSON)                           # 执行结果
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # 关系
    device = relationship("Device")
