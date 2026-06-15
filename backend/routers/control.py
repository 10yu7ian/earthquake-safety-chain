from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user
from schemas import ControlCommand

router = APIRouter()

# device_id -> (command, expire_at)
command_queue: Dict[str, Tuple[str, datetime]] = {}


def _require_auth(current_user):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


@router.post("/api/control")
def queue_command(
    payload: ControlCommand,
    current_user=Depends(get_current_user),
):
    _require_auth(current_user)
    expire_at = datetime.utcnow() + timedelta(seconds=30)
    command_queue[payload.device_id] = (payload.command, expire_at)
    return {"status": "command queued"}


@router.get("/api/control/poll")
def poll_command(device_id: str):
    item: Optional[Tuple[str, datetime]] = command_queue.pop(device_id, None)
    if not item:
        return {"command": None}

    command, expire_at = item
    if expire_at < datetime.utcnow():
        return {"command": None}
    return {"command": command}

