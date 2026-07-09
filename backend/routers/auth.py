from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import authenticate_user, create_access_token
from database import get_db
from schemas import Token, UserLogin

router = APIRouter()


@router.post("/api/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

