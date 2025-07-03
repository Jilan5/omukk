import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import database, schemas
from app.repositories import post
from app.security import get_user, get_user_strict

router = APIRouter(prefix="/posts", tags=["posts"])

get_db = database.get_db


@router.get("/", response_model=list[schemas.PostView])
def get_all_posts(
    user: schemas.User = Depends(get_user), db: Session = Depends(get_db)
):
    return post.get_all_posts(user, db)


@router.get("/{post_id}", response_model=schemas.PostView)
def get_post(
    post_id: uuid.UUID,
    user: schemas.User = Depends(get_user),
    db: Session = Depends(get_db),
):
    return post.get_post(post_id, user, db)


@router.post(
    "/",
    response_model=schemas.PostView,
    status_code=status.HTTP_201_CREATED,
)
def create_post(
    content: schemas.PostCreate,
    user: schemas.User = Depends(get_user_strict),
    db: Session = Depends(get_db),
):
    return post.create_post(user, content, db)


@router.put("/{post_id}", response_model=schemas.PostView)
def edit_post(
    post_id: uuid.UUID,
    content: schemas.PostCreate,
    user: schemas.User = Depends(get_user_strict),
    db: Session = Depends(get_db),
):
    return post.edit_post(post_id, user, content, db)


@router.delete("/{post_id}", response_model=schemas.BaseResponse)
def delete_post(
    post_id: uuid.UUID,
    user: schemas.User = Depends(get_user_strict),
    db: Session = Depends(get_db),
):
    return post.delete_post(post_id, user, db)


@router.post(
    "/{post_id}/like", response_model=schemas.BaseResponse
)
def like_post(
    post_id: uuid.UUID,
    user: schemas.User = Depends(get_user_strict),
    db: Session = Depends(get_db),
):
    return post.toggle_like(post_id, user, db)
