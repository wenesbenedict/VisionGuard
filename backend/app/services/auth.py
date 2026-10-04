import hashlib
import os
import time
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

SECRET = os.getenv("JWT_SECRET", "visionguard-dev-secret")
ALGORITHM = "HS256"
TOKEN_HOURS = 12


def hash_password(password: str, salt: str = None) -> str:
    salt = salt or os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split(":", 1)
    except ValueError:
        return False
    return hash_password(password, salt) == stored


def create_token(user: models.User) -> str:
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(authorization[7:], SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(models.User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    def dep(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return dep


def seed_admin(db: Session):
    if db.query(models.User).count() == 0:
        db.add(models.User(
            name="Admin",
            email="admin@visionguard.local",
            password_hash=hash_password("admin123"),
            role="ADMIN",
        ))
        db.commit()
