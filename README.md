# 水下目标智能检测平台

> 企业级AI检测应用 · 前后端分离架构 · 多用户管理 · YOLO目标检测

[![开发阶段](https://img.shields.io/badge/开发阶段-Phase%202%20完成-success)](./docs/已完成阶段/)
[![后端](https://img.shields.io/badge/后端-FastAPI-009688)](./backend/)
[![前端](https://img.shields.io/badge/前端-Vue%203-42b983)](./frontend/)
[![AI模型](https://img.shields.io/badge/AI-YOLO-ff6b6b)](./docs/规划文档/)

---

## 📋 项目简介

**水下目标智能检测平台**是一个功能完善的企业级AI检测应用，提供图片和视频的目标检测服务。系统采用前后端分离架构，支持多用户、角色权限管理、模型管理和检测历史追踪。

### 核心特性

✅ **用户认证系统** - JWT Token、角色权限、密码加密
✅ **管理后台** - 用户管理、模型管理、数据可视化
🔄 **AI检测核心** - 图片/视频检测（开发中）
🔄 **用户检测界面** - 在线检测、历史记录（规划中）

---

## 🎯 当前状态

**最新版本**: v0.2
**当前阶段**: Phase 2 已完成 ✅
**更新日期**: 2025-11-12

### 开发进度

```
✅ Phase 1: 用户认证系统        (已完成 - 2025-11-12)
✅ Phase 2: 管理后台功能        (已完成 - 2025-11-12)
⏳ Phase 3: AI检测核心          (计划中)
📅 Phase 4: 用户检测界面        (待启动)
📅 Phase 5: 系统优化与部署      (待启动)
```

详细状态：[项目当前状态](./docs/当前状态/项目状态.md)

---

## ✨ 已完成功能

### Phase 1: 用户认证系统

**后端功能**:
- ✅ JWT Token 认证机制
- ✅ 用户注册、登录、密码修改
- ✅ 基于角色的访问控制 (user/admin)
- ✅ SQLAlchemy 2.0 异步ORM
- ✅ Alembic 数据库迁移

**前端功能**:
- ✅ 登录 / 注册页面
- ✅ 用户首页和个人中心
- ✅ 路由守卫和权限验证
- ✅ Pinia 状态管理

### Phase 2: 管理后台系统

**后端功能**:
- ✅ 用户管理完整 CRUD
- ✅ 用户搜索、筛选、批量操作
- ✅ 模型文件上传 (.pt/.pth)
- ✅ 模型状态管理（激活/停用）
- ✅ 异步文件处理
- ✅ 静态文件服务

**前端功能**:
- ✅ 管理后台布局（侧边栏导航）
- ✅ Dashboard 仪表盘（统计卡片 + ECharts图表）
- ✅ 用户管理界面（表格、搜索、编辑）
- ✅ 模型管理界面（拖拽上传、状态切换）

**API端点**: 13个管理接口（用户管理7个 + 模型管理6个）

详细报告：
- [Phase 1 完成报告](./docs/已完成阶段/Phase1-认证系统.md)
- [Phase 2 完成报告](./docs/已完成阶段/Phase2-管理后台.md)

---

## 🛠 技术栈

### 后端技术
- **框架**: FastAPI 0.104+
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **ORM**: SQLAlchemy 2.0 (异步)
- **认证**: JWT + Bcrypt
- **迁移**: Alembic
- **验证**: Pydantic v2
- **文件**: aiofiles

### 前端技术
- **框架**: Vue 3.3+ (Composition API)
- **构建**: Vite 5.0+
- **UI库**: Element Plus 2.4+
- **状态**: Pinia 2.1+
- **路由**: Vue Router 4.2+
- **HTTP**: Axios 1.6+
- **图表**: ECharts + vue-echarts

### AI技术 (规划中)
- **模型**: YOLO v5-v8
- **深度学习**: PyTorch
- **任务队列**: Celery + Redis
- **图像处理**: OpenCV

查看完整技术栈：[技术栈说明](./docs/技术参考/技术栈说明.md)

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- SQLite (或 PostgreSQL)

### 1. 克隆项目

```bash
git clone <repository-url>
cd project
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**后端访问地址**:
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**前端访问地址**:
- 应用首页: http://localhost:5173
- 登录页面: http://localhost:5173/login
- 管理后台: http://localhost:5173/admin/dashboard

### 4. 创建管理员账号

首先注册一个普通用户，然后在数据库中将其升级为管理员：

```bash
# 连接到数据库
sqlite3 backend/water_detection.db

# 更新用户角色为管理员
UPDATE users SET role = 'admin' WHERE username = 'your_username';

# 退出
.exit
```

---

## 📁 项目结构

```
project/
├── backend/                # 后端项目
│   ├── app/
│   │   ├── api/v1/        # API 路由
│   │   ├── core/          # 核心模块（配置、数据库、安全）
│   │   ├── crud/          # 数据库操作
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── utils/         # 工具函数
│   │   └── main.py        # 应用入口
│   ├── alembic/           # 数据库迁移
│   ├── uploads/           # 文件上传目录
│   └── requirements.txt
│
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── api/          # API 接口
│   │   ├── layouts/      # 布局组件
│   │   ├── views/        # 页面组件
│   │   ├── stores/       # Pinia 状态
│   │   ├── router/       # 路由配置
│   │   └── utils/        # 工具函数
│   └── package.json
│
├── docs/                  # 项目文档
│   ├── 规划文档/         # 原始需求和设计
│   ├── 已完成阶段/       # Phase 完成报告
│   ├── 当前状态/         # 项目现状和下一步
│   └── 技术参考/         # 技术栈和架构
│
├── .gitignore
├── README.md             # 本文件
└── CLAUDE.md             # 开发指南
```

完整结构说明：[项目结构文档](./docs/技术参考/项目结构.md)

---

## 📚 文档导航

### 规划文档
- [项目初步计划与选型](./docs/规划文档/项目初步计划与选型.md)
- [开发路线图](./docs/规划文档/开发路线图.md)
- [实施方案](./docs/规划文档/实施方案.md)
- [前端组件化设计](./docs/规划文档/前端组件化设计.md)
- [后端设计参考](./docs/规划文档/后端设计参考.md)

### 已完成阶段
- [Phase 1: 认证系统完成报告](./docs/已完成阶段/Phase1-认证系统.md)
- [Phase 2: 管理后台完成报告](./docs/已完成阶段/Phase2-管理后台.md)

### 当前状态
- [项目当前状态](./docs/当前状态/项目状态.md) ⭐
- [下一步开发计划](./docs/当前状态/下一步计划.md) ⭐

### 技术参考
- [技术栈详细说明](./docs/技术参考/技术栈说明.md)
- [项目结构说明](./docs/技术参考/项目结构.md)

---

## 🔜 下一步计划

### Phase 3: AI检测核心（开发中）

**目标**: 实现YOLO模型集成和图片/视频检测功能

**主要任务**:
1. ✅ YOLO 模型加载器
2. ✅ 图片检测 API
3. ✅ 视频异步检测（Celery + Redis）
4. ✅ 检测结果存储和可视化
5. ✅ 检测历史管理

**预计时间**: 2-3周

详细计划：[Phase 3 开发计划](./docs/当前状态/下一步计划.md)

---

## 🧪 测试

### 后端测试

```bash
cd backend
source venv/bin/activate
pytest
```

### 前端测试

```bash
cd frontend
npm run test
```

---

## 📊 代码统计

- **Git 提交**: 7次
- **总代码量**: ~5,100行
  - 后端: ~2,500行
  - 前端: ~2,600行
- **API 端点**: 17个
- **数据库表**: 2个 (users, ml_models)

---

## ⚠️ 已知问题

1. **数据库**: 开发环境使用SQLite，生产环境需切换到PostgreSQL
2. **Token刷新**: 未实现自动刷新Token机制
3. **文件上传**: 大文件上传未实现分片
4. **测试覆盖**: 缺少自动化测试
5. **AI功能**: 核心检测功能尚未实现

详细信息：[项目状态 - 已知问题](./docs/当前状态/项目状态.md#已知问题)

---

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

请遵循 [CLAUDE.md](./CLAUDE.md) 中的开发规范。

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

如有问题或建议，请：
- 提交 Issue
- 创建 Pull Request
- 查阅 [项目文档](./docs/)

---

**项目开发**: Claude Code + 用户协作
**最后更新**: 2025-11-12
