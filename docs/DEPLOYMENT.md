# 部署指南

## 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (可选)

## 快速部署 (Docker)

### 1. 克隆项目
```bash
git clone https://github.com/your-username/healthguard-opc.git
cd healthguard-opc
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库密码、JWT 密钥等
```

### 3. 启动服务
```bash
docker-compose up -d
```

### 4. 访问应用
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

## 手动部署

### 后端部署

#### 1. 安装依赖
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. 配置数据库
```bash
# 创建 PostgreSQL 数据库
createdb healthguard_opc

# 配置连接字符串
export DATABASE_URL=postgresql://user:password@localhost:5432/healthguard_opc
```

#### 3. 运行数据库迁移
```bash
alembic upgrade head
```

#### 4. 启动后端服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端部署

#### 1. 安装依赖
```bash
cd frontend
npm install
```

#### 2. 构建生产版本
```bash
npm run build
```

#### 3. 部署静态文件
将 `build` 目录部署到 Nginx 或其他 Web 服务器。

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /path/to/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 生产环境配置

### 1. 安全配置
- 使用强密码作为 JWT 密钥
- 启用 HTTPS
- 配置防火墙规则
- 定期更新依赖

### 2. 性能优化
- 启用数据库连接池
- 配置 Redis 缓存
- 使用 CDN 加速静态资源
- 启用 Gzip 压缩

### 3. 监控配置
- 配置日志收集
- 设置性能监控
- 配置告警通知

### 4. 备份策略
- 定期备份数据库
- 备份用户上传的文件
- 测试恢复流程

## 故障排除

### 常见问题

#### 1. 数据库连接失败
检查数据库服务是否运行，连接字符串是否正确。

#### 2. 端口被占用
```bash
# 查看端口占用
lsof -i :8000
# 杀死进程
kill -9 <PID>
```

#### 3. 权限问题
确保上传目录有正确的读写权限。

## 扩展部署

### Kubernetes 部署
参考 `k8s/` 目录下的配置文件。

### 云服务部署
- AWS: 使用 ECS 或 EKS
- 阿里云: 使用 ACK
- 腾讯云: 使用 TKE

## 技术支持

如有部署问题，请通过以下方式获取帮助：
- 创建 GitHub Issue
- 发送邮件至: support@example.com