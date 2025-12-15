#!/bin/bash
cd "$(dirname "$0")"
echo "停止 Label Studio 服务..."
docker compose -f docker-compose.label-studio.yml down
echo "服务已停止"
