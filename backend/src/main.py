#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend main
# CREATE_TIME: 2024/3/20 11:58
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import os, sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
print(sys.path)

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


from api import api_router
from utils.invoke_model import InvokeModel


env_path = r".env"
load_dotenv(env_path)

from sqlmodel import Session, SQLModel, create_engine
   



@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    # 启动时初始化模型
    app.state.model =InvokeModel("model")  # 替换为实际加载函数
    # 加载DB 
    DbConfig = json.loads(os.getenv("DbConfig")) 
    engine = create_engine(f"postgresql+psycopg2://{DbConfig['user']}:{DbConfig['password']}@{DbConfig['host']}:{DbConfig['port']}/{DbConfig['database']}")
    SQLModel.metadata.create_all(engine)
    app.state.db_engine = engine
    
    scenesPath = os.getenv("scenesPath")
    with open(scenesPath, "r", encoding="utf-8") as f:
        app.state.scenes = json.load(f)

    yield  # 应用运行期间保持模型在内存中
    
    # 关闭时清理资源
    app.state.model = None
    app.state.db_engine = None
 
# 创建 FastAPI 应用实例

app = FastAPI(docs_url="/docs",redoc_url="/redoc",lifespan=lifespan)
# 定义路由

app.include_router(api_router)

   

# 鉴权逻辑  tasksN --> user_id
excluded_routes = ["/exuser/user/login","/docs"]
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",

]
# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")

# 如果运行的是这个文件，则启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)