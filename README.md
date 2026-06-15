# 地震安链（Earthquake Safety Chain）

基于物联网与区块链的地震燃气自动切断与预警系统。

## 项目结构

```
earthquake-safety-chain/
├── frontend/   # Vue 3 前端（Vite + Element Plus）
├── backend/    # FastAPI 后端（Python）
├── mock/       # 树莓派模拟脚本（Server酱推送）
└── README.md
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # 填入真实配置
uvicorn main:app --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 模拟脚本

```bash
cd mock
export SERVERCHAN_KEY=your_key_here
python simulate_pi.py
```

## 环境变量说明

| 变量名 | 说明 |
|---|---|
| `SECRET_KEY` | JWT 签名密钥 |
| `SERVERCHAN_SENDKEY` | Server酱微信推送 Key |
| `ADMIN_PASSWORD` | 管理员初始密码 |
| `USER_PASSWORD` | 普通用户初始密码 |
| `SERVERCHAN_KEY` | mock 脚本推送 Key |
