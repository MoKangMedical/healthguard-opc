# HealthGuard OPC - GitHub 部署说明

## 项目已准备就绪！ ✅

项目已经完成初始化，所有代码已提交到本地 Git 仓库。

## 推送到 GitHub 的步骤

### 方法 1: 使用 GitHub CLI (推荐)

1. 安装 GitHub CLI (如果未安装):
   ```bash
   # macOS
   brew install gh
   
   # 或访问 https://cli.github.com/ 下载
   ```

2. 登录 GitHub:
   ```bash
   gh auth login
   ```

3. 创建仓库并推送:
   ```bash
   cd ~/healthguard-opc
   gh repo create healthguard-opc --public --source=. --remote=origin --push
   ```

### 方法 2: 手动创建仓库

1. 访问 https://github.com/new

2. 创建新仓库:
   - Repository name: `healthguard-opc`
   - Description: `门诊人群健康管理平台 - Outpatient Care Health Management Platform`
   - 选择 Public 或 Private
   - 不要勾选 "Add a README file"（我们已经有了）

3. 推送代码:
   ```bash
   cd ~/healthguard-opc
   git remote add origin https://github.com/YOUR_USERNAME/healthguard-opc.git
   git push -u origin main
   ```

## 项目结构

```
healthguard-opc/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── models/      # 数据模型
│   │   ├── routes/      # API 路由
│   │   ├── services/    # 业务逻辑
│   │   └── main.py      # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React 前端
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── pages/       # 页面
│   │   ├── services/    # API 服务
│   │   └── store/       # Redux 状态管理
│   └── package.json
├── docs/                # 文档
├── docker-compose.yml   # Docker 配置
├── .env.example         # 环境变量示例
├── start.sh             # 启动脚本
└── README.md            # 项目说明
```

## 功能特性

### 后端 API
- ✅ 用户认证 (JWT)
- ✅ 患者管理
- ✅ 健康记录 (血压、血糖、心率、体重)
- ✅ 预约管理
- ✅ 用药管理
- ✅ 仪表盘统计

### 前端界面
- ✅ 登录/注册页面
- ✅ 仪表盘
- ✅ 患者管理 (基础)
- ✅ 健康监测 (基础)
- ✅ 预约管理 (基础)
- ✅ 用药管理 (基础)

## 快速启动

### 使用 Docker (推荐)
```bash
cd healthguard-opc
./start.sh
```

### 手动启动
```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm start
```

## 访问地址

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 下一步

1. 推送到 GitHub
2. 配置 GitHub Actions (CI/CD)
3. 添加更多功能
4. 部署到生产环境

---

**祝你使用愉快！🎉**