# HealthGuard OPC - 门诊人群健康管理平台

## 项目概述

HealthGuard OPC 是一个面向门诊患者（OPC - Outpatient Care）的综合健康管理平台，支持健康数据监测、设备对接、智能提醒、健康报告等功能。

## 功能架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    HealthGuard OPC 平台                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 患者管理 │  │ 健康监测 │  │ 预约管理 │  │ 用药管理 │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 设备管理 │  │ 通知系统 │  │ 健康报告 │  │ 数据导出 │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        技术架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  前端: React + TypeScript + Ant Design + ECharts                │
│  后端: FastAPI + SQLAlchemy + PostgreSQL + Redis                 │
│  任务: Celery + Redis (定时任务)                                 │
│  设备: BLE + WiFi + API + Gateway (多协议支持)                  │
│  部署: Docker + Docker Compose                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 核心功能

### 1. 用户认证
- JWT Token 认证
- 多角色支持 (患者/医生/护士/管理员)
- 刷新令牌机制

### 2. 患者管理
- 患者档案管理
- 病史记录
- 慢性病标记

### 3. 健康监测
- 血压记录与分析
- 血糖记录与分析
- 心率监测
- 体重/BMI 管理
- 异常值预警

### 4. 预约管理
- 在线预约
- 可用时段查询
- 预约状态管理
- 自动提醒

### 5. 用药管理
- 药物处方记录
- 用药提醒
- 依从性统计
- 剩余量追踪

### 6. 设备管理
- 多类型设备支持
  - 血压计 (欧姆龙、鱼跃等)
  - 血糖仪 (罗氏、强生等)
  - 心率监测 (Fitbit、Garmin等)
  - 体重秤 (小米、华为等)
  - 血氧仪、体温计
- 多连接方式
  - 蓝牙 BLE
  - WiFi
  - API (云平台)
  - 网关
- 自动数据采集
- 数据解析与验证

### 7. 通知系统
- 多渠道通知 (App/短信/邮件/微信)
- 健康预警
- 用药提醒
- 预约提醒
- 设备告警
- 优先级管理

### 8. 健康报告
- 周报/月报生成
- 趋势分析
- 健康评分
- 个性化建议

### 9. 数据导出
- CSV/JSON/Excel 格式
- 健康记录导出
- 用药记录导出
- 设备数据导出

### 10. 定时任务
- 用药提醒 (8:00, 12:00, 20:00)
- 预约提醒 (每日 9:00)
- 设备状态检查 (每小时)
- 周报生成 (每周日)
- 过期数据清理 (每月)

## API 接口一览

| 模块 | 接口数量 | 主要功能 |
|-----|---------|---------|
| 认证 | 4 | 登录/注册/刷新/用户信息 |
| 患者 | 5 | CRUD/列表 |
| 健康 | 8 | 记录/统计/趋势 |
| 预约 | 6 | CRUD/可用时段 |
| 用药 | 6 | CRUD/提醒/确认 |
| 设备 | 8 | 注册/连接/采集/同步 |
| 通知 | 5 | 列表/已读/删除 |
| 报告 | 3 | 周报/月报/摘要 |
| 导出 | 6 | 多格式导出 |
| 系统 | 4 | 健康检查/统计 |

## 数据模型

```
User (用户)
├── Patient (患者)
│   ├── HealthRecord (健康记录)
│   │   ├── BloodPressure (血压)
│   │   ├── BloodSugar (血糖)
│   │   ├── HeartRate (心率)
│   │   └── Weight (体重)
│   ├── Appointment (预约)
│   ├── Medication (用药)
│   │   └── MedicationReminder (用药提醒)
│   └── Device (设备)
│       └── DeviceDataRecord (设备数据)
└── Notification (通知)
```

## 技术栈

### 后端
- **框架**: FastAPI 0.104
- **ORM**: SQLAlchemy 2.0
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **任务队列**: Celery
- **认证**: JWT (python-jose)
- **密码**: bcrypt

### 前端
- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design 5
- **图表**: ECharts
- **状态**: Redux Toolkit
- **路由**: React Router 6

### 设备对接
- **蓝牙**: bleak (BLE)
- **串口**: pyserial
- **IoT**: paho-mqtt

### 部署
- **容器**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/MoKangMedical/healthguard-opc.git
cd healthguard-opc
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 文件
```

### 3. 启动服务
```bash
docker-compose up -d
```

### 4. 访问应用
- 前端: http://localhost:3000
- API: http://localhost:8000
- 文档: http://localhost:8000/docs

## 项目结构

```
healthguard-opc/
├── backend/
│   ├── app/
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API 路由
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── pages/          # 页面
│   │   ├── services/       # API 服务
│   │   └── store/          # 状态管理
│   └── package.json
├── docs/
│   ├── API_REFERENCE.md    # API 文档
│   ├── DEPLOYMENT.md       # 部署文档
│   ├── HARDWARE_INTEGRATION.md
│   └── CONTRIBUTING.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## 开发计划

### 已完成 ✅
- [x] 用户认证系统
- [x] 患者管理
- [x] 健康数据记录
- [x] 预约管理
- [x] 用药管理
- [x] 设备管理
- [x] 通知系统
- [x] 健康报告
- [x] 数据导出
- [x] 定时任务

### 进行中 🚧
- [ ] 前端页面完善
- [ ] 移动端适配
- [ ] 性能优化

### 计划中 📋
- [ ] 微信小程序
- [ ] 家属端管理
- [ ] AI 健康分析
- [ ] 多语言支持
- [ ] 国际化部署

## 贡献指南

请阅读 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/MoKangMedical/healthguard-opc
- Issues: https://github.com/MoKangMedical/healthguard-opc/issues

---

**HealthGuard OPC** - 让健康管理更智能 🏥💚