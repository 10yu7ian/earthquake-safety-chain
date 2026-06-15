import os

from fastapi import APIRouter, HTTPException, status

from auth import create_access_token
from schemas import Token, UserLogin

router = APIRouter()

_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
_USER_PASSWORD = os.getenv("USER_PASSWORD", "")


@router.post("/api/login", response_model=Token)
def login(payload: UserLogin):
    if _ADMIN_PASSWORD and payload.username == "admin" and payload.password == _ADMIN_PASSWORD:
        role = "admin"
    elif _USER_PASSWORD and payload.username == "user" and payload.password == _USER_PASSWORD:
        role = "resident"
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={
            "sub": payload.username,
            "role": role,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

