# PostgreSQL 迁移指南

本指南将帮助您从SQLite迁移到PostgreSQL数据库。

## 📋 前提条件

1. **安装PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql postgresql-contrib

   # CentOS/RHEL
   sudo yum install postgresql-server postgresql-contrib

   # macOS
   brew install postgresql
   ```

2. **启动PostgreSQL服务**
   ```bash
   # Ubuntu/Debian
   sudo systemctl start postgresql
   sudo systemctl enable postgresql

   # macOS
   brew services start postgresql
   ```

3. **验证PostgreSQL运行状态**
   ```bash
   sudo systemctl status postgresql  # Linux
   brew services list  # macOS
   psql --version  # 查看版本
   ```

## 🚀 迁移步骤

### 方法一：自动化脚本（推荐）

使用提供的自动化脚本完成所有配置：

```bash
cd backend
./init_postgres.sh
```

脚本会自动完成：
- ✅ 检查PostgreSQL环境
- ✅ 创建数据库和用户
- ✅ 安装必要的扩展
- ✅ 配置权限
- ✅ 生成连接URL
- ✅ 可选：自动创建.env文件

### 方法二：手动配置

#### 步骤1：初始化PostgreSQL数据库

```bash
cd backend

# 使用SQL脚本初始化
sudo -u postgres psql -f init_postgres.sql

# 或手动执行以下命令
sudo -u postgres psql <<EOF
CREATE DATABASE water_detection ENCODING 'UTF8';
CREATE USER water_detection_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE water_detection TO water_detection_user;
EOF
```

#### 步骤2：配置环境变量

创建或修改 `.env` 文件：

```bash
# 复制模板
cp .env.example .env

# 编辑.env文件，修改DATABASE_URL
nano .env
```

将 `DATABASE_URL` 修改为：
```
DATABASE_URL="postgresql+asyncpg://water_detection_user:your_password@localhost:5432/water_detection"
```

**重要**：
- 替换 `your_password` 为实际密码
- 如果PostgreSQL在其他主机，修改 `localhost`
- 如果使用非默认端口，修改 `5432`

#### 步骤3：运行数据库迁移

激活虚拟环境并运行Alembic迁移：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行迁移创建表结构
alembic upgrade head
```

您应该看到类似输出：
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Add indexes
```

#### 步骤4：迁移现有数据（如果有）

如果您有现有的SQLite数据库数据需要迁移：

```bash
# 确保SQLite数据库文件存在
ls water_detection.db

# 运行迁移脚本
python migrate_to_postgres.py
```

迁移脚本会：
1. 读取SQLite中的所有数据
2. 按正确顺序导入PostgreSQL（users → ml_models → detection_history）
3. 保持ID和外键关系
4. 验证数据完整性
5. 显示迁移统计信息

**示例输出**：
```
============================================================
  数据库迁移工具: SQLite -> PostgreSQL
============================================================

