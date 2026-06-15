from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

import crud
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter()


def _require_auth(current_user):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


@router.get("/api/devices")
def get_devices(
    skip: int = 0,
    limit: int = 100,
    community: Optional[str] = None,
    device_status: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    devices = crud.get_devices(
        db=db,
        skip=skip,
        limit=limit,
        community=community,
        status=device_status,
    )
    return devices


@router.post("/api/devices")
def create_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    return crud.create_device(db=db, device=device)


@router.put("/api/devices/{device_id}")
def update_device(
    device_id: str,
    device_update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    updated_device = crud.update_device(
        db=db,
        device_id=device_id,
        device_update=device_update,
    )
    if not updated_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return updated_device

