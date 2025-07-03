from datetime import UTC, datetime, timedelta

import jwt
from bcrypt import checkpw, gensalt, hashpw
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import schemas
from app.database import SessionLocal
from app.models import User
from app.settings import settings


def get_password_hash(password: str) -> str:
    return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_jwt_token(data: dict) -> str:
    _ed = timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    iat = datetime.now(UTC)
    exp = iat + _ed
    token_payload = data
    token_payload.update({"iat": iat, "exp": exp})

    token = jwt.encode(
        token_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token


def get_user_from_token(token: str) -> schemas.User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )

    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.User.model_validate(user)


def get_user(
    authorization: HTTPAuthorizationCredentials = Security(HTTPBearer()),
) -> schemas.User:
    if authorization.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Invalid authentication scheme"
        )

    token = authorization.credentials
    return get_user_from_token(token)


def get_user_strict(user: schemas.User = Depends(get_user)) -> schemas.User:
    if not user.is_verified:
        raise HTTPException(status_code=401, detail="User not verified")

    return user
