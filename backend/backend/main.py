#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend main
# CREATE_TIME: 2024/3/20 11:58
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
print(sys.path)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import router, auth_middleware


# 创建 FastAPI 应用实例
app = FastAPI()

# 定义路由
app.include_router(router)

# 鉴权逻辑  tasksN --> user_id
excluded_routes = ["/exuser/user/login","/docs"]
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
# 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(auth_middleware)

# 如果运行的是这个文件，则启动 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)