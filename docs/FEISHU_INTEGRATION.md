# HealthGuard OPC 飞书集成指南

## 功能概述

飞书集成可以实现以下功能：

1. **健康预警通知** - 异常数据自动推送到飞书
2. **用药提醒** - 定时提醒患者服药
3. **预约提醒** - 预约前自动通知
4. **周报推送** - 每周健康报告自动发送
5. **设备告警** - 设备离线/异常通知
6. **机器人交互** - 通过飞书查询健康信息

## 配置步骤

### 1. 创建飞书应用

1. 访问飞书开放平台: https://open.feishu.cn/
2. 登录后点击「创建企业自建应用」
3. 填写应用信息：
   - 应用名称: `HealthGuard OPC 健康管理`
   - 应用描述: `门诊健康管理平台通知系统`

### 2. 获取凭证

创建完成后，在「凭证与基础信息」页面获取：
- **App ID** (格式: cli_xxxxxxxxxxxxxxxx)
- **App Secret**

### 3. 配置应用权限

进入「权限管理」，开通以下权限：

| 权限 | 说明 |
|-----|------|
| `im:message` | 发送/接收消息 |
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:resource` | 接收图片/文件 |
| `contact:user.id:readonly` | 获取用户信息 |

### 4. 开启机器人能力

进入「应用能力」>「机器人」：
1. 开启机器人能力
2. 记录机器人的 webhook URL（可选）

### 5. 配置事件订阅

进入「事件与回调」：
1. 添加事件回调 URL: `https://your-domain.com/api/feishu/webhook`
2. 订阅以下事件：
   - `im.message.receive_v1` - 接收消息
   - `card.action.trigger` - 卡片按钮点击

### 6. 配置环境变量

在 `.env` 文件中添加：

```bash
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=your-feishu-app-secret
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
```

### 7. 安装应用

1. 进入「版本管理与发布」
2. 创建版本并提交审核
3. 管理员审核通过后，应用生效

## 消息类型

### 1. 健康预警卡片

```json
{
  "title": "⚠️ 血压偏高预警",
  "alert_type": "血压",
  "value": "150/95 mmHg",
  "threshold": "140/90 mmHg",
  "patient_name": "张三"
}
```

### 2. 用药提醒卡片

```json
{
  "medication_name": "氨氯地平",
  "dosage": "5mg",
  "patient_name": "张三",
  "scheduled_time": "08:00"
}
```

### 3. 预约提醒卡片

```json
{
  "patient_name": "张三",
  "department": "心血管科",
  "doctor_name": "李医生",
  "appointment_time": "2024-01-15 10:00",
  "appointment_no": "APT20240115001"
}
```

### 4. 周报卡片

```json
{
  "patient_name": "张三",
  "bp_status": "normal",
  "bp_value": "120/80 mmHg",
  "bs_status": "normal",
  "bs_value": "5.6 mmol/L",
  "adherence": 92,
  "recommendations": ["继续保持良好生活习惯", "定期监测血压"]
}
```

## API 接口

### 检查连接状态

```http
GET /api/feishu/status
```

### 发送测试消息

```http
POST /api/feishu/send-test
Content-Type: application/json

{
  "receive_id": "ou_xxxxxxxxxxxxxxxx",
  "message": "这是一条测试消息"
}
```

### 发送卡片消息

```http
POST /api/feishu/send-card
Content-Type: application/json

{
  "receive_id": "ou_xxxxxxxxxxxxxxxx",
  "card_type": "health_alert",
  "data": {
    "title": "血压偏高预警",
    "alert_type": "血压",
    "value": "150/95 mmHg",
    "threshold": "140/90 mmHg",
    "patient_name": "张三"
  }
}
```

### 绑定飞书账号

```http
POST /api/feishu/user-binding
Content-Type: application/json

{
  "feishu_user_id": "ou_xxxxxxxxxxxxxxxx"
}
```

## 机器人命令

在飞书中发送以下命令给机器人：

| 命令 | 说明 |
|-----|------|
| `/help` | 显示帮助信息 |
| `/status` | 查看健康状态 |
| `/today` | 查看今日提醒 |
| `/weekly` | 获取周报 |
| /bind <患者ID> | 绑定患者账号 |

## 注意事项

1. **安全性**: 不要将 App Secret 提交到代码仓库
2. **权限控制**: 建议配置 `FEISHU_ALLOWED_USERS` 限制使用范围
3. **消息频率**: 注意飞书 API 的频率限制
4. **HTTPS**: 生产环境必须使用 HTTPS

## 故障排查

| 问题 | 解决方案 |
|-----|---------|
| 消息发送失败 | 检查 App ID/Secret 是否正确 |
| 机器人不响应 | 检查事件订阅和回调 URL |
| 权限不足 | 检查应用权限配置 |
| 用户收不到消息 | 检查用户 ID 是否正确 |

## 扩展功能

### 自定义通知模板

可以通过修改 `feishu_service.py` 中的卡片模板来自定义通知样式。

### 集成飞书审批

可以集成飞书审批流程，用于：
- 药物处方审批
- 预约确认审批
- 设备采购审批

### 飞书日历集成

可以将预约同步到飞书日历：
- 自动创建日程
- 日程提醒
- 冲突检测