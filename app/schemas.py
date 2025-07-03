import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class BaseResponse(BaseModel):
    message: str


# Auth schemas
class RegistrationRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    verified: bool


class VerificationRequest(BaseModel):
    pass  # No data needed for verification request


class VerificationResponse(BaseModel):
    message: str
    code: str


class UserUnverified(BaseModel):
    id: uuid.UUID
    name: str


class User(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


# Post schemas
class PostView(BaseModel):
    id: uuid.UUID
    content: str
    author: User
    likes: int
    liked: bool
    time: datetime.datetime


class PostCreate(BaseModel):
    content: str


class PostEdit(BaseModel):
    id: uuid.UUID
    content: str


class PostAction(BaseModel):
    id: uuid.UUID
