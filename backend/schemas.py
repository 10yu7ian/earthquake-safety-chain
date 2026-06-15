from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    name: str
    location: Optional[str] = None
    community: Optional[str] = None
    status: Optional[str] = None


class DeviceCreate(DeviceBase):
    id: str


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    community: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[datetime] = None


class DeviceInDB(DeviceBase):
    id: str
    last_seen: Optional[datetime] = None
    created_at: datetime

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    device_id: str
    event_type: str
    acc_max: Optional[float] = None
    details: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventInDB(EventBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ControlCommand(BaseModel):
    device_id: str
    command: str


class StatisticsResponse(BaseModel):
    total_devices: int
    online_devices: int
    today_events: int
    today_triggers: int
    alert_count: int = Field(
        ...,
        description="status 为 triggered 的设备数量，与设备管理「已触发」一致",
    )

