# 地震安链 · 燃气安全云边协同系统

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

地震安链是一套面向燃气安全的近场地震应急防护系统。它通过部署在燃气管道入口的边缘智能终端，在 P 波到达后 3ms 内预测 S 波破坏强度并自动切断燃气，填补震中 20km 近场盲区的控制真空。同时，系统通过云边协同架构，为燃气公司提供设备管理、事件记录、远程复位、数据报表等能力，并为居民提供独立的安全看板。

https://earthquake-safety-chain.vercel.app

## 系统架构

```
┌─────────────────┐  WiFi  ┌─────────────────┐  HTTP  ┌─────────────────┐
│  边缘智能终端   │ ──────→ │    云端平台     │ ←────→ │    多端应用     │
│ (树莓派+MEMS)  │  事件上报 │ (FastAPI+SQLite)│ API调用 │  (Vue3驾驶舱)  │
│                 │ ←────── │                 │ ──────→ │  (居民看板)    │
│   本地AI决策   │  指令轮询 │    指令队列     │        │                 │
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

- **L1 边缘终端**：ADXL345 加速度计 + XGBoost 模型，离线推理，GPIO 驱动电磁阀切断。
- **L2 云端平台**：FastAPI + SQLite，接收事件上报，维护设备状态，提供远程复位/自检指令队列。
- **L3 多端应用**：Vue3 + Element Plus 驾驶舱（设备管理、事件记录、报表） + 居民看板。

## 核心功能

### 燃气公司驾驶舱
- 实时 KPI 卡片（总设备数、在线数、今日事件、拦截次数）
- 设备管理（卡片网格、状态筛选、编辑、自检、远程复位）
- 事件记录（分页筛选、CSV 导出、详情查看）
- 数据报表（事件趋势、社区排名等 ECharts 图表）

### 居民看板
- 设备状态大卡片（正常 / 已切断 / 离线）
- 累计拦截次数、上次触发时间
- 一键自检 + 灾后指引

### 微信告警
- 异常事件（`shutdown`）通过 Server酱 实时推送到管理员/居民微信

## 技术栈

| 层级   | 技术选型                                                        |
| ------ | --------------------------------------------------------------- |
| 前端   | Vue 3 + Vite + Element Plus + ECharts + Axios                   |
| 后端   | FastAPI + SQLite + JWT + python-jose + passlib + uvicorn        |
| 边缘端 | 树莓派 5B + ADXL345 + XGBoost + RPi.GPIO                        |
| 部署   | 本地开发 / 自建服务器                                           |
| 推送   | Server酱（微信）                                                |

## 目录结构

```
earthquake-safety-chain/
├── frontend/   # Vue3 前端项目
├── backend/    # FastAPI 后端项目
├── mock/       # 树莓派模拟脚本
├── .gitignore
└── README.md
```

## 本地运行

### 1. 前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 2. 后端（需 Python 3.9+）

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 访问 http://localhost:8000/docs 查看 API 文档
```

### 3. 模拟脚本（可选，用于测试事件上报）

```bash
cd mock
pip install requests
python simulate_pi.py
```

## 环境变量（后端）

创建 `backend/.env` 文件，可配置以下变量（可选）：

```
SERVERCHAN_KEY=你的Server酱SendKey   # 用于微信推送，不配置则跳过推送
```

## 项目状态

- ✅ 前端界面完整（深色科技风，玻璃拟态）
- ✅ 后端 API 实现（设备管理、事件上报、远程复位、统计）
- ✅ 前后端联调通过，数据实时同步
- ✅ 微信推送集成（Server酱）
- ✅ 模拟脚本支持随机事件 + 第14次强制触发演示
- ⏳ 实际硬件部署与振动台实验（进行中）

## 许可证

本项目仅用于技术展示与学习交流，未经许可不得用于商业用途。详见 LICENSE 文件。

## 致谢

感谢所有参与项目设计、开发和测试的团队成员。
