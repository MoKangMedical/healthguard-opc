"""
报表服务 - 生成健康报告
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.patient import Patient
from app.models.health_record import (
    HealthRecord, BloodPressure, BloodSugar, HeartRate, Weight, HealthRecordType
)
from app.models.appointment import Appointment, AppointmentStatus
from app.models.medication import Medication, MedicationReminder, ReminderStatus
from app.models.device import Device, DeviceDataRecord

class ReportService:
    """报表服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_health_report(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """生成健康报告"""
        
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise ValueError("患者不存在")
        
        report = {
            "patient_info": self._get_patient_info(patient),
            "report_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": (end_date - start_date).days
            },
            "blood_pressure": self._analyze_blood_pressure(patient_id, start_date, end_date),
            "blood_sugar": self._analyze_blood_sugar(patient_id, start_date, end_date),
            "heart_rate": self._analyze_heart_rate(patient_id, start_date, end_date),
            "weight": self._analyze_weight(patient_id, start_date, end_date),
            "medications": self._analyze_medications(patient_id, start_date, end_date),
            "appointments": self._analyze_appointments(patient_id, start_date, end_date),
            "devices": self._analyze_devices(patient_id, start_date, end_date),
            "summary": {},
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # 生成摘要和建议
        report["summary"] = self._generate_summary(report)
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _get_patient_info(self, patient: Patient) -> Dict[str, Any]:
        """获取患者基本信息"""
        return {
            "id": patient.id,
            "patient_no": patient.patient_no,
            "name": patient.user.full_name if patient.user else None,
            "age": patient.age,
            "gender": patient.gender,
            "blood_type": patient.blood_type,
            "chronic_conditions": {
                "diabetes": patient.has_diabetes,
                "hypertension": patient.has_hypertension,
                "heart_disease": patient.has_heart_disease
            }
        }
    
    def _analyze_blood_pressure(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析血压数据"""
        
        records = self.db.query(HealthRecord, BloodPressure).join(
            BloodPressure, HealthRecord.id == BloodPressure.health_record_id
        ).filter(
            HealthRecord.patient_id == patient_id,
            HealthRecord.record_type == HealthRecordType.BLOOD_PRESSURE,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date
        ).all()
        
        if not records:
            return {"record_count": 0, "status": "no_data"}
        
        systolic_values = [bp.systolic for _, bp in records]
        diastolic_values = [bp.diastolic for _, bp in records]
        pulse_values = [bp.pulse for _, bp in records if bp.pulse]
        
        avg_systolic = sum(systolic_values) / len(systolic_values)
        avg_diastolic = sum(diastolic_values) / len(diastolic_values)
        
        # 统计异常次数
        high_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                        if s >= 140 or d >= 90)
        low_count = sum(1 for s, d in zip(systolic_values, diastolic_values) 
                       if s < 90 or d < 60)
        
        # 判断状态
        if avg_systolic >= 140 or avg_diastolic >= 90:
            status = "high"
        elif avg_systolic < 90 or avg_diastolic < 60:
            status = "low"
        else:
            status = "normal"
        
        return {
            "record_count": len(records),
            "average": {
                "systolic": round(avg_systolic, 1),
                "diastolic": round(avg_diastolic, 1),
                "pulse": round(sum(pulse_values) / len(pulse_values), 1) if pulse_values else None
            },
            "range": {
                "systolic": {"min": min(systolic_values), "max": max(systolic_values)},
                "diastolic": {"min": min(diastolic_values), "max": max(diastolic_values)}
            },
            "abnormal": {
                "high_count": high_count,
                "low_count": low_count,
                "abnormal_rate": round((high_count + low_count) / len(records) * 100, 1)
            },
            "status": status,
            "trend": self._calculate_trend(systolic_values)
        }
    
    def _analyze_blood_sugar(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析血糖数据"""
        
        records = self.db.query(HealthRecord, BloodSugar).join(
            BloodSugar, HealthRecord.id == BloodSugar.health_record_id
        ).filter(
            HealthRecord.patient_id == patient_id,
            HealthRecord.record_type == HealthRecordType.BLOOD_SUGAR,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date
        ).all()
        
        if not records:
            return {"record_count": 0, "status": "no_data"}
        
        values = [bs.value for _, bs in records]
        avg_value = sum(values) / len(values)
        
        # 按测量时间分组
        fasting_values = [bs.value for _, bs in records if bs.measurement_time == "fasting"]
        postprandial_values = [bs.value for _, bs in records if bs.measurement_time == "after_meal"]
        
        high_count = sum(1 for v in values if v >= 7.0)
        low_count = sum(1 for v in values if v < 3.9)
        
        if avg_value >= 7.0:
            status = "high"
        elif avg_value < 3.9:
            status = "low"
        else:
            status = "normal"
        
        return {
            "record_count": len(records),
            "average": round(avg_value, 1),
            "fasting_average": round(sum(fasting_values) / len(fasting_values), 1) if fasting_values else None,
            "postprandial_average": round(sum(postprandial_values) / len(postprandial_values), 1) if postprandial_values else None,
            "range": {"min": min(values), "max": max(values)},
            "abnormal": {
                "high_count": high_count,
                "low_count": low_count,
                "abnormal_rate": round((high_count + low_count) / len(records) * 100, 1)
            },
            "status": status
        }
    
    def _analyze_heart_rate(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析心率数据"""
        
        records = self.db.query(HealthRecord, HeartRate).join(
            HeartRate, HealthRecord.id == HeartRate.health_record_id
        ).filter(
            HealthRecord.patient_id == patient_id,
            HealthRecord.record_type == HealthRecordType.HEART_RATE,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date
        ).all()
        
        if not records:
            return {"record_count": 0, "status": "no_data"}
        
        values = [hr.bpm for _, hr in records]
        avg_bpm = sum(values) / len(values)
        
        return {
            "record_count": len(records),
            "average_bpm": round(avg_bpm, 1),
            "range": {"min": min(values), "max": max(values)},
            "status": "normal" if 60 <= avg_bpm <= 100 else "abnormal"
        }
    
    def _analyze_weight(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析体重数据"""
        
        records = self.db.query(HealthRecord, Weight).join(
            Weight, HealthRecord.id == Weight.health_record_id
        ).filter(
            HealthRecord.patient_id == patient_id,
            HealthRecord.record_type == HealthRecordType.WEIGHT,
            HealthRecord.record_date >= start_date,
            HealthRecord.record_date <= end_date
        ).all()
        
        if not records:
            return {"record_count": 0, "status": "no_data"}
        
        values = [w.value for _, w in records]
        bmi_values = [w.bmi for _, w in records if w.bmi]
        
        avg_weight = sum(values) / len(values)
        avg_bmi = sum(bmi_values) / len(bmi_values) if bmi_values else None
        
        weight_change = values[-1] - values[0] if len(values) > 1 else 0
        
        # BMI 状态
        if avg_bmi:
            if avg_bmi < 18.5:
                bmi_status = "underweight"
            elif avg_bmi < 24:
                bmi_status = "normal"
            elif avg_bmi < 28:
                bmi_status = "overweight"
            else:
                bmi_status = "obese"
        else:
            bmi_status = "unknown"
        
        return {
            "record_count": len(records),
            "average_weight": round(avg_weight, 1),
            "average_bmi": round(avg_bmi, 1) if avg_bmi else None,
            "range": {"min": min(values), "max": max(values)},
            "change": round(weight_change, 1),
            "bmi_status": bmi_status
        }
    
    def _analyze_medications(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析用药情况"""
        
        # 获取活跃药物
        active_medications = self.db.query(Medication).filter(
            Medication.patient_id == patient_id,
            Medication.is_active == True
        ).all()
        
        # 获取提醒统计
        reminders = self.db.query(MedicationReminder).join(
            Medication
        ).filter(
            Medication.patient_id == patient_id,
            MedicationReminder.scheduled_time >= start_date,
            MedicationReminder.scheduled_time <= end_date
        ).all()
        
        total_reminders = len(reminders)
        acknowledged = sum(1 for r in reminders if r.status == ReminderStatus.ACKNOWLEDGED)
        missed = sum(1 for r in reminders if r.status == ReminderStatus.MISSED)
        
        adherence_rate = (acknowledged / total_reminders * 100) if total_reminders > 0 else 0
        
        return {
            "active_count": len(active_medications),
            "medications": [
                {
                    "name": m.medication_name,
                    "dosage": m.dosage,
                    "frequency": m.frequency,
                    "remaining": m.remaining
                }
                for m in active_medications
            ],
            "adherence": {
                "total_reminders": total_reminders,
                "acknowledged": acknowledged,
                "missed": missed,
                "adherence_rate": round(adherence_rate, 1)
            }
        }
    
    def _analyze_appointments(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析预约情况"""
        
        appointments = self.db.query(Appointment).filter(
            Appointment.patient_id == patient_id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        ).all()
        
        completed = sum(1 for a in appointments if a.status == AppointmentStatus.COMPLETED)
        cancelled = sum(1 for a in appointments if a.status == AppointmentStatus.CANCELLED)
        no_show = sum(1 for a in appointments if a.status == AppointmentStatus.NO_SHOW)
        
        return {
            "total": len(appointments),
            "completed": completed,
            "cancelled": cancelled,
            "no_show": no_show,
            "upcoming": sum(1 for a in appointments if a.status in 
                          [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED])
        }
    
    def _analyze_devices(
        self,
        patient_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """分析设备使用情况"""
        
        devices = self.db.query(Device).filter(Device.patient_id == patient_id).all()
        
        device_stats = []
        for device in devices:
            data_count = self.db.query(DeviceDataRecord).filter(
                DeviceDataRecord.device_id == device.id,
                DeviceDataRecord.measured_at >= start_date,
                DeviceDataRecord.measured_at <= end_date
            ).count()
            
            device_stats.append({
                "name": device.device_name,
                "type": device.device_type.value,
                "status": device.status.value,
                "data_count": data_count
            })
        
        return {
            "total_devices": len(devices),
            "online_devices": sum(1 for d in devices if d.status.value == "online"),
            "devices": device_stats
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "stable"
        
        # 简单趋势判断
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff = second_half - first_half
        if diff > 5:
            return "increasing"
        elif diff < -5:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """生成报告摘要"""
        
        summary = {
            "health_status": "good",
            "alerts": [],
            "highlights": []
        }
        
        # 检查血压
        bp = report.get("blood_pressure", {})
        if bp.get("status") == "high":
            summary["health_status"] = "attention_needed"
            summary["alerts"].append("血压偏高，建议咨询医生")
        elif bp.get("status") == "low":
            summary["alerts"].append("血压偏低，请注意休息")
        
        # 检查血糖
        bs = report.get("blood_sugar", {})
        if bs.get("status") == "high":
            summary["health_status"] = "attention_needed"
            summary["alerts"].append("血糖偏高，请注意饮食控制")
        elif bs.get("status") == "low":
            summary["alerts"].append("血糖偏低，请及时补充糖分")
        
        # 检查用药依从性
        med = report.get("medications", {})
        adherence = med.get("adherence", {})
        if adherence.get("adherence_rate", 100) < 80:
            summary["alerts"].append(f"用药依从性较低 ({adherence.get('adherence_rate')}%)，请按时服药")
        
        # 生成亮点
        if bp.get("status") == "normal":
            summary["highlights"].append("血压控制良好")
        if bs.get("status") == "normal":
            summary["highlights"].append("血糖控制良好")
        if adherence.get("adherence_rate", 0) >= 90:
            summary["highlights"].append("用药依从性优秀")
        
        return summary
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成健康建议"""
        
        recommendations = []
        
        # 基于血压的建议
        bp = report.get("blood_pressure", {})
        if bp.get("status") == "high":
            recommendations.append("建议减少盐分摄入，每天控制在6克以下")
            recommendations.append("建议适量运动，如每天步行30分钟")
            recommendations.append("建议保持充足睡眠，每天7-8小时")
        
        # 基于血糖的建议
        bs = report.get("blood_sugar", {})
        if bs.get("status") == "high":
            recommendations.append("建议控制碳水化合物摄入")
            recommendations.append("建议增加膳食纤维摄入")
            recommendations.append("建议餐后适当活动")
        
        # 基于体重的建议
        weight = report.get("weight", {})
        if weight.get("bmi_status") == "overweight":
            recommendations.append("建议控制饮食，减少高热量食物摄入")
            recommendations.append("建议增加运动量，每周至少150分钟中等强度运动")
        elif weight.get("bmi_status") == "underweight":
            recommendations.append("建议增加营养摄入，保证蛋白质和热量充足")
        
        # 通用建议
        recommendations.append("建议定期监测健康指标")
        recommendations.append("建议保持良好的生活习惯")
        
        return recommendations
    
    def generate_weekly_report(self, patient_id: int) -> Dict[str, Any]:
        """生成周报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        return self.generate_health_report(patient_id, start_date, end_date)
    
    def generate_monthly_report(self, patient_id: int) -> Dict[str, Any]:
        """生成月报"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return self.generate_health_report(patient_id, start_date, end_date)