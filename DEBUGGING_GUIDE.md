# 功能调试指南

本指南帮助您诊断和解决模型上传、检测功能的问题。

---

## 🔍 问题排查步骤

### 1️⃣ 检查服务是否正常运行

#### 检查后端服务

```bash
# 检查后端是否运行在8000端口
lsof -i :8000

# 或者查看进程
ps aux | grep uvicorn
```

**期望输出**：应该看到uvicorn进程正在运行

#### 检查前端服务

```bash
# 检查前端是否运行在5173端口
lsof -i :5173

# 或者查看进程
ps aux | grep vite
```

**期望输出**：应该看到vite进程正在运行

#### 检查Redis服务

```bash
redis-cli ping
```

**期望输出**：`PONG`

---

### 2️⃣ 打开浏览器开发者工具

这是最重要的调试步骤！

**Chrome/Edge**：按 `F12` 或 `Ctrl+Shift+I`
**Firefox**：按 `F12`
**Safari**：`Cmd+Option+I`

#### 查看Console（控制台）标签页

**检查JavaScript错误**：
- 红色的错误信息
- 橙色的警告信息
- 注意时间戳，找到点击"上传"按钮时的错误

**常见错误及解决方法**：

```
❌ TypeError: Cannot read property 'validate' of null
   原因：表单ref没有正确绑定
   解决：重启前端服务
```

```
❌ Network Error / ERR_CONNECTION_REFUSED
   原因：后端服务未运行或端口错误
   解决：启动后端服务
```

```
❌ 401 Unauthorized
   原因：登录已过期或未登录
   解决：重新登录
```

```
❌ 404 Not Found
   原因：API端点不存在
   解决：检查后端路由配置
```

#### 查看Network（网络）标签页

**检查上传请求**：

1. 点击"上传"按钮
2. 在Network标签页中查找：
   - 模型上传：`/admin/models/upload`
   - 图片检测：`/detect/image`
   - 视频检测：`/detect/video`

3. 点击请求，查看：
   - **Headers**：请求头信息
   - **Payload**：发送的数据
   - **Response**：服务器响应
   - **Status Code**：状态码（200=成功，400=请求错误，500=服务器错误）

**成功的模型上传请求示例**：
```
Status: 201 Created
Response:
{
  "id": 1,
  "name": "yolov8n",
  "version": "v1.0",
  "status": "inactive",
  "file_size": 6234567,
  ...
}
```

**失败的请求示例**：
```
Status: 422 Unprocessable Entity
Response:
{
  "detail": "File type not allowed"
}
```

---

### 3️⃣ 模型上传问题排查

#### 问题1：点击"上传"按钮无反应

**排查清单**：

✅ **步骤1**：打开浏览器Console，查看是否有错误信息

✅ **步骤2**：检查是否选择了文件
```
如果未显示"已选择文件：xxx"，说明文件选择失败
```

✅ **步骤3**：检查是否填写了模型名称（必填项）

✅ **步骤4**：检查文件格式
```
只支持 .pt 和 .pth 格式
如果选择了其他格式，会被拒绝
```

✅ **步骤5**：检查文件大小
```
最大500MB
超过会被拒绝
```

✅ **步骤6**：打开Network标签页，看是否有上传请求发出

如果没有请求发出，说明前端代码有问题：

```bash
# 重启前端服务
cd frontend
npm run dev
```

#### 问题2：上传请求失败（显示错误）

**检查后端日志**：

```bash
# 如果使用后台日志文件
tail -f backend.log

# 或者直接查看终端输出
```

**常见错误**：

```
错误：413 Payload Too Large
原因：文件超过服务器限制
解决：检查nginx配置或FastAPI文件大小限制
```

```
错误：401 Unauthorized
原因：未登录或token过期
解决：重新登录
```

```
错误：403 Forbidden
原因：权限不足（非管理员）
解决：使用管理员账号登录
```

```
错误：500 Internal Server Error
原因：后端代码错误
解决：查看后端日志，检查文件保存路径是否存在
```

---

### 4️⃣ 检测功能问题排查

#### 问题1：检测按钮无法点击（灰色）

**检查条件**：
- ✅ 是否选择了文件？
- ✅ 是否选择了模型？
- ✅ 是否有可用的模型？（需要管理员先上传并激活模型）

**如何激活模型**：
1. 以管理员身份登录
2. 进入"管理后台" → "模型管理"
3. 找到已上传的模型
4. 点击状态开关，激活模型

