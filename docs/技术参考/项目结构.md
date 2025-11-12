# 项目结构说明

> 本文档详细说明水下目标智能检测平台的完整目录结构和文件组织方式。

---

## 总体结构

```
water-target-detection/
├── backend/                 # 后端项目
├── frontend/                # 前端项目
├── docker-compose.yml       # Docker编排配置
├── .env.example            # 环境变量模板
├── .gitignore              # Git忽略文件
└── README.md               # 项目说明文档
```

---

## 后端目录结构

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py
│   ├── main.py                  # FastAPI应用入口
│   ├── config.py                # 配置管理
│   ├── database.py              # 数据库连接
│   ├── dependencies.py          # 依赖注入
│   │
│   ├── api/                     # API路由
│   │   ├── __init__.py
│   │   ├── v1/                  # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── router.py        # 主路由
│   │   │   ├── auth.py          # 认证相关API
│   │   │   ├── users.py         # 用户管理API
│   │   │   ├── admin.py         # 管理员API
│   │   │   ├── models.py        # 模型管理API
│   │   │   ├── detection.py     # 检测API
│   │   │   └── tasks.py         # 任务状态API
│   │   └── deps.py              # API依赖
│   │
│   ├── models/                  # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── ml_model.py          # ML模型模型
│   │   └── detection_history.py # 检测历史模型
│   │
│   ├── schemas/                 # Pydantic模式
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模式
│   │   ├── ml_model.py          # ML模型模式
│   │   ├── detection.py         # 检测模式
│   │   └── token.py             # 令牌模式
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证服务
│   │   ├── user_service.py      # 用户服务
│   │   ├── model_service.py     # 模型加载服务
│   │   ├── detection_service.py # 检测服务
│   │   └── file_service.py      # 文件服务
│   │
│   ├── core/                    # 核心功能
│   │   ├── __init__.py
│   │   ├── security.py          # 安全相关（JWT、密码哈希）
│   │   ├── config.py            # 配置类
│   │   ├── cache.py             # 缓存管理
│   │   └── logging.py           # 日志配置
│   │
│   ├── tasks/                   # Celery任务
│   │   ├── __init__.py
│   │   ├── celery_app.py        # Celery应用
│   │   └── detection_tasks.py   # 检测任务
│   │
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── image.py             # 图像处理工具
│       ├── video.py             # 视频处理工具
│       └── validators.py        # 验证器
│
├── alembic/                     # 数据库迁移
│   ├── versions/                # 迁移脚本
│   ├── env.py
│   └── script.py.mako
│
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── conftest.py              # pytest配置
│   ├── test_auth.py             # 认证测试
│   ├── test_detection.py        # 检测测试
│   └── test_api/                # API测试
│       ├── __init__.py
│       ├── test_auth_api.py
│       ├── test_user_api.py
│       └── test_detection_api.py
│
├── models/                      # YOLO模型文件
│   ├── yolov5s.pt
│   ├── yolov8n.pt
│   └── README.md
│
├── uploads/                     # 用户上传文件
│   ├── images/
│   └── videos/
│
├── results/                     # 检测结果
│   ├── images/
│   └── videos/
│
├── logs/                        # 日志文件
│   └── app_YYYY-MM-DD.log
│
├── requirements.txt             # Python依赖
├── pyproject.toml              # Poetry配置（可选）
├── Dockerfile                   # Docker镜像
├── .env                        # 环境变量（不提交）
├── .env.example                # 环境变量模板
├── alembic.ini                 # Alembic配置
└── README.md                   # 后端说明
```

### 关键文件说明

#### `app/main.py` - 应用入口
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

# 配置日志
setup_logging()

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### `app/config.py` - 配置管理
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Water Target Detection API"
    API_V1_STR: str = "/api/v1"

    # 数据库
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 文件上传
    UPLOAD_DIR: str = "uploads"
    RESULT_DIR: str = "results"
    MODEL_DIR: str = "models"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024  # 500MB

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:5173"]

    class Config:
        env_file = ".env"

settings = Settings()
```

#### `app/database.py` - 数据库连接
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 前端目录结构

