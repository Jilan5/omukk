from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import database, schemas
from app.repositories import auth
from app.security import get_user

router = APIRouter(prefix="", tags=["auth"])

get_db = database.get_db


@router.post(
    "/register",
    response_model=schemas.BaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: schemas.RegistrationRequest, db: Session = Depends(get_db)
):
    return auth.register(request, db)


@router.post("/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    return auth.login(request, db)


@router.get("/me", response_model=schemas.User)
def current_user(user: schemas.User = Depends(get_user)):
    return user


@router.post("/verify", response_model=schemas.VerificationResponse)
def send_verification(
    user: schemas.User = Depends(get_user),
    db: Session = Depends(get_db)
):
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified"
        )
    return auth.send_verification_code(user, db)


@router.get("/verify/{code}", response_model=schemas.BaseResponse)
def verify_user(
    code: str,
    user: schemas.User = Depends(get_user),
    db: Session = Depends(get_db)
):
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already verified"
        )
    return auth.verify_code(code, user, db)
