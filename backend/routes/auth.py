import uuid
from datetime import datetime, timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.database import User, Session as DBSession, get_db
from middleware.auth_middleware import get_current_user
from config.settings import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def _create_refresh_token(user_id: str, db: Session) -> str:
    # Invalidate existing sessions (single-session system)
    db.query(DBSession).filter(DBSession.user_id == user_id).delete()

    refresh_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    session = DBSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()
    return refresh_token


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        name=body.name,
        email=body.email,
        hashed_password=pwd_context.hash(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = _create_access_token(user.id)
    refresh_token = _create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd_context.verify(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = _create_access_token(user.id)
    refresh_token = _create_refresh_token(user.id, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(DBSession).filter(DBSession.user_id == current_user.id).delete()
    db.commit()
    return {"message": "Logged out"}


@router.post("/refresh")
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    session = db.query(DBSession).filter(DBSession.refresh_token == body.refresh_token).first()
    if not session or session.expires_at < datetime.utcnow():
        if session:
            db.delete(session)
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    access_token = _create_access_token(session.user_id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email}
