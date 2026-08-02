#!/usr/bin/env bash
# 部署脚本:在部署服务器上执行(由 CD 调用,也可手动运行)。
# 要求:服务器已装 Docker;代码已同步到部署目录。
# 用法: cd /opt/banksys_sy_lixiaohua && bash scripts/deploy.sh
# 特性:幂等可重跑;主机端口 8888~8898 自动回退;失败即停(规范 05)。
set -e

APP="banksys_sy_lixiaohua"
PORT_BASE="8888"
PORT_MAX="8898"
HEALTH_PATH="/_stcore/health"
# 国内服务器构建慢/超时时,可预置环境变量 PIP_INDEX_URL 指向国内源
PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"

echo ">> 构建镜像 ${APP}:latest"
docker build --build-arg PIP_INDEX_URL="${PIP_INDEX_URL}" -t "${APP}:latest" .

# 先停删自身旧容器(幂等),再找空闲端口:否则旧端口每次部署都被跳过,
# 端口会一路漂移(8890→8891→8897…),预留区间很快耗尽(见 PROGRESS GOTCHAS)
docker rm -f "${APP}" 2>/dev/null || true

port_in_use() {
  ss -ltnH 2>/dev/null | grep -q ":$1 " && return 0
  docker ps --format "{{.Ports}}" 2>/dev/null | grep -q ":$1->" && return 0
  return 1
}

PORT=""
for p in $(seq "${PORT_BASE}" "${PORT_MAX}"); do
  if ! port_in_use "$p"; then
    PORT="$p"
    break
  fi
done
[ -z "$PORT" ] && { echo "预留端口区间 ${PORT_BASE}-${PORT_MAX} 已全部占用,部署中止"; exit 1; }
echo ">> 部署到主机端口 ${PORT}"

docker run -d --name "${APP}" --restart unless-stopped -p "${PORT}:8888" "${APP}:latest"

sleep 3
curl -fsS "http://localhost:${PORT}${HEALTH_PATH}"
echo ""
echo ">> 部署成功:http://localhost:${PORT}${HEALTH_PATH}"
