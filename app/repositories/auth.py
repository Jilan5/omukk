from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import random
import string

from app import schemas
from app.models import User
from app.security import create_jwt_token, get_password_hash, verify_password
from app.redis_client import get_redis


def register(
    request: schemas.RegistrationRequest, db: Session
) -> schemas.BaseResponse:
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    user = User(
        name=request.name,
        email=request.email,
        password_hash=get_password_hash(request.password),
    )

    db.add(user)
    db.commit()

    return schemas.BaseResponse(message="Registration successful")


def login(request: schemas.LoginRequest, db: Session):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    token = create_jwt_token({"user_id": str(user.id)})

    return schemas.LoginResponse(token=token, verified=user.is_verified)


def send_verification_code(
    user: schemas.User, db: Session
) -> schemas.VerificationResponse:
    """Generate and store a 6-digit verification code in Redis"""
    # Generate 6-digit code
    code = "".join(random.choices(string.digits, k=6))

    # Store in Redis with 10 minute expiration
    redis_client = get_redis()
    redis_key = f"verify:{user.id}"
    redis_client.set(redis_key, code, ex=600)  # 600 seconds = 10 minutes

    # Print code to console for testing
    print(f"Verification code for user {user.email}: {code}")

    return schemas.VerificationResponse(
        message="Verification code sent successfully", code=code  # For simplicity, return the code in response
    )


def verify_code(code: str, user: schemas.User, db: Session) -> schemas.BaseResponse:
    """Verify the provided code and mark user as verified"""
    redis_client = get_redis()
    redis_key = f"verify:{user.id}"

    # Get stored code from Redis
    stored_code = redis_client.get(redis_key)

    if not stored_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired or not found",
        )

    if stored_code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code",
        )

    # Mark user as verified
    db_user = db.query(User).filter(User.id == user.id).first()
    if db_user:
        db_user.is_verified = True
        db.commit()

    # Delete the verification code from Redis
    redis_client.delete(redis_key)

    return schemas.BaseResponse(message="User verified successfully")
