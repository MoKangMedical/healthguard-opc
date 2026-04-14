"""
通知路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services.auth import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/", summary="获取通知列表")
async def get_notifications(
    unread_only: bool = False,
    notification_type: Optional[NotificationType] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的通知列表"""
    service = NotificationService(db)
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        notification_type=notification_type,
        limit=limit
    )
    
    return {
        "total": len(notifications),
        "unread_count": service.get_unread_count(current_user.id),
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "content": n.content,
                "type": n.notification_type.value,
                "priority": n.priority.value,
                "is_read": n.is_read,
                "related_type": n.related_type,
                "related_id": n.related_id,
                "created_at": n.created_at,
                "read_at": n.read_at,
            }
            for n in notifications
        ]
    }

@router.get("/unread-count", summary="获取未读通知数量")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取未读通知数量"""
    service = NotificationService(db)
    count = service.get_unread_count(current_user.id)
    return {"unread_count": count}

@router.put("/{notification_id}/read", summary="标记通知为已读")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记通知为已读"""
    service = NotificationService(db)
    success = service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    return {"message": "已标记为已读"}

@router.put("/read-all", summary="标记所有通知为已读")
async def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记所有通知为已读"""
    service = NotificationService(db)
    count = service.mark_all_as_read(current_user.id)
    return {"message": f"已标记 {count} 条通知为已读"}

@router.delete("/{notification_id}", summary="删除通知")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除通知"""
    service = NotificationService(db)
    success = service.delete_notification(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="通知不存在")
    
    return {"message": "通知已删除"}

@router.get("/stats", summary="获取通知统计")
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取通知统计"""
    service = NotificationService(db)
    
    # 获取各类通知数量
    all_notifications = service.get_user_notifications(current_user.id, limit=1000)
    
    stats = {
        "total": len(all_notifications),
        "unread": service.get_unread_count(current_user.id),
        "by_type": {},
        "by_priority": {"low": 0, "normal": 0, "high": 0, "urgent": 0}
    }
    
    for n in all_notifications:
        # 按类型统计
        type_key = n.notification_type.value
        stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1
        
        # 按优先级统计
        priority_key = n.priority.value
        if priority_key in stats["by_priority"]:
            stats["by_priority"][priority_key] += 1
    
    return stats