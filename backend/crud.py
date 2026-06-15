from datetime import datetime
from typing import Dict, Optional, Union

from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas


def get_device(db: Session, device_id: str):
    return db.query(models.Device).filter(models.Device.id == device_id).first()


def get_devices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    community: Optional[str] = None,
    status: Optional[str] = None,
):
    query = db.query(models.Device)
    if community:
        query = query.filter(models.Device.community == community)
    if status:
        query = query.filter(models.Device.status == status)
    return query.offset(skip).limit(limit).all()


def create_device(db: Session, device: schemas.DeviceCreate):
    db_device = models.Device(
        id=device.id,
        name=device.name,
        location=device.location,
        community=device.community,
        status=device.status,
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(
    db: Session,
    device_id: str,
    device_update: Union[schemas.DeviceUpdate, Dict],
):
    db_device = get_device(db, device_id)
    if not db_device:
        return None

    if isinstance(device_update, dict):
        update_data = device_update
    else:
        dump = getattr(device_update, "model_dump", None)
        update_data = (
            dump(exclude_unset=True) if callable(dump) else device_update.dict(exclude_unset=True)
        )

    for key, value in update_data.items():
        setattr(db_device, key, value)

    db.commit()
    db.refresh(db_device)
    return db_device


def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    device_id: Optional[str] = None,
    event_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    query = db.query(models.Event)
    if device_id:
        query = query.filter(models.Event.device_id == device_id)
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if start_time:
        query = query.filter(models.Event.created_at >= start_time)
    if end_time:
        query = query.filter(models.Event.created_at <= end_time)

    return query.order_by(models.Event.created_at.desc()).offset(skip).limit(limit).all()


def create_event(db: Session, event: schemas.EventCreate):
    db_event = models.Event(
        device_id=event.device_id,
        event_type=event.event_type,
        acc_max=event.acc_max,
        details=event.details,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    role: str = "user",
    device_id: Optional[str] = None,
):
    db_user = models.User(
        username=username,
        password_hash=password_hash,
        role=role,
        device_id=device_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_statistics(
    db: Session,
    *,
    event_window_start: datetime,
    event_window_end: datetime,
):
    """event_window_* 为 UTC 的 naive datetime，与库中 created_at（按 UTC 存储）比较。
    在线设备数以设备表 status=='online' 为准（与设备管理一致），不依赖 last_seen。
    """
    total_devices = db.query(func.count(models.Device.id)).scalar() or 0
    online_devices = (
        db.query(func.count(models.Device.id))
        .filter(models.Device.status == "online")
        .scalar()
        or 0
    )
    today_events = (
        db.query(func.count(models.Event.id))
        .filter(models.Event.created_at >= event_window_start)
        .filter(models.Event.created_at <= event_window_end)
        .scalar()
        or 0
    )
    today_triggers = (
        db.query(func.count(models.Event.id))
        .filter(models.Event.created_at >= event_window_start)
        .filter(models.Event.created_at <= event_window_end)
        .filter(models.Event.event_type == "shutdown")
        .scalar()
        or 0
    )
    alert_count = (
        db.query(func.count(models.Device.id))
        .filter(models.Device.status == "triggered")
        .scalar()
        or 0
    )

    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "today_events": today_events,
        "today_triggers": today_triggers,
        "alert_count": alert_count,
    }

