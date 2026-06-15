import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import crud
import schemas
from auth import get_password_hash
from database import Base, SessionLocal, engine
from routers import auth, control, devices, events, statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(events.router)
app.include_router(control.router)
app.include_router(statistics.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def backend_home():
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>地震安链 · 后端服务</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 36rem; margin: 3rem auto; padding: 0 1.25rem; color: #1a1a1a; }
    h1 { font-size: 1.35rem; font-weight: 600; }
    p { color: #444; line-height: 1.6; }
    ul { padding-left: 1.2rem; line-height: 2; }
    a { color: #2563eb; }
  </style>
</head>
<body>
  <h1>地震安链后端 API</h1>
  <p>服务已运行。可从下方入口在浏览器中调试与查看接口。</p>
  <ul>
    <li><a href="/docs">Swagger 交互文档（/docs）</a></li>
    <li><a href="/redoc">ReDoc 文档（/redoc）</a></li>
    <li><a href="/openapi.json">OpenAPI 原始 JSON</a></li>
  </ul>
</body>
</html>"""


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_pw = os.getenv("ADMIN_PASSWORD", "")
        user_pw = os.getenv("USER_PASSWORD", "")
        if not admin_pw or not user_pw:
            print("警告: 环境变量 ADMIN_PASSWORD / USER_PASSWORD 未设置，跳过默认用户初始化")
        else:
            if not crud.get_user_by_username(db, "admin"):
                crud.create_user(
                    db=db,
                    username="admin",
                    password_hash=get_password_hash(admin_pw),
                    role="admin",
                )
            if not crud.get_user_by_username(db, "user"):
                crud.create_user(
                    db=db,
                    username="user",
                    password_hash=get_password_hash(user_pw),
                    role="resident",
                )

        demo_devices = [
            {
                "id": "LM-1001",
                "name": "东门节点A1",
                "location": "东门围栏北侧",
                "community": "龙门一社区",
            },
            {
                "id": "LM-1002",
                "name": "东门节点A2",
                "location": "东门围栏南侧",
                "community": "龙门一社区",
            },
            {
                "id": "LM-1003",
                "name": "西门监测点",
                "location": "西门停车场",
                "community": "龙门二社区",
            },
            {
                "id": "LM-1004",
                "name": "北门阀室",
                "location": "北门桥下",
                "community": "龙门二社区",
            },
            {
                "id": "LM-1005",
                "name": "中心站",
                "location": "物业大楼东侧",
                "community": "龙门一社区",
            },
        ]

        for item in demo_devices:
            if crud.get_device(db, item["id"]):
                continue
            crud.create_device(
                db=db,
                device=schemas.DeviceCreate(
                    id=item["id"],
                    name=item["name"],
                    location=item["location"],
                    community=item["community"],
                    status="online",
                ),
            )
    finally:
        db.close()

