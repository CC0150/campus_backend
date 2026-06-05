from contextlib import asynccontextmanager

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import Base
import app.models.shop  # noqa: F401
import app.models.dish  # noqa: F401
import app.models.order  # noqa: F401
import app.models.user  # noqa: F401
import app.models.feedback  # noqa: F401

from app.core.database import engine
from app.core.migrate import migrate_db
from app.core.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. 创建不存在的表
    Base.metadata.create_all(bind=engine)
    # 2. 对已存在的表补全缺失的列（不再需要删库）
    migrate_db(engine)
    # 3. 填充初始数据（幂等 — 已有数据则跳过）
    seed_data()
    yield


app = FastAPI(
    title="Campus Ordering System",
    description="校园点餐系统后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1.endpoints import shops, orders, auth, admin, feedback

app.include_router(auth.router, prefix="/api/v1")
app.include_router(shops.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(feedback.router, prefix="/api/v1")
app.include_router(feedback.admin_router, prefix="/api/v1")

# 静态文件服务 — 上传的图片通过 /uploads/ 访问
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
def read_root():
    return {"code": 200, "data": {"message": "Campus Ordering System API"}, "msg": "success"}