#### 问题2：点击"开始检测"无反应

**排查步骤**：

1. **打开Console**，查看错误信息

2. **打开Network标签页**，检查是否有检测请求

**图片检测请求**：
```
POST /api/v1/detect/image
Content-Type: multipart/form-data

FormData:
- file: (binary)
- model_id: 1
- confidence_threshold: 0.5
- iou_threshold: 0.45
```

**视频检测请求**：
```
POST /api/v1/detect/video
Content-Type: multipart/form-data

FormData:
- file: (binary)
- model_id: 1
- confidence_threshold: 0.5
- iou_threshold: 0.45
```

3. **检查响应**：

成功响应示例（图片）：
```json
{
  "id": 1,
  "file_type": "image",
  "status": "completed",
  "output_file_path": "results/image_123456.jpg",
  "result_json": {
    "detections": [
      {
        "class": "person",
        "confidence": 0.95,
        "bbox": [100, 200, 300, 400]
      }
    ]
  },
  "detected_objects_count": 1,
  "processing_time": 0.5
}
```

失败响应示例：
```json
{
  "detail": "Model not found or not active"
}
```

#### 问题3：检测请求失败

**常见错误**：

```
错误：No active model found
原因：没有激活的模型
解决：管理员激活至少一个模型
```

```
错误：Model file not found
原因：模型文件被删除或路径错误
解决：重新上传模型
```

```
错误：File too large
原因：上传文件超过限制
解决：压缩文件或分段上传
```

---

### 5️⃣ 测试完整流程

#### 测试模型上传

```bash
# 1. 准备一个YOLO模型文件（.pt或.pth）
# 下载示例：https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# 2. 登录管理员账号
用户名：admin
密码：admin123

# 3. 进入"管理后台" → "模型管理"

# 4. 点击"上传模型"按钮

# 5. 填写信息：
模型名称：yolov8n（必填）
版本号：v1.0（可选）
描述：YOLO v8 nano模型（可选）

# 6. 选择模型文件（.pt或.pth）

# 7. 点击"上传"按钮

# 8. 等待上传完成

# 9. 激活模型（点击状态开关）
```

**验证上传成功**：
- ✅ 表格中显示新模型
- ✅ 文件大小正确显示
- ✅ 可以激活/停用模型

#### 测试图片检测

```bash
# 1. 准备一张测试图片（jpg/png/bmp，< 20MB）

# 2. 以任意用户登录

# 3. 进入"目标检测"页面

# 4. 选择图片文件（拖拽或点击上传）

# 5. 选择模型（下拉框）

# 6. 调整参数（可选）：
置信度阈值：0.5
IOU阈值：0.45

# 7. 点击"开始检测"

# 8. 等待检测完成（几秒钟）

# 9. 查看结果
```

**验证检测成功**：
- ✅ 显示检测结果图片（带标注框）
- ✅ 显示检测统计信息
- ✅ 显示检测到的对象列表
- ✅ 可以下载结果

#### 测试视频检测

```bash
# 1. 准备一个测试视频（mp4/avi/mov，< 500MB）

# 2. 以任意用户登录

# 3. 进入"目标检测"页面

# 4. 选择视频文件

# 5. 选择模型

# 6. 点击"开始检测"

# 7. 等待异步处理（可能需要几分钟）
   - 会显示处理状态
   - 可以取消处理

# 8. 完成后查看结果
```

**验证检测成功**：
- ✅ 显示处理状态变化（等待→处理中→已完成）
- ✅ 显示结果视频（带标注框）
- ✅ 可以播放视频
- ✅ 可以下载结果

---

## 🛠 常见问题修复

### 修复1：前端上传按钮无反应

**可能原因**：前端代码热更新失败

**解决方法**：

```bash
# 1. 停止前端服务（Ctrl+C）

# 2. 清理缓存
cd frontend
rm -rf node_modules/.vite
rm -rf dist

# 3. 重新启动
npm run dev
```

### 修复2：后端API 404错误

**可能原因**：后端路由未正确注册

**检查后端API**：

```bash
cd backend

# 查看已注册的路由
python -c "
from app.main import app
for route in app.routes:
    if hasattr(route, 'path'):
        print(f'{route.methods} {route.path}')
" | grep -E "(upload|detect)"
```

**期望输出**：
```
{'POST'} /api/v1/admin/models/upload
{'POST'} /api/v1/detect/image
{'POST'} /api/v1/detect/video
```

