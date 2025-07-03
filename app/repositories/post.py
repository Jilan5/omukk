import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.models import Like, Post, User
from app.security import create_jwt_token


def get_all_posts(user: schemas.User, db: Session) -> list[schemas.PostView]:
    _posts = db.query(Post).order_by(Post.created_at.desc()).all()
    posts = []
    for post in _posts:
        author = db.query(User).filter_by(id=post.user_id).first()
        likes = db.query(Like).filter_by(post_id=post.id).count()
        liked = (
            db.query(Like).filter_by(post_id=post.id, user_id=user.id).first()
            is not None
        )

        _post = schemas.PostView(
            id=post.id,
            content=post.content,
            author=schemas.User.model_validate(author),
            likes=likes,
            liked=liked,
            time=post.time,
        )
        posts.append(_post)

    return posts


def get_post(post_id: uuid.UUID, user: schemas.User, db: Session) -> schemas.PostView:
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    
    author = db.query(User).filter_by(id=post.user_id).first()
    likes = db.query(Like).filter_by(post_id=post.id).count()
    liked = (
        db.query(Like).filter_by(post_id=post.id, user_id=user.id).first()
        is not None
    )

    return schemas.PostView(
        id=post.id,
        content=post.content,
        author=schemas.User.model_validate(author),
        likes=likes,
        liked=liked,
        time=post.time,
    )


def create_post(
    user: schemas.User, content: schemas.PostCreate, db: Session
) -> schemas.PostView:
    # Validate that post content is not empty
    if not content.content or content.content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty",
        )
    
    new_post = Post(user_id=user.id, content=content.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    post = schemas.PostView(
        id=new_post.id,
        content=new_post.content,
        author=schemas.User.model_validate(user),
        likes=0,
        liked=False,
        time=new_post.time,
    )

    return post


def edit_post(
    post_id: uuid.UUID, user: schemas.User, content: schemas.PostCreate, db: Session
) -> schemas.PostView:
    # Validate that post content is not empty
    if not content.content or content.content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post content cannot be empty",
        )
    
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    post.content = content.content
    db.commit()
    db.refresh(post)

    likes = db.query(Like).filter_by(post_id=post.id).count()
    liked = (
        db.query(Like).filter_by(post_id=post.id, user_id=user.id).first()
        is not None
    )

    return schemas.PostView(
        id=post.id,
        content=post.content,
        author=schemas.User.model_validate(user),
        likes=likes,
        liked=liked,
        time=post.time,
    )


def delete_post(
    post_id: uuid.UUID, user: schemas.User, db: Session
) -> schemas.BaseResponse:
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    db.delete(post)
    db.commit()

    return schemas.BaseResponse(message="Post deleted")


def toggle_like(
    post_id: uuid.UUID, user: schemas.User, db: Session
) -> schemas.BaseResponse:
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if post.user_id == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't like own post",
        )

    like = db.query(Like).filter_by(post_id=post.id, user_id=user.id).first()
    if like:
        db.delete(like)
        db.commit()
        return schemas.BaseResponse(message="Like removed")

    like = Like(post_id=post.id, user_id=user.id)
    db.add(like)
    db.commit()

    return schemas.BaseResponse(message="Liked")
