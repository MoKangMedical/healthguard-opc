"""
飞书集成服务
"""

import json
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from sqlalchemy.orm import Session

from app.config import settings
from app.models.notification import Notification, NotificationType


class FeishuService:
    """飞书服务类"""
    
    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self.base_url = "https://open.feishu.cn/open-apis"
        self._tenant_token = None
        self._token_expires = None
        
        # 初始化飞书 SDK
        if self.app_id and self.app_secret:
            self.client = lark.Client.builder() \
                .app_id(self.app_id) \
                .app_secret(self.app_secret) \
                .log_level(lark.LogLevel.INFO) \
                .build()
        else:
            self.client = None
    
    async def _get_tenant_token(self) -> str:
        """获取 tenant_access_token"""
        if self._tenant_token and self._token_expires and datetime.now() < self._token_expires:
            return self._tenant_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/v3/tenant_access_token/internal",
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret
                }
            )
            
            data = response.json()
            if data.get("code") == 0:
                self._tenant_token = data["tenant_access_token"]
                # Token 有效期 2 小时，提前 10 分钟刷新
                from datetime import timedelta
                self._token_expires = datetime.now() + timedelta(seconds=data.get("expire", 7200) - 600)
                return self._tenant_token
            else:
                raise Exception(f"获取 tenant_token 失败: {data.get('msg')}")
    
    async def send_message(
        self,
        receive_id: str,
        content: str,
        msg_type: str = "text",
        receive_id_type: str = "open_id"
    ) -> Dict[str, Any]:
        """发送消息"""
        
        if not self.app_id or not self.app_secret:
            raise Exception("飞书 App ID 或 Secret 未配置")
        
        token = await self._get_tenant_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/im/v1/messages",
                params={"receive_id_type": receive_id_type},
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json={
                    "receive_id": receive_id,
                    "msg_type": msg_type,
                    "content": content if msg_type == "text" else json.dumps(content)
                }
            )
            
            return response.json()
    
    async def send_text(self, receive_id: str, text: str) -> Dict[str, Any]:
        """发送文本消息"""
        content = json.dumps({"text": text})
        return await self.send_message(receive_id, content, "text")
    
    async def send_card(self, receive_id: str, card: Dict[str, Any]) -> Dict[str, Any]:
        """发送卡片消息"""
        return await self.send_message(receive_id, card, "interactive")
    
    def create_health_alert_card(
        self,
        title: str,
        alert_type: str,
        value: str,
        threshold: str,
        patient_name: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """创建健康预警卡片"""
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"⚠️ {title}"
                },
                "template": "red"
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**患者**: {patient_name}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**类型**: {alert_type}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**当前值**: {value}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**阈值**: {threshold}"
                            }
                        }
                    ]
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"⏰ {timestamp}"
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(card)
    
    def create_medication_reminder_card(
        self,
        medication_name: str,
        dosage: str,
        patient_name: str,
        scheduled_time: str
    ) -> Dict[str, Any]:
        """创建用药提醒卡片"""
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "💊 用药提醒"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**患者**: {patient_name}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**药物**: {medication_name}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**剂量**: {dosage}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**时间**: {scheduled_time}"
                            }
                        }
                    ]
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "tag": "plain_text",
                                "content": "✅ 已服药"
                            },
                            "type": "primary",
                            "value": {
                                "action": "medication_taken"
                            }
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(card)
    
    def create_appointment_reminder_card(
        self,
        patient_name: str,
        department: str,
        doctor_name: str,
        appointment_time: str,
        appointment_no: str
    ) -> Dict[str, Any]:
        """创建预约提醒卡片"""
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📅 预约提醒"
                },
                "template": "green"
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**患者**: {patient_name}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**预约号**: {appointment_no}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**科室**: {department}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**医生**: {doctor_name}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**就诊时间**: {appointment_time}"
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "请提前15分钟到达医院"
                        }
                    ]
                }
            ]
        }
        
        return json.dumps(card)
    
    def create_weekly_report_card(
        self,
        patient_name: str,
        bp_status: str,
        bp_value: str,
        bs_status: str,
        bs_value: str,
        adherence: int,
        recommendations: List[str]
    ) -> Dict[str, Any]:
        """创建周报卡片"""
        
        status_emoji = {
            "normal": "✅",
            "high": "⚠️",
            "low": "⬇️",
            "attention_needed": "⚠️"
        }
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "📊 健康周报"
                },
                "template": "turquoise"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**患者**: {patient_name}"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"{status_emoji.get(bp_status, '')} **血压**\n{bp_value}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"{status_emoji.get(bs_status, '')} **血糖**\n{bs_value}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"💊 **用药依从性**: {adherence}%"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**💡 健康建议**\n" + "\n".join([f"• {r}" for r in recommendations[:3]])
                    }
                }
            ]
        }
        
        return json.dumps(card)
    
    def create_device_alert_card(
        self,
        device_name: str,
        device_type: str,
        alert_message: str,
        patient_name: str
    ) -> Dict[str, Any]:
        """创建设备告警卡片"""
        
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": "🔌 设备告警"
                },
                "template": "orange"
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**设备**: {device_name}"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "tag": "lark_md",
                                "content": f"**类型**: {device_type}"
                            }
                        }
                    ]
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**告警信息**: {alert_message}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**关联患者**: {patient_name}"
                    }
                }
            ]
        }
        
        return json.dumps(card)


