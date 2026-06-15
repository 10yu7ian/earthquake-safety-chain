from datetime import datetime, timedelta, timezone
from typing import Tuple

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter()

# 中国大陆无夏令时，固定 UTC+8；避免 Windows 未装 tzdata 时 ZoneInfo 失败
_TZ_BEIJING = timezone(timedelta(hours=8))


def _require_auth(current_user):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


def _beijing_today_event_window_utc_naive() -> Tuple[datetime, datetime]:
    """北京时间当日 00:00:00 至当前时刻，转为 UTC naive 与 events.created_at（按 UTC 存库）比较。"""
    now_utc = datetime.now(timezone.utc)
    now_bj = now_utc.astimezone(_TZ_BEIJING)
    start_bj = now_bj.replace(hour=0, minute=0, second=0, microsecond=0)
    start_utc_naive = start_bj.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc_naive = now_utc.replace(tzinfo=None)
    return start_utc_naive, end_utc_naive


@router.get("/api/statistics", response_model=schemas.StatisticsResponse)
def get_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    start_naive, end_naive = _beijing_today_event_window_utc_naive()
    stats = crud.get_statistics(
        db,
        event_window_start=start_naive,
        event_window_end=end_naive,
    )
    return schemas.StatisticsResponse(**stats)

