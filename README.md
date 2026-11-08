# ops-lab

Docker Compose 部署 Nginx + 应用 + MySQL + Redis，附 Prometheus/Grafana 监控与 Python 巡检脚本。

## 架构

- Nginx `:8080` 反代到 app
- MySQL `:3306` / Redis `:6379`
- Prometheus `:9090` / Grafana `:3000`（admin/admin）
- `scripts/healthcheck.py` 检查容器、HTTP、MySQL、Redis 端口

## 一键启动

```bash
cd compose
docker compose up -d
docker compose ps
curl -s http://127.0.0.1:8080/
python3 ../scripts/healthcheck.py

## 告警演示

```bash
cd compose
docker compose stop node-exporter
# 约 1～2 分钟后
curl -s 'http://127.0.0.1:9090/api/v1/alerts'
docker compose start node-exporter
