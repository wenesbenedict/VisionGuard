import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session

from .. import models
from ..config import JWT_SECRET
from ..database import get_db

ALGORITHM = "HS256"
TOKEN_HOURS = 12


def validate_secret() -> None:
    if len(JWT_SECRET.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET must be configured with at least 32 bytes")


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split(":", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def create_token(user: models.User) -> str:
    validate_secret()
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "pwdv": hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest(),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def get_user_from_token(db: Session, token: str) -> models.User:
    validate_secret()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    current_password_version = hashlib.sha256(user.password_hash.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(str(payload.get("pwdv", "")), current_password_version):
        raise HTTPException(status_code=401, detail="Session is no longer valid")
    return user


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> models.User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    return get_user_from_token(db, authorization[7:])


def websocket_token(protocol_header: str) -> str | None:
    for protocol in protocol_header.split(","):
        protocol = protocol.strip()
        if protocol.startswith("vg-auth."):
            token = protocol[len("vg-auth."):]
            return token or None
    return None


def require_role(*roles: str):
    def dep(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return dep