```
frontend/
├── public/                      # 静态资源
│   ├── favicon.ico
│   └── logo.png
│
├── src/                         # 源代码
│   ├── assets/                  # 资源文件
│   │   ├── images/
│   │   ├── styles/
│   │   │   ├── main.css
│   │   │   └── variables.css
│   │   └── icons/
│   │
│   ├── components/              # 通用组件
│   │   ├── common/              # 公共组件
│   │   │   ├── Header.vue
│   │   │   ├── Sidebar.vue
│   │   │   ├── Footer.vue
│   │   │   ├── Loading.vue
│   │   │   └── EmptyState.vue
│   │   │
│   │   ├── upload/              # 上传组件
│   │   │   ├── ImageUpload.vue
│   │   │   └── VideoUpload.vue
│   │   │
│   │   ├── detection/           # 检测组件
│   │   │   ├── ResultDisplay.vue
│   │   │   ├── DetectionList.vue
│   │   │   └── ProgressBar.vue
│   │   │
│   │   └── admin/               # 管理组件
│   │       ├── UserTable.vue
│   │       ├── ModelTable.vue
│   │       └── StatCard.vue
│   │
│   ├── views/                   # 页面视图
│   │   ├── auth/                # 认证页面
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   │
│   │   ├── user/                # 用户端页面
│   │   │   ├── Home.vue
│   │   │   ├── Detect.vue
│   │   │   ├── History.vue
│   │   │   ├── VideoResult.vue
│   │   │   └── Profile.vue
│   │   │
│   │   └── admin/               # 管理端页面
│   │       ├── Dashboard.vue
│   │       ├── UserManagement.vue
│   │       └── ModelManagement.vue
│   │
│   ├── layouts/                 # 布局组件
│   │   ├── MainLayout.vue       # 主布局
│   │   ├── AdminLayout.vue      # 管理后台布局
│   │   └── AuthLayout.vue       # 认证页面布局
│   │
│   ├── router/                  # 路由配置
│   │   ├── index.js             # 主路由
│   │   ├── user.js              # 用户路由
│   │   └── admin.js             # 管理员路由
│   │
│   ├── stores/                  # Pinia状态管理
│   │   ├── index.js
│   │   ├── auth.js              # 认证状态
│   │   ├── user.js              # 用户状态
│   │   ├── detection.js         # 检测状态
│   │   └── admin.js             # 管理状态
│   │
│   ├── api/                     # API接口
│   │   ├── index.js
│   │   ├── auth.js              # 认证API
│   │   ├── user.js              # 用户API
│   │   ├── detection.js         # 检测API
│   │   ├── model.js             # 模型API
│   │   └── admin.js             # 管理API
│   │
│   ├── utils/                   # 工具函数
│   │   ├── request.js           # Axios封装
│   │   ├── auth.js              # 认证工具
│   │   ├── validators.js        # 表单验证
│   │   ├── formatters.js        # 格式化工具
│   │   └── constants.js         # 常量定义
│   │
│   ├── composables/             # 组合式函数
│   │   ├── useAuth.js
│   │   ├── useDetection.js
│   │   └── useUpload.js
│   │
│   ├── App.vue                  # 根组件
│   └── main.js                  # 入口文件
│
├── tests/                       # 测试目录
│   ├── unit/                    # 单元测试
│   │   └── components/
│   └── e2e/                     # E2E测试
│       └── specs/
│
├── .vscode/                     # VS Code配置
│   └── settings.json
│
├── index.html                   # HTML模板
├── vite.config.js              # Vite配置
├── package.json                # npm配置
├── package-lock.json
├── .eslintrc.js                # ESLint配置
├── .prettierrc.js              # Prettier配置
├── .gitignore
├── Dockerfile                   # Docker镜像
├── nginx.conf                   # Nginx配置
└── README.md                   # 前端说明
```

### 关键文件说明

#### `src/main.js` - 入口文件
```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

#### `src/router/index.js` - 路由配置
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/user/Home.vue')
      },
      {
        path: 'detect',
        name: 'Detect',
        component: () => import('@/views/user/Detect.vue')
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/user/History.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagement.vue')
      },
      {
        path: 'models',
        name: 'ModelManagement',
        component: () => import('@/views/admin/ModelManagement.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router
```

#### `src/utils/request.js` - Axios封装
```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
```

---

## Docker配置文件

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    container_name: water_detection_db
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-water_detection}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: water_detection_redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  # 后端API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: water_detection_backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-water_detection}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend:/app
      - model_files:/app/models
      - upload_files:/app/uploads
      - result_files:/app/results
      - backend_logs:/app/logs
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: water_detection_celery
    command: celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-postgres}@postgres:5432/${POSTGRES_DB:-water_detection}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend:/app
      - model_files:/app/models
      - upload_files:/app/uploads
      - result_files:/app/results
      - celery_logs:/app/logs
    depends_on:
      - redis
      - postgres
      - backend
    networks:
      - app-network
    restart: unless-stopped

  # 前端应用
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: water_detection_frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - result_files:/usr/share/nginx/html/results:ro
    depends_on:
      - backend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  model_files:
    driver: local
  upload_files:
    driver: local
  result_files:
    driver: local
  backend_logs:
    driver: local
  celery_logs:
    driver: local

