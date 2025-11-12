# 技术栈详细说明

> 本文档详细说明水下目标智能检测平台使用的所有技术组件、版本要求和配置说明。

---

## 目录
- [后端技术栈](#后端技术栈)
- [前端技术栈](#前端技术栈)
- [AI与机器学习](#ai与机器学习)
- [数据库与缓存](#数据库与缓存)
- [部署与运维](#部署与运维)
- [开发工具](#开发工具)
- [版本要求汇总](#版本要求汇总)

---

## 后端技术栈

### 核心框架

#### FastAPI
- **版本**: ^0.104.0
- **用途**: Web框架，提供REST API服务
- **选择理由**:
  - 高性能（基于Starlette和Pydantic）
  - 自动生成OpenAPI文档
  - 原生支持async/await异步编程
  - 强大的类型提示和数据验证
  - 活跃的社区和生态系统

- **主要功能**:
  - 路由管理
  - 请求/响应处理
  - 依赖注入
  - 中间件支持
  - WebSocket支持（可选）

- **配置示例**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Water Target Detection API",
    description="AI-powered underwater target detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Uvicorn
- **版本**: ^0.24.0
- **用途**: ASGI服务器，运行FastAPI应用
- **配置**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### ORM与数据库

#### SQLAlchemy
- **版本**: ^2.0.0
- **用途**: ORM框架，数据库操作
- **特性**:
  - 支持多种数据库（PostgreSQL、MySQL、SQLite）
  - 声明式模型定义
  - 查询构建器
  - 关系映射
  - 事务管理

- **模型示例**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Alembic
- **版本**: ^1.12.0
- **用途**: 数据库迁移工具
- **命令**:
```bash
# 初始化
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "create users table"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 认证与安全

#### Python-jose
- **版本**: ^3.3.0
- **用途**: JWT令牌生成和验证
- **使用示例**:
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

#### Passlib
- **版本**: ^1.7.4
- **用途**: 密码哈希和验证
- **配置**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 异步任务队列

#### Celery
- **版本**: ^5.3.0
- **用途**: 分布式任务队列，处理视频检测等耗时任务
- **配置**:
```python
from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时超时
)
```

- **任务示例**:
```python
@celery_app.task(bind=True)
def detect_video_task(self, video_path: str, model_id: int):
    # 更新进度
    self.update_state(state='PROGRESS', meta={'progress': 0})

    # 处理视频
    # ...

    return {"status": "completed", "result_path": result_path}
```

#### Redis
- **版本**: ^7.0
- **用途**:
  - Celery消息代理
  - 缓存存储
  - 会话存储
- **Python客户端**: redis-py ^5.0.0

### 数据验证

#### Pydantic
- **版本**: ^2.4.0（FastAPI内置）
- **用途**: 数据验证和设置管理
- **示例**:
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
```

### 环境配置

#### Python-dotenv
- **版本**: ^1.0.0
- **用途**: 加载环境变量
- **使用**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
```

### 其他后端依赖

- **python-multipart** ^0.0.6: 文件上传支持
- **aiofiles** ^23.2.0: 异步文件操作
- **httpx** ^0.25.0: HTTP客户端（用于外部API调用）

---

## 前端技术栈

### 核心框架

#### Vue 3
- **版本**: ^3.3.0
- **用途**: 前端框架
- **特性**:
  - Composition API
  - 更好的TypeScript支持
  - 更小的打包体积
  - 更快的渲染性能

- **配置**:
```javascript
// main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

const app = createApp(App)
app.use(router)
app.use(pinia)
app.use(ElementPlus)
app.mount('#app')
```

#### Vite
- **版本**: ^5.0.0
- **用途**: 构建工具和开发服务器
- **优势**:
  - 极快的冷启动
  - 即时的模块热更新（HMR）
  - 真正的按需编译
  - 优化的构建命令

- **配置**:
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### UI组件库

#### Element Plus
- **版本**: ^2.4.0
- **用途**: 企业级UI组件库
- **核心组件**:
  - Table: 数据表格
  - Form: 表单
  - Dialog: 对话框
  - Upload: 文件上传
  - Button: 按钮
  - Select: 下拉选择
  - Switch: 开关
  - Tag: 标签
  - Pagination: 分页
  - Message: 消息提示

- **按需引入**:
```javascript
import { ElButton, ElTable } from 'element-plus'
```

### 路由管理

#### Vue Router
- **版本**: ^4.2.0
- **用途**: 单页应用路由
- **配置示例**:
```javascript
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: 'detect',
        name: 'Detect',
        component: () => import('@/views/Detect.vue')
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
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

### 状态管理

#### Pinia
- **版本**: ^2.1.0
- **用途**: 状态管理（Vue 3官方推荐，替代Vuex）
- **示例**:
```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { login, getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin'
  },

  actions: {
    async login(credentials) {
      const response = await login(credentials)
      this.token = response.access_token
      localStorage.setItem('access_token', this.token)
      await this.fetchUser()
    },

    async fetchUser() {
      const user = await getCurrentUser()
      this.user = user
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
    }
  }
})
```

### HTTP客户端

#### Axios
- **版本**: ^1.6.0
- **用途**: HTTP请求库
- **配置**:
```javascript
// utils/request.js
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
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

### 图表库

#### ECharts
- **版本**: ^5.4.0
- **用途**: 数据可视化
- **使用**:
```javascript
import * as echarts from 'echarts'

const chart = echarts.init(document.getElementById('chart'))
chart.setOption({
  title: { text: '检测趋势' },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed'] },
  yAxis: { type: 'value' },
  series: [{
    data: [120, 200, 150],
    type: 'line'
  }]
})
```

### 视频播放器

#### Video.js
- **版本**: ^8.6.0
- **用途**: 视频播放器
- **配置**:
```javascript
import videojs from 'video.js'
import 'video.js/dist/video-js.css'

const player = videojs('my-video', {
  controls: true,
  autoplay: false,
  preload: 'auto'
})
```

### 代码质量工具

#### ESLint
- **版本**: ^8.50.0
- **用途**: JavaScript代码检查
- **配置**: .eslintrc.js

#### Prettier
- **版本**: ^3.0.0
- **用途**: 代码格式化
- **配置**: .prettierrc.js

---

## AI与机器学习

### 深度学习框架

#### PyTorch
- **版本**: ^2.1.0
- **用途**: 深度学习框架，运行YOLO模型
- **安装**:
```bash
# CPU版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU版本（CUDA 11.8）
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

- **设备选择**:
```python
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
```

### 目标检测

#### Ultralytics
- **版本**: ^8.0.0
- **用途**: YOLO系列模型的官方实现
- **支持模型**:
  - YOLOv5
  - YOLOv8
  - YOLOv9（可选）

- **使用示例**:
```python
from ultralytics import YOLO

# 加载模型
model = YOLO("yolov8n.pt")

# 推理
results = model("image.jpg", conf=0.5, iou=0.45)

# 处理结果
for result in results:
    boxes = result.boxes  # 检测框
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = box.conf[0].item()
        cls = box.cls[0].item()
        print(f"Class: {cls}, Confidence: {conf:.2f}, Box: ({x1}, {y1}, {x2}, {y2})")
```

### 图像处理

#### OpenCV
- **版本**: ^4.8.0 (opencv-python)
- **用途**: 图像和视频处理
- **功能**:
  - 图像读取和保存
  - 视频读取和写入
  - 图像预处理
  - 绘制检测框

- **示例**:
```python
import cv2

# 读取图像
image = cv2.imread("image.jpg")

# 绘制检测框
cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
cv2.putText(image, f"{class_name} {conf:.2f}", (x1, y1-10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# 保存结果
cv2.imwrite("result.jpg", image)
```

#### Pillow
- **版本**: ^10.1.0
- **用途**: Python图像处理库
- **使用**:
```python
from PIL import Image

# 打开图像
img = Image.open("image.jpg")

# 调整大小
img_resized = img.resize((640, 640))

# 保存
img_resized.save("resized.jpg")
```

### 数值计算

#### NumPy
- **版本**: ^1.24.0
- **用途**: 数值计算和数组操作
- **使用**:
```python
import numpy as np

# 图像转数组
img_array = np.array(image)

# 归一化
img_normalized = img_array / 255.0
```

---

## 数据库与缓存

### 关系型数据库

#### PostgreSQL
- **版本**: 15.x
- **用途**: 主数据库
- **特性**:
  - ACID事务支持
  - 复杂查询
  - JSON支持
  - 全文搜索
  - 丰富的数据类型

- **Docker配置**:
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: water_detection
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
```

- **数据库设计**:
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 模型表
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20),
    file_path VARCHAR(255) NOT NULL,
    file_size BIGINT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 检测历史表
CREATE TABLE detection_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    model_id INTEGER REFERENCES ml_models(id) ON DELETE SET NULL,
    file_type VARCHAR(20),  -- 'image' or 'video'
    file_path VARCHAR(255),
    result_path VARCHAR(255),
    result_json JSONB,
    status VARCHAR(20),  -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_detection_user_id ON detection_history(user_id);
CREATE INDEX idx_detection_created_at ON detection_history(created_at DESC);
```

#### Psycopg2
- **版本**: ^2.9.0 (psycopg2-binary)
- **用途**: PostgreSQL数据库适配器

### 缓存数据库

#### Redis
- **版本**: 7.x
- **用途**:
  - Celery消息代理
  - 缓存存储
  - 会话管理
  - 实时数据

- **Docker配置**:
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
```

- **缓存示例**:
```python
import redis

# 连接Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# 缓存模型列表
r.setex('models_list', 3600, json.dumps(models))  # 1小时过期

# 获取缓存
cached = r.get('models_list')
if cached:
    models = json.loads(cached)
```

---

## 部署与运维

### 容器化

#### Docker
- **版本**: ^24.0
- **用途**: 容器化应用
- **后端Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- **前端Dockerfile**:
```dockerfile
# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
- **版本**: ^2.20
- **用途**: 多容器编排
- **配置**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: water_detection
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/water_detection
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    volumes:
      - ./backend:/app
      - model_files:/app/models
      - detection_results:/app/results
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/water_detection
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
      - model_files:/app/models
      - detection_results:/app/results
    depends_on:
      - redis
      - postgres

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
  model_files:
  detection_results:
```

### Web服务器

#### Nginx
- **版本**: ^1.25
- **用途**:
  - 静态文件服务
  - 反向代理
  - 负载均衡
  - SSL终止

- **配置**:
```nginx
# nginx.conf
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;

    # GZIP压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # 上传大小限制
    client_max_body_size 500M;

    server {
        listen 80;
        server_name example.com;

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # API反向代理
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时设置
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # 静态文件（检测结果）
        location /results {
            alias /app/results;
            autoindex off;
        }
    }

    # HTTPS配置（使用Let's Encrypt）
    # server {
    #     listen 443 ssl http2;
    #     server_name example.com;
    #
    #     ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    #     ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    #
    #     # SSL配置
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #     ssl_prefer_server_ciphers on;
    #
    #     # 其他配置同上...
    # }
}
```

### 日志管理

#### Loguru
- **版本**: ^0.7.0
- **用途**: Python日志库
- **配置**:
```python
from loguru import logger
import sys

# 移除默认handler
logger.remove()

# 添加控制台输出
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 添加文件输出
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",  # 每天午夜轮转
    retention="30 days",  # 保留30天
    compression="zip",  # 压缩旧日志
    level="INFO"
)
```

---

## 开发工具

### Python开发

- **Python版本**: 3.11+
- **包管理**: pip, poetry（推荐）
- **虚拟环境**: venv, conda
- **代码格式化**: Black ^23.0.0
- **代码检查**: Flake8 ^6.1.0, Pylint
- **类型检查**: MyPy ^1.6.0

### JavaScript开发

- **Node.js版本**: 18.x LTS
- **包管理**: npm, pnpm（推荐）
- **代码格式化**: Prettier
- **代码检查**: ESLint
- **构建工具**: Vite

### 测试工具

#### 后端测试
- **pytest** ^7.4.0: 单元测试和集成测试
- **pytest-asyncio** ^0.21.0: 异步测试
- **pytest-cov** ^4.1.0: 测试覆盖率
- **httpx** ^0.25.0: 测试HTTP客户端

#### 前端测试
- **Vitest** ^0.34.0: 单元测试
- **@vue/test-utils** ^2.4.0: Vue组件测试
- **Playwright** ^1.39.0: E2E测试（可选）
- **Cypress** ^13.0.0: E2E测试（可选）

### API测试

- **Postman**: API测试和文档
- **Thunder Client**: VS Code插件
- **Insomnia**: API测试工具

### 数据库工具

- **DBeaver**: 通用数据库管理工具
- **pgAdmin**: PostgreSQL管理工具
- **RedisInsight**: Redis管理工具

### 版本控制

- **Git**: 版本控制
- **GitHub/GitLab**: 代码托管
- **Git Flow**: 分支管理策略

---

## 版本要求汇总

### 运行环境
| 组件 | 版本要求 |
|------|---------|
| Python | 3.11+ |
| Node.js | 18.x LTS |
| PostgreSQL | 15.x |
| Redis | 7.x |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |

### 后端依赖
| 包名 | 版本 | 说明 |
|------|------|------|
| fastapi | ^0.104.0 | Web框架 |
| uvicorn | ^0.24.0 | ASGI服务器 |
| sqlalchemy | ^2.0.0 | ORM |
| alembic | ^1.12.0 | 数据库迁移 |
| psycopg2-binary | ^2.9.0 | PostgreSQL驱动 |
| redis | ^5.0.0 | Redis客户端 |
| celery | ^5.3.0 | 任务队列 |
| python-jose | ^3.3.0 | JWT |
| passlib | ^1.7.4 | 密码哈希 |
| python-multipart | ^0.0.6 | 文件上传 |
| python-dotenv | ^1.0.0 | 环境变量 |
| torch | ^2.1.0 | 深度学习 |
| ultralytics | ^8.0.0 | YOLO |
| opencv-python | ^4.8.0 | 图像处理 |
| pillow | ^10.1.0 | 图像库 |
| numpy | ^1.24.0 | 数值计算 |
| loguru | ^0.7.0 | 日志 |

### 前端依赖
| 包名 | 版本 | 说明 |
|------|------|------|
| vue | ^3.3.0 | 前端框架 |
| vue-router | ^4.2.0 | 路由 |
| pinia | ^2.1.0 | 状态管理 |
| axios | ^1.6.0 | HTTP客户端 |
| element-plus | ^2.4.0 | UI组件库 |
| echarts | ^5.4.0 | 图表库 |
| video.js | ^8.6.0 | 视频播放器 |
| vite | ^5.0.0 | 构建工具 |

### 开发依赖
| 包名 | 用途 |
|------|------|
| black | Python代码格式化 |
| flake8 | Python代码检查 |
| pytest | Python测试 |
| pytest-cov | 测试覆盖率 |
| eslint | JS代码检查 |
| prettier | JS代码格式化 |
| vitest | Vue测试 |

---

## 安装指南

### 后端环境设置

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 或使用Poetry
poetry install
```

### 前端环境设置

```bash
# 安装依赖
npm install
# 或
pnpm install

# 启动开发服务器
npm run dev
```

### 数据库设置

```bash
# 使用Docker启动PostgreSQL和Redis
docker-compose up -d postgres redis

# 运行数据库迁移
alembic upgrade head
```

---

## 生产环境建议

### 性能优化
- 使用Gunicorn或Uvicorn多worker模式
- 启用数据库连接池
- 使用Redis缓存热点数据
- 使用CDN加速静态资源
- 启用HTTP/2和GZIP压缩

### 安全加固
- 使用HTTPS（Let's Encrypt）
- 配置CORS白名单
- 设置强密码策略
- 定期更新依赖包
- 配置防火墙规则
- 使用环境变量管理密钥

### 监控和日志
- 使用Prometheus + Grafana监控
- 配置ELK日志收集（可选）
- 设置告警规则
- 定期备份数据库

---

## 总结

本技术栈设计遵循以下原则：

1. **现代化**: 使用最新稳定版本的技术
2. **成熟**: 选择经过生产环境验证的技术
3. **高性能**: 优先考虑性能和可扩展性
4. **易维护**: 代码清晰，文档完善
5. **安全**: 内置安全最佳实践

这个技术栈适合构建企业级AI应用，能够满足高并发、高可用、易扩展的需求。