### 修复3：模型加载失败

**检查模型文件**：

```bash
cd backend

# 检查模型目录
ls -lh models/

# 检查数据库中的模型记录
sqlite3 water_detection.db "SELECT id, name, file_path, status FROM ml_models;"
# 或PostgreSQL:
# psql -U water_detection_user -d water_detection -c "SELECT id, name, file_path, status FROM ml_models;"
```

**验证模型文件存在**：
- models/目录应该存在
- 模型文件路径与数据库记录一致
- 文件权限正确（可读）

### 修复4：Celery任务失败（视频检测）

**检查Celery Worker**：

```bash
# 1. 查看Celery Worker是否运行
ps aux | grep celery

# 2. 查看Celery日志
tail -f celery.log

# 3. 重启Celery Worker
cd backend
celery -A app.celery_app worker --loglevel=info
```

**检查Redis连接**：

```bash
# 测试Redis
redis-cli ping

# 查看任务队列
redis-cli
> KEYS celery*
> QUIT
```

---

## 📋 完整测试检查表

### 环境检查
- [ ] PostgreSQL/SQLite 运行正常
- [ ] Redis 运行正常
- [ ] 后端服务运行在8000端口
- [ ] Celery Worker 运行正常
- [ ] 前端服务运行在5173端口

### 模型上传测试
- [ ] 可以选择.pt/.pth文件
- [ ] 必填项验证正常
- [ ] 文件大小验证正常
- [ ] 上传进度显示正常
- [ ] 上传成功后显示在列表中
- [ ] 可以激活/停用模型
- [ ] 可以编辑模型信息
- [ ] 可以删除模型

### 图片检测测试
- [ ] 可以选择图片文件
- [ ] 模型列表正常加载
- [ ] 参数滑块正常工作
- [ ] 检测按钮状态正确
- [ ] 检测请求成功发送
- [ ] 检测结果正常显示
- [ ] 可以下载结果
- [ ] 结果保存到历史记录

### 视频检测测试
- [ ] 可以选择视频文件
- [ ] 异步任务创建成功
- [ ] 状态轮询正常工作
- [ ] 进度显示正常
- [ ] 可以取消任务
- [ ] 完成后结果正常显示
- [ ] 可以播放结果视频
- [ ] 可以下载结果

---

## 🚀 快速验证脚本

创建一个快速测试脚本：

```bash
#!/bin/bash
# test_services.sh

echo "=== 服务状态检查 ==="

# 检查后端
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ 后端服务运行正常 (端口8000)"
else
    echo "❌ 后端服务未运行"
fi

# 检查前端
if lsof -i :5173 > /dev/null 2>&1; then
    echo "✅ 前端服务运行正常 (端口5173)"
else
    echo "❌ 前端服务未运行"
fi

# 检查Redis
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis服务运行正常"
else
    echo "❌ Redis服务未运行"
fi

# 检查Celery
if ps aux | grep -v grep | grep celery > /dev/null 2>&1; then
    echo "✅ Celery Worker运行正常"
else
    echo "⚠️  Celery Worker未运行（视频检测将无法使用）"
fi

echo ""
echo "=== 后端API测试 ==="

# 测试后端健康检查
HEALTH_CHECK=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
    echo "✅ 后端API可访问"
    echo "响应：$HEALTH_CHECK"
else
    echo "❌ 后端API不可访问"
fi

echo ""
echo "=== 前端访问测试 ==="
echo "请在浏览器打开：http://localhost:5173"
echo "查看Console和Network标签页进行调试"
```

**使用方法**：

```bash
chmod +x test_services.sh
./test_services.sh
```

---

## 💡 获取帮助

如果以上步骤都无法解决问题：

1. **收集以下信息**：
   - 浏览器Console的完整错误信息
   - Network标签页的请求和响应
   - 后端日志（backend.log或终端输出）
   - Celery日志（celery.log）

2. **检查相关文档**：
   - [环境配置指南](./ENVIRONMENT_SETUP.md)
   - [项目使用说明](./docs/使用说明.md)
   - [后端README](./backend/README.md)

3. **常见问题场景**：
   - **开发环境**：检查所有服务是否启动
   - **权限问题**：确保使用正确的账号（管理员/用户）
   - **网络问题**：检查API基础URL配置
   - **数据库问题**：检查数据库连接和迁移状态

---

**最后更新**：2025-11-12
**适用版本**：v0.5
