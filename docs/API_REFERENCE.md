# HealthGuard OPC API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Bearer Token (JWT)
- **API 文档**: http://localhost:8000/docs

## 认证接口

### 登录
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin123
```

**响应**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

### 注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "patient001",
  "email": "patient@example.com",
  "password": "password123",
  "full_name": "张三",
  "role": "patient"
}
```

## 患者管理

### 获取患者列表
```http
GET /api/patients/?skip=0&limit=20
Authorization: Bearer {token}
```

### 获取患者详情
```http
GET /api/patients/{patient_id}
Authorization: Bearer {token}
```

### 创建患者档案
```http
POST /api/patients/
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 1,
  "patient_no": "P20240001",
  "gender": "男",
  "date_of_birth": "1990-01-01"
}
```

## 健康监测

### 记录血压
```http
POST /api/health/blood-pressure
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "systolic": 120,
  "diastolic": 80,
  "pulse": 72,
  "notes": "早晨空腹测量"
}
```

### 记录血糖
```http
POST /api/health/blood-sugar
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "value": 5.6,
  "measurement_time": "fasting",
  "notes": "空腹血糖"
}
```

### 记录心率
```http
POST /api/health/heart-rate
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "bpm": 72,
  "is_resting": true
}
```

### 获取健康记录
```http
GET /api/health/records/{patient_id}?record_type=blood_pressure&days=30
Authorization: Bearer {token}
```

### 获取健康统计
```http
GET /api/health/statistics/{patient_id}?days=30
Authorization: Bearer {token}
```

## 预约管理

### 获取预约列表
```http
GET /api/appointments/?status=pending&days=7
Authorization: Bearer {token}
```

### 创建预约
```http
POST /api/appointments/
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2024-01-15 10:00",
  "department": "内科",
  "appointment_type": "复诊",
  "reason": "血压复查"
}
```

### 更新预约状态
```http
PUT /api/appointments/{appointment_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "new_status": "confirmed"
}
```

### 获取可预约时段
```http
GET /api/appointments/available-slots?doctor_id=2&date=2024-01-15
Authorization: Bearer {token}
```

## 用药管理

### 获取患者用药
```http
GET /api/medications/patient/{patient_id}?active_only=true
Authorization: Bearer {token}
```

### 添加用药记录
```http
POST /api/medications/
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "medication_name": "氨氯地平",
  "dosage": "5mg",
  "frequency": "每日1次",
  "route": "口服",
  "instructions": "早餐后服用"
}
```

### 获取用药提醒
```http
GET /api/medications/reminders/{patient_id}?days=1
Authorization: Bearer {token}
```

### 确认用药
```http
PUT /api/medications/reminder/{reminder_id}/acknowledge
Authorization: Bearer {token}
```

## 设备管理

### 注册设备
```http
POST /api/devices/register
Authorization: Bearer {token}
Content-Type: application/json

{
  "device_sn": "BP2024001",
  "device_name": "客厅血压计",
  "device_type": "blood_pressure",
  "connection_type": "bluetooth",
  "connection_config": {
    "mac_address": "AA:BB:CC:DD:EE:FF"
  },
  "patient_id": 1,
  "brand": "欧姆龙",
  "model": "HEM-7130"
}
```

### 连接设备
```http
POST /api/devices/{device_id}/connect
Authorization: Bearer {token}
```

### 采集数据
```http
POST /api/devices/{device_id}/collect
Authorization: Bearer {token}
```

### 获取设备历史
```http
GET /api/devices/{device_id}/history?days=7&limit=100
Authorization: Bearer {token}
```

### 同步所有设备
```http
POST /api/devices/patient/{patient_id}/sync
Authorization: Bearer {token}
```

## 通知管理

### 获取通知列表
```http
GET /api/notifications/?unread_only=false&limit=50
Authorization: Bearer {token}
```

### 获取未读数量
```http
GET /api/notifications/unread-count
Authorization: Bearer {token}
```

### 标记已读
```http
PUT /api/notifications/{notification_id}/read
Authorization: Bearer {token}
```

### 全部已读
```http
PUT /api/notifications/read-all
Authorization: Bearer {token}
```

### 删除通知
```http
DELETE /api/notifications/{notification_id}
Authorization: Bearer {token}
```

## 健康报告

### 生成周报
```http
GET /api/reports/patient/{patient_id}/weekly
Authorization: Bearer {token}
```

### 生成月报
```http
GET /api/reports/patient/{patient_id}/monthly
Authorization: Bearer {token}
```

### 获取健康摘要
```http
GET /api/reports/patient/{patient_id}/summary
Authorization: Bearer {token}
```

## 数据导出

### 导出健康记录
```http
GET /api/export/health-records/{patient_id}?format=csv&days=30
Authorization: Bearer {token}
```

### 导出用药记录
```http
GET /api/export/medications/{patient_id}?format=csv
Authorization: Bearer {token}
```

### 导出预约记录
```http
GET /api/export/appointments/{patient_id}?format=csv&days=90
Authorization: Bearer {token}
```

### 导出设备数据
```http
GET /api/export/device-data/{device_id}?format=json&days=7
Authorization: Bearer {token}
```

### 导出患者摘要
```http
GET /api/export/patient-summary/{patient_id}?format=csv
Authorization: Bearer {token}
```

## 仪表盘

### 患者仪表盘
```http
GET /api/dashboard/patient/{patient_id}
Authorization: Bearer {token}
```

### 医生仪表盘
```http
GET /api/dashboard/doctor
Authorization: Bearer {token}
```

### 管理员仪表盘
```http
GET /api/dashboard/admin
Authorization: Bearer {token}
```

## 系统管理

### 健康检查
```http
GET /api/system/health
```

### 详细健康检查
```http
GET /api/system/health/detailed
Authorization: Bearer {token}
```

### 系统信息
```http
GET /api/system/info
```

### 系统统计
```http
GET /api/system/stats
Authorization: Bearer {token}
```

## 错误码

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 500 | 服务器内部错误 |

## 分页

列表接口支持分页参数:
- `skip`: 跳过条数 (默认 0)
- `limit`: 返回条数 (默认 20, 最大 100)

## 时间格式

所有时间字段使用 ISO 8601 格式:
```
2024-01-15T10:30:00+08:00
```

或简化格式:
```
2024-01-15 10:30
```