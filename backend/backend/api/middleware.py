#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend middleware
# CREATE_TIME: 2024/3/27 16:26
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: fastapi 中间件 有点傻逼 尽量使用 Depends 处理上下文

from fastapi import FastAPI, Request, Depends, Header
from utils.gen_token import decode_jwt_token
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
excluded_routes = ["/exuser/user/login","/docs","/openapi.json"]

class GlobalVariable:
    def __init__(self):
        self.user_id = None

class PicItem(BaseModel):
    pages: list

    
def get_user_info(token):
    payload = decode_jwt_token(token)
    user_id = payload["user_id"]
    return {
        "user_id": user_id,
        "requests_id": str(uuid.uuid4())
    }

def api_ocr_depends(token: str=Header(...)):
    payload = decode_jwt_token(token)
    user_id = payload["user_id"]
    return {
        "user_id": user_id,
        "requests_id": str(uuid.uuid4())

    }
async def auth_middleware(request: Request, call_next):

    """鉴权中间件"""
    if request.scope.get("path") not in excluded_routes:
        token = request.headers.get("token")
        payload = decode_jwt_token(token)

        if not payload:
            return JSONResponse({"code": "501", "message": "传入token 错误", "status": 0})
    response = await call_next(request)
    return response

