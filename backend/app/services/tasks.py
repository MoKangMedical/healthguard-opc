"""
定时任务服务
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from celery import Celery
from celery.schedules import crontab

from app.config import settings
from app.models.patient import Patient
from app.models.medication import Medication, MedicationReminder, ReminderStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.device import Device, DeviceStatus
from app.models.notification import NotificationType
from app.services.notification_service import NotificationService
from app.services.report_service import ReportService

# 创建 Celery 应用
celery_app = Celery(
    'healthguard',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# 配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天早上 8 点发送用药提醒
    'medication-reminder-morning': {
        'task': 'app.services.tasks.send_medication_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
    # 每天中午 12 点发送用药提醒
    'medication-reminder-noon': {
        'task': 'app.services.tasks.send_medication_reminders',
        'schedule': crontab(hour=12, minute=0),
    },
    # 每天晚上 8 点发送用药提醒
    'medication-reminder-evening': {
        'task': 'app.services.tasks.send_medication_reminders',
        'schedule': crontab(hour=20, minute=0),
    },
    # 每天早上 9 点检查预约提醒
    'appointment-reminder-daily': {
        'task': 'app.services.tasks.check_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    # 每小时检查设备状态
    'device-status-check': {
        'task': 'app.services.tasks.check_device_status',
        'schedule': crontab(minute=0),
    },
    # 每周日晚上 8 点生成周报
    'weekly-report': {
        'task': 'app.services.tasks.generate_weekly_reports',
        'schedule': crontab(hour=20, minute=0, day_of_week=0),
    },
    # 每月 1 号凌晨 2 点清理过期通知
    'cleanup-notifications': {
        'task': 'app.services.tasks.cleanup_expired_notifications',
        'schedule': crontab(hour=2, minute=0, day_of_month=1),
    },
}

class TaskService:
    """定时任务服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_medication_reminders(self):
        """发送用药提醒"""
        
        notification_service = NotificationService(self.db)
        
        # 获取当前时间
        now = datetime.now()
        current_hour = now.hour
        
        # 根据时间确定应该发送哪些提醒
        reminder_hours = {
            8: ['每日1次', '每日2次', '每日3次', '每日4次'],
            12: ['每日2次', '每日3次', '每日4次'],
            14: ['每日3次', '每日4次'],
            16: ['每日4次'],
            20: ['每日1次', '每日2次', '每日3次', '每日4次'],
        }
        
        applicable_frequencies = reminder_hours.get(current_hour, [])
        
        if not applicable_frequencies:
            return
        
        # 获取需要提醒的药物
        medications = self.db.query(Medication).filter(
            Medication.is_active == True,
            Medication.frequency.in_(applicable_frequencies)
        ).all()
        
        for medication in medications:
            # 检查今天是否已经提醒过
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            existing_reminder = self.db.query(MedicationReminder).filter(
                MedicationReminder.medication_id == medication.id,
                MedicationReminder.scheduled_time >= today_start,
                MedicationReminder.scheduled_time < today_end,
                MedicationReminder.scheduled_time.hour == current_hour
            ).first()
            
            if not existing_reminder:
                # 创建提醒记录
                reminder = MedicationReminder(
                    medication_id=medication.id,
                    reminder_time=now,
                    scheduled_time=now,
                    status=ReminderStatus.PENDING
                )
                self.db.add(reminder)
                
                # 发送通知
                notification_service.send_medication_reminder(
                    patient_id=medication.patient_id,
                    medication_name=medication.medication_name,
                    dosage=medication.dosage or '',
                    scheduled_time=now
                )
        
        self.db.commit()
    
    def check_appointment_reminders(self):
        """检查并发送预约提醒"""
        
        notification_service = NotificationService(self.db)
        
        # 获取明天的预约
        tomorrow = datetime.now().date() + timedelta(days=1)
        tomorrow_start = datetime.combine(tomorrow, datetime.min.time())
        tomorrow_end = datetime.combine(tomorrow, datetime.max.time())
        
        appointments = self.db.query(Appointment).filter(
            Appointment.appointment_date >= tomorrow_start,
            Appointment.appointment_date <= tomorrow_end,
            Appointment.status.in_([AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        ).all()
        
        for appointment in appointments:
            # 检查是否已经提醒过
            # 这里简化处理，实际应该检查通知记录
            
            patient = self.db.query(Patient).filter(Patient.id == appointment.patient_id).first()
            if patient:
                notification_service.send_appointment_reminder(
                    patient_id=appointment.patient_id,
                    doctor_name=appointment.doctor.full_name if appointment.doctor else '待定',
                    department=appointment.department or '待定',
                    appointment_time=appointment.appointment_date
                )
    
    def check_device_status(self):
        """检查设备状态"""
        
        notification_service = NotificationService(self.db)
        
        # 检查长时间离线的设备
        offline_threshold = datetime.now() - timedelta(hours=24)
        
        devices = self.db.query(Device).filter(
            Device.status == DeviceStatus.OFFLINE,
            Device.last_online < offline_threshold,
            Device.patient_id.isnot(None)
        ).all()
        
        for device in devices:
            if device.patient_id:
                notification_service.send_device_alert(
                    patient_id=device.patient_id,
                    device_name=device.device_name,
                    alert_message=f"设备 {device.device_name} 已离线超过 24 小时，请检查设备连接。"
                )
    
    def generate_weekly_reports(self):
        """生成周报"""
        
        notification_service = NotificationService(self.db)
        report_service = ReportService(self.db)
        
        # 获取所有活跃患者
        patients = self.db.query(Patient).all()
        
        for patient in patients:
            try:
                # 生成周报
                report = report_service.generate_weekly_report(patient.id)
                
                # 生成摘要文本
                summary = self._format_report_summary(report)
                
                # 发送周报通知
                notification_service.send_weekly_report(
                    patient_id=patient.id,
                    report_summary=summary
                )
            except Exception as e:
                print(f"生成周报失败 (patient_id={patient.id}): {e}")
    
    def _format_report_summary(self, report: Dict[str, Any]) -> str:
        """格式化报告摘要"""
        
        lines = ["📊 健康周报摘要\n"]
        
        # 血压
        bp = report.get('blood_pressure', {})
        if bp.get('status') != 'no_data':
            avg = bp.get('average', {})
            lines.append(f"❤️ 血压: {avg.get('systolic', '--')}/{avg.get('diastolic', '--')} mmHg ({bp.get('status', '--')})")
        
        # 血糖
        bs = report.get('blood_sugar', {})
        if bs.get('status') != 'no_data':
            lines.append(f"🩸 血糖: {bs.get('average', '--')} mmol/L ({bs.get('status', '--')})")
        
        # 用药依从性
        med = report.get('medications', {})
        adherence = med.get('adherence', {})
        if adherence:
            lines.append(f"💊 用药依从性: {adherence.get('adherence_rate', '--')}%")
        
        # 建议
        recommendations = report.get('recommendations', [])
        if recommendations:
            lines.append("\n📋 健康建议:")
            for rec in recommendations[:3]:
                lines.append(f"  • {rec}")
        
        return '\n'.join(lines)
    
    def cleanup_expired_notifications(self):
        """清理过期通知"""
        
        notification_service = NotificationService(self.db)
        count = notification_service.cleanup_expired()
        
        print(f"清理了 {count} 条过期通知")


# Celery 任务定义
@celery_app.task
def send_medication_reminders():
    """发送用药提醒任务"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        service = TaskService(db)
        service.send_medication_reminders()
    finally:
        db.close()

@celery_app.task
def check_appointment_reminders():
    """检查预约提醒任务"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        service = TaskService(db)
        service.check_appointment_reminders()
    finally:
        db.close()

@celery_app.task
def check_device_status():
    """检查设备状态任务"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        service = TaskService(db)
        service.check_device_status()
    finally:
        db.close()

@celery_app.task
def generate_weekly_reports():
    """生成周报任务"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        service = TaskService(db)
        service.generate_weekly_reports()
    finally:
        db.close()

@celery_app.task
def cleanup_expired_notifications():
    """清理过期通知任务"""
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        service = TaskService(db)
        service.cleanup_expired_notifications()
    finally:
        db.close()