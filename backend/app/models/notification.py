"""
通知模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base

class NotificationType(str, enum.Enum):
    """通知类型"""
    HEALTH_ALERT = "health_alert"          # 健康预警
    MEDICATION_REMINDER = "medication"     # 用药提醒
    APPOINTMENT_REMINDER = "appointment"   # 预约提醒
    DEVICE_ALERT = "device_alert"          # 设备告警
    SYSTEM = "system"                      # 系统通知
    REPORT = "report"                      # 报告通知

class NotificationPriority(str, enum.Enum):
    """通知优先级"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationChannel(str, enum.Enum):
    """通知渠道"""
    APP = "app"              # 应用内通知
    SMS = "sms"              # 短信
    EMAIL = "email"          # 邮件
    WECHAT = "wechat"        # 微信
    PUSH = "push"            # 推送通知

class Notification(Base):
    """通知表"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 接收者
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 通知内容
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # 渠道
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.APP)
    
    # 关联
    related_type = Column(String(50))  # patient, device, appointment 等
    related_id = Column(Integer)
    extra_data = Column(JSON)
    
    # 状态
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True))
    
    # 发送状态
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    send_error = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # 过期时间
    
    # 关系
    user = relationship("User")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}')>"

class NotificationRule(Base):
    """通知规则表（用于自动触发通知）"""
    __tablename__ = "notification_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 规则信息
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # 触发条件
    trigger_type = Column(String(50), nullable=False)  # health_value, device_status, schedule
    trigger_condition = Column(JSON, nullable=False)  # 触发条件配置
    
    # 通知配置
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.NORMAL)
    channels = Column(JSON, default=["app"])  # 通知渠道列表
    
    # 消息模板
    title_template = Column(String(500))
    content_template = Column(Text)
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<NotificationRule(id={self.id}, name='{self.name}')>"