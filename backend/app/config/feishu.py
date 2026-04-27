"""
飞书集成配置
"""

from pydantic_settings import BaseSettings
import os

class FeishuSettings(BaseSettings):
    """飞书配置"""
    
    # 飞书应用凭证
    FEISHU_APP_ID: str = os.getenv("FEISHU_APP_ID", "")
    FEISHU_APP_SECRET: str = os.getenv("FEISHU_APP_SECRET", "")
    
    # 飞书域名 (feishu 或 lark)
    FEISHU_DOMAIN: str = os.getenv("FEISHU_DOMAIN", "feishu")
    
    # 连接模式
    FEISHU_CONNECTION_MODE: str = os.getenv("FEISHU_CONNECTION_MODE", "websocket")
    
    # 允许的用户 ID 列表 (逗号分隔)
    FEISHU_ALLOWED_USERS: str = os.getenv("FEISHU_ALLOWED_USERS", "")
    
    # 默认通知频道
    FEISHU_HOME_CHANNEL: str = os.getenv("FEISHU_HOME_CHANNEL", "")
    
    # Webhook URL (用于接收事件)
    FEISHU_WEBHOOK_URL: str = os.getenv("FEISHU_WEBHOOK_URL", "")
    
    # 加密密钥 (用于验证事件)
    FEISHU_ENCRYPT_KEY: str = os.getenv("FEISHU_ENCRYPT_KEY", "")
    
    # 验证令牌 (用于验证事件)
    FEISHU_VERIFICATION_TOKEN: str = os.getenv("FEISHU_VERIFICATION_TOKEN", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

feishu_settings = FeishuSettings()