# 贡献指南

感谢您对 HealthGuard OPC 项目的关注！我们欢迎所有形式的贡献。

## 如何贡献

### 1. 报告问题

如果您发现了 bug 或有功能建议，请创建一个 Issue：

1. 访问 [Issues](https://github.com/your-username/healthguard-opc/issues)
2. 点击 "New Issue"
3. 选择适当的模板
4. 提供详细的描述

### 2. 提交代码

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add your feature'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 创建 Pull Request

### 3. 开发规范

#### 代码风格
- Python: 使用 Black 格式化，遵循 PEP 8
- TypeScript: 使用 ESLint 和 Prettier
- 提交前运行 linting

#### 提交信息
使用语义化提交信息：
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

#### 分支命名
- `feature/` 新功能
- `bugfix/` Bug 修复
- `hotfix/` 紧急修复
- `release/` 版本发布

### 4. 开发环境设置

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

#### 前端
```bash
cd frontend
npm install
```

#### 数据库
```bash
docker-compose up -d postgres redis
```

### 5. 测试

运行测试：
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

### 6. 代码审查

所有 PR 都需要经过代码审查：
- 至少 1 个批准
- 所有 CI 检查通过
- 代码符合项目规范

## 行为准则

请遵循 [Contributor Covenant](https://www.contributor-covenant.org/) 行为准则。

## 联系方式

如有疑问，请通过以下方式联系：
- 创建 Issue
- 发送邮件至: [your-email@example.com]

感谢您的贡献！🎉