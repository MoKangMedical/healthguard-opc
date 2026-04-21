# HealthGuard OPC - 门诊人群健康管理平台

HealthGuard OPC 是一个面向门诊患者（OPC - Outpatient Care）的综合健康管理平台，帮助患者和医护人员更好地管理健康数据、预约和治疗计划。

## 功能特性

### 🏥 核心功能
- **患者管理** - 完整的患者档案管理
- **健康监测** - 血压、血糖、心率、体重等指标追踪
- **慢性病管理** - 糖尿病、高血压等慢性病专项管理
- **预约系统** - 门诊预约和提醒
- **用药管理** - 药物提醒和用药记录
- **数据可视化** - 健康趋势图表分析

### 📱 用户端功能
- 个人健康仪表盘
- 健康数据录入
- 预约管理
- 用药提醒
- 健康报告查看

### 👨‍⚕️ 医护端功能
- 患者管理
- 健康数据监控
- 异常预警
- 治疗计划制定
- 统计报表

## 技术架构

### 后端 (Backend)
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL + Redis
- **认证**: JWT Token
- **API**: RESTful API

### 前端 (Frontend)
- **框架**: React 18 + TypeScript
- **UI库**: Ant Design
- **图表**: ECharts / Recharts
- **状态管理**: Redux Toolkit

### 部署
- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **部署**: 云服务器 / Kubernetes

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/MoKangMedical/healthguard-opc.git
cd healthguard-opc
```

### 2. 后端启动
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. 前端启动
```bash
cd frontend
npm install
npm start
```

### 4. Docker 启动（推荐）
```bash
docker-compose up -d
```

## 项目结构

```
healthguard-opc/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── models/      # 数据模型
│   │   ├── routes/      # API 路由
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试
│   └── requirements.txt
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   └── services/    # API 服务
│   └── public/
├── docs/                # 文档
├── scripts/             # 脚本工具
└── docker-compose.yml   # Docker 配置
```

## 贡献指南

欢迎贡献！请阅读 [贡献指南](docs/CONTRIBUTING.md)。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE)

## 联系方式

- 项目地址: https://github.com/MoKangMedical/healthguard-opc
- 问题反馈: https://github.com/MoKangMedical/healthguard-opc/issues

---

**HealthGuard OPC** - 让健康管理更简单、更智能 🏥💚
## 📐 理论基础

> **Harness理论**：在AI领域，Harness（环境设计）比模型本身更重要。优秀的Harness设计能使性能提升64%。

> **红杉论点**：从卖工具到卖结果。
