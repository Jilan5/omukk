from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, post

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index() -> str:
    return "Version 0.1.0"


app.include_router(auth.router)
app.include_router(post.router)