networks:
  app-network:
    driver: bridge
```

### `.env.example` - 环境变量模板

```env
# 项目配置
PROJECT_NAME=Water Target Detection API

# 数据库配置
POSTGRES_DB=water_detection
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here

# Redis配置
REDIS_URL=redis://redis:6379/0

# JWT配置
SECRET_KEY=your_secret_key_here_replace_with_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件配置
MAX_UPLOAD_SIZE=524288000  # 500MB

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# 日志配置
LOG_LEVEL=INFO
```

---

## 配置文件

### `backend/requirements.txt`

```txt
# Web框架
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# 认证
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# 任务队列
celery==5.3.4
redis==5.0.1

# AI/ML
torch==2.1.1
torchvision==0.16.1
ultralytics==8.0.220
opencv-python==4.8.1.78
pillow==10.1.0
numpy==1.24.4

# 工具
python-dotenv==1.0.0
aiofiles==23.2.1
httpx==0.25.1
loguru==0.7.2
pydantic-settings==2.1.0

# 开发工具
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.11.0
flake8==6.1.0
```

### `frontend/package.json`

```json
{
  "name": "water-detection-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --fix --ignore-path .gitignore",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.3.8",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.2",
    "element-plus": "^2.4.3",
    "echarts": "^5.4.3",
    "video.js": "^8.6.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.5.0",
    "vite": "^5.0.0",
    "eslint": "^8.54.0",
    "eslint-plugin-vue": "^9.18.1",
    "prettier": "^3.1.0",
    "vitest": "^0.34.6",
    "@vue/test-utils": "^2.4.2"
  }
}
```

---

## 文件命名规范

### 后端（Python）
- **模块文件**: 小写+下划线，如 `user_service.py`
- **类名**: 大驼峰，如 `UserService`
- **函数名**: 小写+下划线，如 `get_current_user`
- **常量**: 大写+下划线，如 `MAX_UPLOAD_SIZE`

### 前端（Vue/JavaScript）
- **组件文件**: 大驼峰，如 `UserTable.vue`
- **工具文件**: 小写+连字符，如 `request.js`
- **函数名**: 小驼峰，如 `getCurrentUser`
- **常量**: 大写+下划线，如 `API_BASE_URL`

---

## 数据存储目录

### 后端存储结构
```
backend/
├── models/              # AI模型文件（持久化）
│   ├── yolov5s.pt
│   └── yolov8n.pt
│
├── uploads/             # 用户上传文件（临时）
│   ├── images/
│   │   └── {user_id}/
│   │       └── {timestamp}_{filename}
│   └── videos/
│       └── {user_id}/
│           └── {timestamp}_{filename}
│
├── results/             # 检测结果（持久化）
│   ├── images/
│   │   └── {detection_id}/
│   │       ├── original.jpg
│   │       ├── result.jpg
│   │       └── result.json
│   └── videos/
│       └── {detection_id}/
│           ├── original.mp4
│           ├── result.mp4
│           └── result.json
│
└── logs/                # 日志文件
    ├── app_2024-01-01.log
    └── celery_2024-01-01.log
```

---

## Git忽略文件

### `backend/.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# 数据文件
uploads/
results/
logs/
*.pt
*.pth

# 配置
.env
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo
```

### `frontend/.gitignore`
```gitignore
# Dependencies
node_modules/
.pnp
.pnp.js

# Production
dist/
build/

# Misc
.DS_Store
.env
.env.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
```

---

## 开发流程中的目录使用

### 1. 初始化项目
```bash
# 创建项目根目录
mkdir water-target-detection
cd water-target-detection

# 创建后端项目
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 创建前端项目
cd ..
npm create vite@latest frontend -- --template vue
cd frontend
npm install
```

### 2. 开发阶段
- 后端代码放在 `backend/app/` 目录
- 前端代码放在 `frontend/src/` 目录
- 测试代码分别放在对应的 `tests/` 目录

### 3. 部署阶段
- 使用 `docker-compose.yml` 编排所有服务
- 环境变量通过 `.env` 文件管理
- 数据通过Docker volumes持久化

---

## 总结

这个项目结构设计遵循以下原则：

1. **清晰的分层**: 后端采用MVC模式，前端采用组件化设计
2. **模块化**: 每个功能模块独立，便于维护
3. **可扩展**: 易于添加新功能和模块
4. **标准化**: 遵循行业最佳实践
5. **Docker友好**: 便于容器化部署

建议在开发过程中严格遵循这个结构，保持代码组织的一致性和可维护性。
