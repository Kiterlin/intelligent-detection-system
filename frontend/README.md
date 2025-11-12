# 前端 - 水下目标智能检测平台

基于 Vue 3 + Vite 的现代化前端应用。

## 技术栈

- **框架**: Vue 3.3+
- **构建工具**: Vite 5.0+
- **UI 组件库**: Element Plus 2.4+
- **路由**: Vue Router 4.2+
- **状态管理**: Pinia 2.1+
- **HTTP 客户端**: Axios 1.6+
- **图表**: ECharts 5.4+
- **视频播放**: Video.js 8.6+

## 目录结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 通用组件
│   ├── views/           # 页面视图
│   ├── layouts/         # 布局组件
│   ├── router/          # 路由配置
│   ├── stores/          # Pinia 状态管理
│   ├── api/             # API 接口
│   ├── utils/           # 工具函数
│   ├── composables/     # 组合式函数
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── public/              # 公共静态资源
└── tests/               # 测试目录
```

## 安装

```bash
# 安装依赖
npm install

# 或使用 pnpm
pnpm install
```

## 运行

### 开发模式

```bash
npm run dev
```

访问 http://localhost:5173

### 生产构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

## 代码规范

```bash
# ESLint 检查
npm run lint

# 代码格式化
npm run format
```

## 测试

```bash
# 运行单元测试
npm run test:unit

# 运行 E2E 测试
npm run test:e2e
```

## 环境变量

创建 `.env.local` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 页面路由

### 用户端
- `/` - 首页
- `/detect` - 智能检测
- `/history` - 检测历史
- `/profile` - 个人中心

### 管理后台
- `/admin` - 仪表盘
- `/admin/users` - 用户管理
- `/admin/models` - 模型管理

### 认证
- `/login` - 登录
- `/register` - 注册

## 开发规范

- 组件文件使用大驼峰命名（如 `UserTable.vue`）
- 工具函数文件使用小写+连字符（如 `request.js`）
- 遵循 Vue 3 组合式 API 风格
- 使用 ESLint + Prettier 保持代码风格一致
- 提交前确保 lint 通过
