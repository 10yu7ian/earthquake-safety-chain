import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

import crud
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter()

# 微信推送统一由 longmen-mock/simulate_pi.py 经 Server酱发送；
# 后端不再调用 sctapi.ftqq.com，避免与模拟脚本重复推送。


class EventIngest(BaseModel):
    device_id: str
    event_type: str
    acc_max: Optional[float] = None
    timestamp: datetime


def _require_auth(current_user):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


@router.post("/api/event")
def create_event(payload: EventIngest, db: Session = Depends(get_db)):
    db_device = crud.get_device(db, payload.device_id)
    if not db_device:
        initial_status = "online"
        if payload.event_type == "shutdown":
            initial_status = "triggered"
        elif payload.event_type == "restore":
            initial_status = "online"
        crud.create_device(
            db,
            schemas.DeviceCreate(
                id=payload.device_id,
                name=payload.device_id,
                location=None,
                community=None,
                status=initial_status,
            ),
        )
    else:
        if payload.event_type == "shutdown":
            crud.update_device(
                db,
                payload.device_id,
                {"last_seen": payload.timestamp, "status": "triggered"},
            )
        elif payload.event_type == "restore":
            # 设备状态在写入 restore 事件后再统一更新为 online（见下方）
            pass
        else:
            crud.update_device(
                db,
                payload.device_id,
                {"last_seen": payload.timestamp},
            )

    crud.create_event(
        db,
        schemas.EventCreate(
            device_id=payload.device_id,
            event_type=payload.event_type,
            acc_max=payload.acc_max,
            details=f"timestamp={payload.timestamp.isoformat()}",
        ),
    )

    if payload.event_type == "restore":
        crud.update_device(
            db,
            payload.device_id,
            {"status": "online", "last_seen": payload.timestamp},
        )

    # shutdown 时 Server酱 推送仅由 simulate_pi 发送（标题「【地震安链】地震预警 - 燃气已切断」）

    return {"status": "ok"}


@router.get("/api/events")
def get_events(
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    return crud.get_events(
        db=db,
        skip=skip,
        limit=limit,
        device_id=device_id,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
    )


@router.get("/api/events/export")
def export_events(
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    events = crud.get_events(
        db=db,
        skip=skip,
        limit=limit,
        device_id=device_id,
        event_type=event_type,
        start_time=start_time,
        end_time=end_time,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "device_id", "event_type", "acc_max", "details", "created_at"])
    for item in events:
        writer.writerow(
            [
                item.id,
                item.device_id,
                item.event_type,
                item.acc_max,
                item.details,
                item.created_at.isoformat() if item.created_at else "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=events.csv"},
    )
