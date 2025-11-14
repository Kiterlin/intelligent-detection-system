# 🚀 一键启动指南

## 快速开始

### 1. 激活 Conda 环境

```bash
conda activate RSD
```

### 2. 启动所有服务

```bash
./start.sh
```

**脚本会自动：**
- ✅ 检查并启动 PostgreSQL
- ✅ 检查并启动 Redis
- ✅ 启动后端 FastAPI 服务 (端口 8000)
- ✅ 启动 Celery 异步任务服务
- ✅ 启动前端 Vite 开发服务器 (端口 5173)
- ✅ 显示实时日志

### 3. 访问系统

启动成功后，打开浏览器访问：

- **前端应用**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs

### 4. 停止服务

按下 `Ctrl+C` 或在新终端运行：

```bash
./stop.sh
```

---

## 📋 测试账号

系统预置了两个测试账号：

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 👤 普通用户 | user | user123 | 检测功能、历史记录 |
| 👑 管理员 | admin | admin123 | 所有功能 + 管理后台 |

---

## 📊 日志文件

所有服务日志保存在项目根目录：

- `backend.log` - 后端服务日志
- `celery.log` - Celery 任务日志
- `frontend.log` - 前端服务日志

**查看日志：**

```bash
# 查看后端日志
tail -f backend.log

# 查看 Celery 日志
tail -f celery.log

# 查看前端日志
tail -f frontend.log
```

---

## 🔧 功能测试流程

### 普通用户测试

1. 使用 `user / user123` 登录
2. 点击"开始检测"
3. 上传图片或视频
4. 选择可用模型
5. 调整参数（可选）
6. 开始检测
7. 查看结果
8. 下载结果文件
9. 在"检测历史"中查看所有记录

### 管理员测试

1. 使用 `admin / admin123` 登录
2. 进入"管理后台"
3. 查看 Dashboard 统计信息
4. 在"用户管理"中管理用户
5. 在"模型管理"中上传和管理模型
6. 测试所有管理功能

---

## ⚠️ 常见问题

### Q: 启动失败提示端口被占用

**解决方案：**

```bash
# 查找占用端口的进程
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口

# 停止所有服务
./stop.sh
```

### Q: PostgreSQL 或 Redis 启动失败

**解决方案：**

```bash
# 手动启动 PostgreSQL
sudo service postgresql start

# 手动启动 Redis
sudo service redis-server start

# 检查状态
pg_isready -h localhost -p 5432
redis-cli ping
```

### Q: 前端编译错误

**解决方案：**

```bash
cd frontend
rm -rf node_modules
npm install
cd ..
./start.sh
```

### Q: 后端启动失败

**解决方案：**

```bash
# 检查 conda 环境
conda activate RSD
pip list | grep fastapi

# 重新安装依赖（如需要）
cd backend
pip install -r requirements.txt
cd ..
./start.sh
```

---

## 📝 开发模式

### 热更新

所有服务都支持热更新：

- **后端**: 修改 Python 代码后自动重载
- **前端**: 修改 Vue 代码后自动刷新
- **Celery**: 需要手动重启

### 仅启动后端

```bash
cd backend
conda activate RSD
uvicorn app.main:app --reload --port 8000
```

### 仅启动前端

```bash
cd frontend
npm run dev
```

### 仅启动 Celery

```bash
cd backend
conda activate RSD
celery -A app.celery_app worker --loglevel=info
```

---

## 🎯 下一步

系统启动成功后，建议：

1. ✅ 用管理员账号登录
2. ✅ 进入"模型管理"上传 YOLO 模型
3. ✅ 激活上传的模型
4. ✅ 切换到普通用户测试检测功能
5. ✅ 上传测试图片或视频
6. ✅ 查看检测结果和历史记录

---

**最后更新**: 2025-11-12
**系统版本**: v0.5
**环境**: Conda RSD
