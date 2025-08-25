#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend __init__.py
# CREATE_TIME: 2024/3/20 11:41
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
# from .api import router
from fastapi import APIRouter
from .invoke_model_api import invoke_model_router
from .query_api import query_router

# from .middleware import auth_middleware
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(invoke_model_router)
api_router.include_router(query_router)