class FeishuNotificationSender:
    """飞书通知发送器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.feishu = FeishuService()
    
    async def send_notification(
        self,
        notification: Notification,
        feishu_user_id: str
    ) -> bool:
        """发送通知到飞书"""
        
        try:
            if notification.notification_type == NotificationType.HEALTH_ALERT:
                return await self._send_health_alert(notification, feishu_user_id)
            elif notification.notification_type == NotificationType.MEDICATION_REMINDER:
                return await self._send_medication_reminder(notification, feishu_user_id)
            elif notification.notification_type == NotificationType.APPOINTMENT_REMINDER:
                return await self._send_appointment_reminder(notification, feishu_user_id)
            elif notification.notification_type == NotificationType.REPORT:
                return await self._send_report(notification, feishu_user_id)
            elif notification.notification_type == NotificationType.DEVICE_ALERT:
                return await self._send_device_alert(notification, feishu_user_id)
            else:
                # 默认发送文本消息
                await self.feishu.send_text(
                    feishu_user_id,
                    f"{notification.title}\n\n{notification.content}"
                )
                return True
                
        except Exception as e:
            print(f"发送飞书通知失败: {e}")
            return False
    
    async def _send_health_alert(self, notification: Notification, feishu_user_id: str) -> bool:
        """发送健康预警"""
        extra_data = notification.extra_data or {}
        
        card = self.feishu.create_health_alert_card(
            title=notification.title,
            alert_type=extra_data.get("alert_type", "未知"),
            value=extra_data.get("value", "--"),
            threshold=extra_data.get("threshold", "--"),
            patient_name=extra_data.get("patient_name", "--"),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        
        await self.feishu.send_message(feishu_user_id, card, "interactive")
        return True
    
    async def _send_medication_reminder(self, notification: Notification, feishu_user_id: str) -> bool:
        """发送用药提醒"""
        extra_data = notification.extra_data or {}
        
        card = self.feishu.create_medication_reminder_card(
            medication_name=extra_data.get("medication_name", "--"),
            dosage=extra_data.get("dosage", "--"),
            patient_name=extra_data.get("patient_name", "--"),
            scheduled_time=datetime.now().strftime("%H:%M")
        )
        
        await self.feishu.send_message(feishu_user_id, card, "interactive")
        return True
    
    async def _send_appointment_reminder(self, notification: Notification, feishu_user_id: str) -> bool:
        """发送预约提醒"""
        extra_data = notification.extra_data or {}
        
        card = self.feishu.create_appointment_reminder_card(
            patient_name=extra_data.get("patient_name", "--"),
            department=extra_data.get("department", "--"),
            doctor_name=extra_data.get("doctor_name", "--"),
            appointment_time=extra_data.get("appointment_time", "--"),
            appointment_no=extra_data.get("appointment_no", "--")
        )
        
        await self.feishu.send_message(feishu_user_id, card, "interactive")
        return True
    
    async def _send_report(self, notification: Notification, feishu_user_id: str) -> bool:
        """发送报告"""
        extra_data = notification.extra_data or {}
        
        card = self.feishu.create_weekly_report_card(
            patient_name=extra_data.get("patient_name", "--"),
            bp_status=extra_data.get("bp_status", "normal"),
            bp_value=extra_data.get("bp_value", "--/-- mmHg"),
            bs_status=extra_data.get("bs_status", "normal"),
            bs_value=extra_data.get("bs_value", "-- mmol/L"),
            adherence=extra_data.get("adherence", 100),
            recommendations=extra_data.get("recommendations", [])
        )
        
        await self.feishu.send_message(feishu_user_id, card, "interactive")
        return True
    
    async def _send_device_alert(self, notification: Notification, feishu_user_id: str) -> bool:
        """发送设备告警"""
        extra_data = notification.extra_data or {}
        
        card = self.feishu.create_device_alert_card(
            device_name=extra_data.get("device_name", "--"),
            device_type=extra_data.get("device_type", "--"),
            alert_message=notification.content,
            patient_name=extra_data.get("patient_name", "--")
        )
        
        await self.feishu.send_message(feishu_user_id, card, "interactive")
        return True


# 创建全局实例
feishu_service = FeishuService()