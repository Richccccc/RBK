"""FastAPI 入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .init_db import init_db
from .routers import auth, guestbook, health, posts, sheets, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时自动建库建表并写入默认管理员账号（幂等，只执行一次）
    init_db()
    yield


app = FastAPI(title="个人博客 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(sheets.router, prefix="/api")
app.include_router(guestbook.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "个人博客后端运行中"}