请输入PostgreSQL数据库URL
(例如: postgresql+asyncpg://user:password@localhost:5432/water_detection)
> postgresql+asyncpg://water_detection_user:password@localhost:5432/water_detection

⚠️  警告：此操作会覆盖PostgreSQL中的现有数据
   源数据库: sqlite:///./water_detection.db
   目标数据库: postgresql+asyncpg://water_detection_user:***@localhost:5432/water_detection

是否继续？(yes/no): yes

🚀 开始数据库迁移
============================================================
📋 创建PostgreSQL表结构...
✅ 表结构创建完成

📖 读取SQLite用户数据...
   找到 3 条用户记录

📖 读取SQLite模型数据...
   找到 2 条模型记录

📖 读取SQLite检测历史数据...
   找到 15 条检测记录

🚀 开始迁移用户数据...
✅ 用户迁移完成: 3/3

🚀 开始迁移模型数据...
✅ 模型迁移完成: 2/2

🚀 开始迁移检测历史数据...
✅ 检测历史迁移完成: 15/15

🔍 验证数据完整性...
   用户表: 3 条记录
   模型表: 2 条记录
   检测历史表: 15 条记录
✅ 数据验证通过

============================================================
📊 迁移摘要
============================================================

users:
  总数: 3
  成功: 3
  失败: 0
  成功率: 100.0%

ml_models:
  总数: 2
  成功: 2
  失败: 0
  成功率: 100.0%

detection_history:
  总数: 15
  成功: 15
  失败: 0
  成功率: 100.0%

============================================================

✅ 迁移完成！

📝 下一步操作：
   1. 更新 .env 文件中的 DATABASE_URL 为 PostgreSQL URL
   2. 重启应用服务
   3. 验证所有功能正常工作
   4. 备份 SQLite 文件后可以删除
```

#### 步骤5：验证迁移

连接到PostgreSQL并验证数据：

```bash
# 连接到数据库
psql -U water_detection_user -d water_detection -h localhost

# 在psql中执行查询
\dt  -- 列出所有表
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM ml_models;
SELECT COUNT(*) FROM detection_history;

# 退出
\q
```

#### 步骤6：启动应用

```bash
# 确保在backend目录并激活虚拟环境
cd backend
source venv/bin/activate

# 启动FastAPI应用
uvicorn app.main:app --reload --port 8000
```

#### 步骤7：功能测试

1. **测试用户认证**
   - 访问 http://localhost:5173
   - 尝试登录现有用户
   - 尝试注册新用户

2. **测试管理功能**
   - 访问 http://localhost:5173/admin
   - 查看用户列表
   - 查看模型列表
   - 测试CRUD操作

3. **测试检测功能**
   - 访问 http://localhost:5173/detection
   - 上传图片进行检测
   - 查看检测历史

## 🔧 故障排查

### 问题1：连接被拒绝

```
ERROR: could not connect to server: Connection refused
```

**解决方案**：
```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 启动PostgreSQL
sudo systemctl start postgresql

# 检查端口
sudo netstat -tulpn | grep 5432
```

### 问题2：认证失败

```
ERROR: FATAL: password authentication failed for user "water_detection_user"
```

**解决方案**：
1. 验证密码是否正确
2. 检查 `pg_hba.conf` 配置：
   ```bash
   sudo nano /etc/postgresql/15/main/pg_hba.conf
   ```
   确保包含：
   ```
   local   all             all                                     md5
   host    all             all             127.0.0.1/32            md5
   ```
3. 重启PostgreSQL：
   ```bash
   sudo systemctl restart postgresql
   ```

### 问题3：权限不足

```
ERROR: permission denied for schema public
```

**解决方案**：
```bash
sudo -u postgres psql -d water_detection <<EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO water_detection_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO water_detection_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO water_detection_user;
EOF
```

### 问题4：Alembic迁移失败

```
ERROR: Can't locate revision identified by 'xxxxx'
```

**解决方案**：
```bash
# 检查当前版本
alembic current

# 查看历史
alembic history

# 如果是新数据库，直接标记为最新
alembic stamp head
```

### 问题5：数据迁移部分失败

如果迁移脚本报告有失败的记录，检查详细错误信息：

1. 查看外键约束是否满足
2. 检查数据类型是否兼容
3. 验证枚举值是否匹配
4. 手动修复问题数据后重新运行

## 📊 性能对比

迁移后，您应该体验到显著的性能提升：

| 指标 | SQLite | PostgreSQL | 提升 |
|------|--------|------------|------|
| 并发查询 | 单连接 | 20+连接 | ~20x |
| 写入性能 | 受限 | 高效 | ~5-10x |
| 复杂查询 | 慢 | 优化 | ~3-5x |
| 索引效率 | 基础 | 高级 | ~2-3x |

## 🔒 安全建议

1. **强密码**：使用强密码（至少16位，包含大小写字母、数字、特殊字符）
   ```bash
   # 生成强密码
   openssl rand -base64 24
   ```

2. **限制访问**：配置PostgreSQL只允许必要的主机访问
   ```
   # pg_hba.conf
   host    water_detection    water_detection_user    127.0.0.1/32    md5
   ```

3. **定期备份**：
   ```bash
   # 创建备份
   pg_dump -U water_detection_user -d water_detection -F c -f backup_$(date +%Y%m%d).dump

   # 恢复备份
   pg_restore -U water_detection_user -d water_detection -c backup_20231120.dump
   ```

4. **更新SECRET_KEY**：迁移后更新应用的SECRET_KEY
   ```bash
   # 生成新密钥
   openssl rand -hex 32

   # 更新.env文件
   SECRET_KEY="生成的新密钥"
   ```

## 📝 迁移检查清单

在完成迁移后，使用此清单确保一切正常：

- [ ] PostgreSQL服务正常运行
- [ ] 数据库和用户已创建
- [ ] 扩展已安装（uuid-ossp, pg_trgm）
- [ ] .env文件已更新DATABASE_URL
- [ ] Alembic迁移成功执行
- [ ] 数据迁移完成（如适用）
- [ ] 数据完整性验证通过
- [ ] 应用可以正常启动
- [ ] 用户认证功能正常
- [ ] 管理功能正常
- [ ] 检测功能正常
- [ ] 检测历史可以查看
- [ ] 性能满足预期
- [ ] SQLite数据已备份
- [ ] 文档已更新

## 🔄 回滚到SQLite（如需要）

如果迁移后遇到问题，可以快速回滚到SQLite：

1. 停止应用
2. 修改 `.env` 文件：
   ```
   DATABASE_URL="sqlite+aiosqlite:///./water_detection.db"
   ```
3. 重启应用

原始SQLite数据保持不变，可以安全回滚。

## 📞 获取帮助

如果遇到本指南未涵盖的问题：

1. 查看应用日志：`logs/app.log`
2. 查看PostgreSQL日志：`/var/log/postgresql/postgresql-15-main.log`
3. 检查Celery日志（如果使用）
4. 参考文档：`docs/`目录
5. 提交Issue：项目仓库

## ✅ 迁移完成

恭喜！您已成功将应用迁移到PostgreSQL。现在您可以享受：

- 🚀 更好的性能
- 💪 更强的并发能力
- 🔧 更多的高级特性
- 📈 更好的扩展性

开始使用您的水下目标智能检测平台吧！
