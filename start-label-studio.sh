#!/bin/bash
cd "$(dirname "$0")"
echo "启动 Label Studio 服务..."
docker compose -f docker-compose.label-studio.yml up -d
echo "服务已启动"
echo "访问: http://localhost:8080"
echo "用户名: admin@example.com"
echo "密码: admin123"
