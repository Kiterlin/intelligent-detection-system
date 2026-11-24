## Stage 1: 复现与定位
**Goal**: 复现“登录网络错误”，明确失败链路（前端请求 / 后端是否启动 / 依赖缺失）。
**Success Criteria**: 能从日志或脚本输出中确认导致网络错误的根因。
**Tests**: 查看 `backend.log` / `frontend.log`；定位启动脚本实际是否启动后端进程。
**Status**: Complete

## Stage 2: 修复启动脚本的后端启动方式
**Goal**: 让 `./start.sh` 能可靠启动后端（避免 `uvicorn`/`celery` 不在 PATH 导致“假启动”）。
**Success Criteria**: 后端启动失败时脚本能明确报错并退出；后端启动成功时能继续启动前端。
**Tests**: 运行 `./start.sh`，确认能检测到后端是否监听端口/健康检查可用。
**Status**: Complete

## Stage 3: 增强服务自检（含登录接口验证）
**Goal**: 增强 `test_services.sh`（或启动脚本）覆盖登录接口检查，快速暴露“网络错误/后端未起”的问题。
**Success Criteria**: 脚本可检测 `/api/v1/auth/login` 连通性与返回码，并给出可操作的提示。
**Tests**: 运行 `./test_services.sh`，确认包含登录测试并能输出结果。
**Status**: Complete

## Stage 4: 回归验证与收尾
**Goal**: 确认默认账号 `user/user123`、`admin/admin123` 可以正常登录（不再是“网络错误”）。
**Success Criteria**: 浏览器登录成功或脚本返回 200；文档/脚本输出与实际行为一致。
**Tests**: 运行 `./start.sh` 后通过前端登录；或使用脚本/HTTP请求验证登录返回 200。
**Status**: Complete
