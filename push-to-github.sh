#!/bin/bash

# HealthGuard OPC GitHub 推送脚本
# 使用方法: ./push-to-github.sh <your-github-username> [repo-name]

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "❌ 请提供 GitHub 用户名"
    echo "使用方法: ./push-to-github.sh <your-github-username> [repo-name]"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME=${2:-healthguard-opc}

echo "🚀 开始推送 HealthGuard OPC 到 GitHub..."
echo "   用户名: $GITHUB_USERNAME"
echo "   仓库名: $REPO_NAME"
echo ""

# 检查是否已安装 gh CLI
if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI (gh) 未安装"
    echo "请安装 GitHub CLI: https://cli.github.com/"
    echo ""
    echo "或者手动创建仓库并推送："
    echo "1. 访问 https://github.com/new"
    echo "2. 创建仓库: $REPO_NAME"
    echo "3. 运行以下命令："
    echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "🔐 请先登录 GitHub CLI"
    echo "运行: gh auth login"
    exit 1
fi

# 检查是否已初始化 git
if [ ! -d ".git" ]; then
    echo "📁 初始化 Git 仓库..."
    git init
    git add .
    git commit -m "Initial commit: HealthGuard OPC - 门诊人群健康管理平台"
fi

# 创建 GitHub 仓库
echo "📦 创建 GitHub 仓库..."
gh repo create "$REPO_NAME" --public --source=. --remote=origin --push

echo ""
echo "✅ 成功推送到 GitHub!"
echo "🔗 仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "📋 后续步骤："
echo "1. 访问仓库设置页面"
echo "2. 添加仓库描述和主题标签"
echo "3. 配置 GitHub Actions（可选）"
echo "4. 邀请协作者（如需要）"
echo ""
echo "🎉 项目已成功部署到 GitHub！"