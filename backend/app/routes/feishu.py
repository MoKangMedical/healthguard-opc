"""
飞书集成路由
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import hashlib

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.feishu_service import FeishuService
from app.config import settings

router = APIRouter()

# 飞书服务实例
feishu = FeishuService()

@router.get("/status", summary="飞书连接状态")
async def feishu_status():
    """检查飞书连接状态"""
    
    is_configured = bool(settings.FEISHU_APP_ID and settings.FEISHU_APP_SECRET)
    
    return {
        "configured": is_configured,
        "app_id": settings.FEISHU_APP_ID[:8] + "..." if settings.FEISHU_APP_ID else None,
        "domain": settings.FEISHU_DOMAIN
    }

@router.post("/webhook", summary="飞书事件回调")
async def feishu_webhook(request: Request, db: Session = Depends(get_db)):
    """接收飞书事件回调"""
    
    body = await request.json()
    
    # 处理 URL 验证请求
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}
    
    # 处理事件
    event = body.get("event", {})
    event_type = body.get("header", {}).get("event_type", "")
    
    if event_type == "im.message.receive_v1":
        # 收到消息事件
        await handle_message_event(event, db)
    
    elif event_type == "card.action.trigger":
        # 卡片按钮点击事件
        return await handle_card_action(event, db)
    
    return {"code": 0}

async def handle_message_event(event: Dict[str, Any], db: Session):
    """处理消息事件"""
    
    message = event.get("message", {})
    sender = event.get("sender", {})
    
    message_type = message.get("message_type")
    content = json.loads(message.get("content", "{}"))
    sender_id = sender.get("sender_id", {}).get("open_id")
    
    # 只处理文本消息
    if message_type == "text":
        text = content.get("text", "")
        
        # 处理命令
        if text.startswith("/"):
            await handle_command(text, sender_id, message.get("chat_id"), db)
        else:
            # 普通消息，可以记录或忽略
            pass

async def handle_command(
    command: str,
    sender_id: str,
    chat_id: str,
    db: Session
):
    """处理飞书命令"""
    
    cmd = command.split()[0].lower()
    
    if cmd == "/help":
        help_text = """
🏥 HealthGuard OPC 健康管理助手

可用命令:
/help - 显示帮助信息
/status - 查看健康状态
/today - 查看今日提醒
/weekly - 获取周报
/bind <患者ID> - 绑定患者账号

更多功能请访问管理平台
        """
        await feishu.send_text(sender_id, help_text)
    
    elif cmd == "/status":
        # 查询健康状态
        # TODO: 根据绑定的患者查询状态
        await feishu.send_text(sender_id, "请先使用 /bind 命令绑定患者账号")
    
    elif cmd == "/bind":
        # 绑定患者账号
        parts = command.split()
        if len(parts) > 1:
            patient_id = parts[1]
            # TODO: 实现绑定逻辑
            await feishu.send_text(sender_id, f"绑定患者 {patient_id} 成功！")
        else:
            await feishu.send_text(sender_id, "用法: /bind <患者ID>")

async def handle_card_action(event: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """处理卡片按钮点击事件"""
    
    action = event.get("action", {})
    value = json.loads(action.get("value", "{}"))
    user_id = event.get("operator", {}).get("open_id", {})
    
    action_type = value.get("action")
    
    if action_type == "medication_taken":
        # 确认服药
        # TODO: 更新用药记录
        return {
            "toast": {
                "type": "success",
                "content": "已确认服药！"
            }
        }
    
    return {"code": 0}

@router.post("/send-test", summary="发送测试消息")
async def send_test_message(
    receive_id: str,
    message: str = "这是一条测试消息",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送测试消息"""
    
    try:
        result = await feishu.send_text(receive_id, message)
        return {
            "success": True,
            "message": "消息发送成功",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-card", summary="发送卡片消息")
async def send_card_message(
    receive_id: str,
    card_type: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送卡片消息"""
    
    try:
        if card_type == "health_alert":
            card = feishu.create_health_alert_card(
                title=data.get("title", "健康预警"),
                alert_type=data.get("alert_type", "未知"),
                value=data.get("value", "--"),
                threshold=data.get("threshold", "--"),
                patient_name=data.get("patient_name", "--"),
                timestamp=data.get("timestamp", "--")
            )
        elif card_type == "medication_reminder":
            card = feishu.create_medication_reminder_card(
                medication_name=data.get("medication_name", "--"),
                dosage=data.get("dosage", "--"),
                patient_name=data.get("patient_name", "--"),
                scheduled_time=data.get("scheduled_time", "--")
            )
        elif card_type == "appointment_reminder":
            card = feishu.create_appointment_reminder_card(
                patient_name=data.get("patient_name", "--"),
                department=data.get("department", "--"),
                doctor_name=data.get("doctor_name", "--"),
                appointment_time=data.get("appointment_time", "--"),
                appointment_no=data.get("appointment_no", "--")
            )
        else:
            raise HTTPException(status_code=400, detail="不支持的卡片类型")
        
        result = await feishu.send_message(receive_id, card, "interactive")
        
        return {
            "success": True,
            "message": "卡片消息发送成功",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-binding", summary="获取用户绑定信息")
async def get_user_binding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的飞书绑定信息"""
    
    # TODO: 从数据库获取绑定信息
    
    return {
        "bound": False,
        "feishu_user_id": None,
        "feishu_open_id": None
    }

@router.post("/user-binding", summary="绑定飞书账号")
async def bind_feishu_account(
    feishu_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """绑定飞书账号"""
    
    # TODO: 保存绑定信息到数据库
    
    return {
        "success": True,
        "message": "飞书账号绑定成功"
    }