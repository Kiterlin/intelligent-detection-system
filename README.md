# 水下目标智能检测平台

企业级的水下目标智能检测平台，采用前后端分离架构，提供多用户、可管理的 AI 检测服务。

## 项目架构

- **后端**: FastAPI + SQLAlchemy + PostgreSQL/SQLite + Celery + Redis
- **前端**: Vue 3 + Element Plus + Vite
- **AI**: YOLOv5-v8 目标检测模型

## 功能特性

### 用户端
- 智能检测（图片/视频）
- 检测历史管理
- 个人中心

### 管理后台
- 用户管理
- 模型管理
- 仪表盘统计
- 全局检测历史

## 快速开始

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 文档

- [项目结构说明](Files/PROJECT_STRUCTURE.md)
- [开发计划](Files/DEVELOPMENT_PLAN.md)
- [技术栈详情](Files/TECH_STACK.md)
- [实施计划](IMPLEMENTATION_PLAN.md)

## 开发进度

当前阶段：**第一阶段 - 基础架构与认证系统**

查看 [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) 了解详细进度。

## 许可证

MIT License
