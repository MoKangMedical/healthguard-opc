"""
通知服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.notification import (
    Notification, NotificationType, NotificationPriority, 
    NotificationChannel, NotificationRule
)
from app.models.user import User
from app.models.patient import Patient

class NotificationService:
    """通知服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channel: NotificationChannel = NotificationChannel.APP,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None,
        extra_data: Optional[Dict] = None,
        expires_hours: int = 72
    ) -> Notification:
        """创建通知"""
        
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            priority=priority,
            channel=channel,
            related_type=related_type,
            related_id=related_id,
            extra_data=extra_data,
            expires_at=datetime.now() + timedelta(hours=expires_hours)
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # 发送通知
        self._send_notification(notification)
        
        return notification
    
    def _send_notification(self, notification: Notification):
        """发送通知（根据渠道）"""
        try:
            if notification.channel == NotificationChannel.APP:
                # 应用内通知，直接存储即可
                notification.is_sent = True
                notification.sent_at = datetime.now()
            
            elif notification.channel == NotificationChannel.SMS:
                # 发送短信
                self._send_sms(notification)
            
            elif notification.channel == NotificationChannel.EMAIL:
                # 发送邮件
                self._send_email(notification)
            
            elif notification.channel == NotificationChannel.WECHAT:
                # 发送微信消息
                self._send_wechat(notification)
            
            self.db.commit()
            
        except Exception as e:
            notification.send_error = str(e)
            self.db.commit()
    
    def _send_sms(self, notification: Notification):
        """发送短信（示例）"""
        # 实际需要接入短信服务商 API
        user = self.db.query(User).filter(User.id == notification.user_id).first()
        if user and user.phone:
            # 调用短信 API
            print(f"SMS sent to {user.phone}: {notification.title}")
            notification.is_sent = True
            notification.sent_at = datetime.now()
    
    def _send_email(self, notification: Notification):
        """发送邮件（示例）"""
        # 实际需要配置 SMTP
        user = self.db.query(User).filter(User.id == notification.user_id).first()
        if user and user.email:
            print(f"Email sent to {user.email}: {notification.title}")
            notification.is_sent = True
            notification.sent_at = datetime.now()
    
    def _send_wechat(self, notification: Notification):
        """发送微信消息（示例）"""
        # 实际需要接入微信 API
        print(f"WeChat sent to user {notification.user_id}: {notification.title}")
        notification.is_sent = True
        notification.sent_at = datetime.now()
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50
    ) -> List[Notification]:
        """获取用户通知"""
        
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            or_(Notification.expires_at.is_(None), Notification.expires_at > datetime.now())
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        if notification_type:
            query = query.filter(Notification.notification_type == notification_type)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """标记通知为已读"""
        
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now()
            self.db.commit()
            return True
        
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.now()
        })
        
        self.db.commit()
        return count
    
    def get_unread_count(self, user_id: int) -> int:
        """获取未读通知数量"""
        
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            or_(Notification.expires_at.is_(None), Notification.expires_at > datetime.now())
        ).count()
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def cleanup_expired(self) -> int:
        """清理过期通知"""
        
        count = self.db.query(Notification).filter(
            Notification.expires_at < datetime.now()
        ).delete()
        
        self.db.commit()
        return count
    
    # ============ 预定义通知 ============
    
    def send_health_alert(
        self,
        patient_id: int,
        alert_type: str,
        value: str,
        threshold: str
    ):
        """发送健康预警"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return
        
        # 给患者发通知
        self.create_notification(
            user_id=patient.user_id,
            title=f"健康预警: {alert_type}",
            content=f"您的{alert_type}值为 {value}，超出正常范围 ({threshold})。请注意休息，如有不适请及时就医。",
            notification_type=NotificationType.HEALTH_ALERT,
            priority=NotificationPriority.HIGH,
            related_type="patient",
            related_id=patient_id
        )
    
    def send_medication_reminder(
        self,
        patient_id: int,
        medication_name: str,
        dosage: str,
        scheduled_time: datetime
    ):
        """发送用药提醒"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return
        
        self.create_notification(
            user_id=patient.user_id,
            title="用药提醒",
            content=f"该服用 {medication_name} {dosage} 了。",
            notification_type=NotificationType.MEDICATION_REMINDER,
            priority=NotificationPriority.NORMAL,
            related_type="medication",
            expires_hours=4
        )
    
    def send_appointment_reminder(
        self,
        patient_id: int,
        doctor_name: str,
        department: str,
        appointment_time: datetime,
        hours_before: int = 24
    ):
        """发送预约提醒"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return
        
        time_str = appointment_time.strftime("%m月%d日 %H:%M")
        
        self.create_notification(
            user_id=patient.user_id,
            title="预约提醒",
            content=f"您在 {department} 的预约将于 {time_str} 开始，医生: {doctor_name}。",
            notification_type=NotificationType.APPOINTMENT_REMINDER,
            priority=NotificationPriority.NORMAL,
            related_type="appointment",
            expires_hours=48
        )
    
    def send_device_alert(
        self,
        patient_id: int,
        device_name: str,
        alert_message: str
    ):
        """发送设备告警"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return
        
        self.create_notification(
            user_id=patient.user_id,
            title=f"设备告警: {device_name}",
            content=alert_message,
            notification_type=NotificationType.DEVICE_ALERT,
            priority=NotificationPriority.HIGH,
            related_type="device",
            expires_hours=24
        )
    
    def send_weekly_report(
        self,
        patient_id: int,
        report_summary: str
    ):
        """发送周报"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return
        
        self.create_notification(
            user_id=patient.user_id,
            title="健康周报",
            content=report_summary,
            notification_type=NotificationType.REPORT,
            priority=NotificationPriority.LOW,
            channel=NotificationChannel.EMAIL,
            expires_hours=168  # 7天
        )