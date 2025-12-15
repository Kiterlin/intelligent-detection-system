# 智能目标检测系统

> 企业级AI检测应用 · 前后端分离架构 · 多用户管理 · YOLO目标检测

[![开发阶段](https://img.shields.io/badge/开发阶段-Phase%204%20完成-success)](docs/第一阶段计划/已完成阶段/)
[![后端](https://img.shields.io/badge/后端-FastAPI-009688)](./backend/)
[![前端](https://img.shields.io/badge/前端-Vue%203-42b983)](./frontend/)
[![AI模型](https://img.shields.io/badge/AI-YOLO-ff6b6b)](./docs/规划文档/)

---

## 🚀 快速开始

### 📖 新用户必读

**第一次使用本项目？** 请按顺序阅读：

1. **[📘 环境配置指南](./ENVIRONMENT_SETUP.md)** ⭐ **首先阅读**
   - 环境要求和安装
   - Conda / venv 两种配置方式
   - 数据库配置和迁移
   - 一键启动脚本
   - 常见问题解决

2. **[📘 项目使用说明](./docs/使用说明.md)** - 详细的功能使用指南
   - 系统功能介绍
   - 首次使用指南（从注册到检测）
   - 各模块使用说明
   - 常见操作流程

### ⚡ 极速启动（已安装依赖）

**使用一键启动脚本（推荐）**:
```bash
# 1. 激活环境
conda activate RSD  # 或 source backend/venv/bin/activate

# 2. 一键启动所有服务
./start.sh
```

**或手动启动各服务**:
```bash
# 终端1: 后端API
cd backend && source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# 终端2: Celery Worker
cd backend && celery -A app.celery_app worker --loglevel=info

# 终端3: 前端
cd frontend && npm run dev
```

**访问地址**:
- 前端应用: http://localhost:5173
- API文档: http://localhost:8000/docs

---

## 📋 项目简介

**智能目标检测系统**是一个功能完善的企业级AI检测应用，提供图片和视频的目标检测服务。系统采用前后端分离架构，支持多用户、角色权限管理、模型管理和检测历史追踪。

### 核心特性

✅ **用户认证系统** - JWT Token、角色权限、密码加密
✅ **管理后台** - 用户管理、模型管理、数据可视化
✅ **AI检测核心** - YOLO模型集成、图片/视频检测、Celery异步任务
✅ **用户检测界面** - 在线检测、实时进度、历史管理（Stage 1-3完成）

---

## 🎯 当前状态

**最新版本**: v0.5
**当前阶段**: Phase 4 已完成 ✅
**更新日期**: 2025-11-12

### 开发进度

```
✅ Phase 1: 用户认证系统        (已完成 - 2025-11-12)
✅ Phase 2: 管理后台功能        (已完成 - 2025-11-12)
✅ Phase 3: AI检测核心          (已完成 - 2025-11-12)
✅ Phase 4: 用户检测界面        (已完成 - 2025-11-12)
  ├─ Stage 1: API集成         ✅
  ├─ Stage 2: 图片检测        ✅
  ├─ Stage 3: 视频+历史       ✅
  ├─ Stage 4: UI/UX优化       ✅
  └─ Stage 5: 代码质量        ✅
📅 Phase 5: 系统优化与部署      (准备启动)
```

详细状态：[项目当前状态](docs/第一阶段计划/当前状态/项目状态.md)

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

### Phase 3: AI检测核心

**后端功能**:
- ✅ YOLO模型加载服务（单例模式）
- ✅ 图片检测API（同步处理）
- ✅ 视频检测API（Celery异步任务）
- ✅ 检测历史记录管理
- ✅ GPU加速支持（CUDA）
- ✅ Redis消息队列
- ✅ 结果可视化（边界框标注）

**API端点**: 8个检测接口（图片/视频检测、历史管理、下载）

### Phase 4: 用户检测界面 (已完成 ✅)

**前端功能**:
- ✅ 检测页面（/detection）
  - 拖拽式文件上传（支持图片和视频）
  - 模型选择和参数配置（含Tooltip说明）
  - 图片检测（同步）+ 视频检测（异步）
  - 实时进度跟踪和状态反馈
  - 结果展示（预览、统计、对象列表）
  - 结果下载功能

- ✅ 历史页面（/detection-history）
  - 分页列表展示
  - 筛选（类型、状态）和批量操作
  - 详情查看和下载

- ✅ UI/UX优化
  - 响应式设计（移动端/平板/桌面）
  - 加载动画和进度条优化
  - 图片/视频懒加载
  - 工具函数库（helpers.js）

- ✅ 代码质量
  - ESLint配置完成
  - 代码规范检查通过
  - .gitignore配置

**新增文件**: 7个核心文件（~1,720行代码）

详细报告：
- [Phase 1 完成报告](docs/第一阶段计划/已完成阶段/Phase1-认证系统.md)
- [Phase 2 完成报告](docs/第一阶段计划/已完成阶段/Phase2-管理后台.md)
- [Phase 3 完成报告](docs/第一阶段计划/已完成阶段/Phase3-AI检测核心.md)
- [Phase 4 Stage 1-3 完成报告](docs/第一阶段计划/已完成阶段/Phase4_Stage1-3_完成报告.md)
- [Phase 4 完成报告](docs/第一阶段计划/已完成阶段/Phase4_完成报告.md) ⭐ **最新**

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

### AI技术
- **模型**: YOLO (Ultralytics)
- **深度学习**: PyTorch 2.1.1+
- **任务队列**: Celery 5.3.4 + Redis
- **图像处理**: OpenCV 4.8.1
- **文件处理**: aiofiles

查看完整技术栈：[技术栈说明](./docs/技术参考/技术栈说明.md)

---

## 🚀 快速开始

> **💡 提示**: 详细的安装和使用说明请查看 [📘 使用说明文档](./docs/使用说明.md)

### 环境要求

- Python 3.11+
- Node.js 18+
- Redis 5.0+ (用于Celery任务队列)
- SQLite (开发) / PostgreSQL (生产)

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
- 检测页面: http://localhost:5173/detection
- 历史页面: http://localhost:5173/detection-history
- 管理后台: http://localhost:5173/admin/dashboard

### 4. 启动Redis和Celery (用于视频检测)

```bash
# 终端3: 启动Redis
redis-server

# 终端4: 启动Celery Worker
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info
```

### 5. 首次使用配置

**创建管理员账号**:
1. 访问 http://localhost:5173/register
2. 注册第一个用户（自动成为管理员）

**上传YOLO模型**:
1. 以管理员身份登录
2. 进入管理后台 → 模型管理
3. 上传YOLO模型文件（.pt或.pth格式）
4. 激活模型以供检测使用

**详细步骤**: 请参考 [使用说明 - 首次使用指南](./docs/使用说明.md#首次使用指南)

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
│   ├── 使用说明.md        # 项目使用指南 ⭐ 新用户必读
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

### 💡 新用户入门
- **[📘 环境配置指南](./ENVIRONMENT_SETUP.md)** ⭐ **首先阅读**
  - 完整的环境配置说明
  - Conda / venv 两种方式
  - 一键启动脚本
  - 常见问题解决

- **[📘 项目使用说明](./docs/使用说明.md)** ⭐ **推荐阅读**
  - 系统功能介绍
  - 首次使用指南
  - 功能使用说明
  - 常见操作流程

### 📋 项目规划
- [项目初步计划与选型](./docs/规划文档/项目初步计划与选型.md)
- [开发路线图](./docs/规划文档/开发路线图.md)
- [前端组件化设计](./docs/规划文档/前端组件化设计.md)
- [后端设计参考](./docs/规划文档/后端设计参考.md)

### ✅ 完成报告
- [Phase 1: 认证系统](docs/第一阶段计划/已完成阶段/Phase1-认证系统.md)
- [Phase 2: 管理后台](docs/第一阶段计划/已完成阶段/Phase2-管理后台.md)
- [Phase 3: AI检测核心](docs/第一阶段计划/已完成阶段/Phase3-AI检测核心.md)
- [Phase 4: 用户检测界面](docs/第一阶段计划/已完成阶段/Phase4_完成报告.md) ⭐ **最新**
- [Phase 5: Stage 2 完成](docs/第一阶段计划/已完成阶段/Phase5_Stage2_完成报告.md)
- [PostgreSQL 迁移完成报告](docs/第一阶段计划/已完成阶段/PostgreSQL_迁移完成报告.md)

### 📊 当前状态
- **[项目当前状态](docs/第一阶段计划/当前状态/项目状态.md)** ⭐ **实时更新**
- **[下一步开发计划](docs/第一阶段计划/当前状态/下一步计划.md)** ⭐
- **[Phase 5 实施计划](docs/第一阶段计划/当前状态/IMPLEMENTATION_PLAN.md)** - 活跃开发计划

### 🔧 技术参考
- [技术栈详细说明](./docs/技术参考/技术栈说明.md)
- [项目结构说明](./docs/技术参考/项目结构.md)
- [PostgreSQL 迁移指南](./backend/POSTGRES_MIGRATION_GUIDE.md)

### 📁 归档文档
旧版本和历史文档已归档至 `docs/归档/` 目录

---

## 🔜 下一步计划

### Phase 5: 系统优化与部署（准备启动）

**目标**: 生产环境部署和系统优化

**主要任务**:
1. 📦 Docker容器化部署
2. 🌐 Nginx反向代理配置
3. 🗄️ PostgreSQL数据库迁移
4. 🚀 性能优化和压力测试
5. 📊 监控和日志系统
6. 🔒 安全加固和审计

**预计时间**: 1-2周

详细计划：[下一步计划](docs/第一阶段计划/当前状态/下一步计划.md)

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

- **Git 提交**: 9次
- **总代码量**: ~22,200行
  - 后端: ~6,800行
  - 前端: ~10,400行 (新增~1,700行)
  - 文档: ~5,000行 (新增~1,500行)
- **API 端点**: 26个 (认证5个 + 用户管理7个 + 模型管理6个 + 检测8个)
- **数据库表**: 3个 (users, ml_models, detection_history)
- **文件数**: ~94个

---

## ⚠️ 待优化项

Phase 4已完成所有基础功能和UI/UX优化，以下是Phase 5的规划：

1. **系统部署**: Docker容器化、Nginx配置、PostgreSQL迁移
2. **性能优化**: 大文件分片上传、虚拟滚动、API缓存
3. **高级功能**: 批量检测、结果对比、导出报告
4. **测试覆盖**: 单元测试、集成测试、E2E测试
5. **监控运维**: 日志系统、性能监控、告警机制

详细信息：[项目状态 - 待优化项](docs/第一阶段计划/当前状态/项目状态.md#待优化项)

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
