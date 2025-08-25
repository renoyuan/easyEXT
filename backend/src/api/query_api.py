#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend api
# CREATE_TIME: 2024/3/20 11:46
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 10 个接口
import json
from typing import Optional,List,Union

from fastapi import APIRouter, UploadFile, Request, Depends
from loguru import logger


from fastapi import UploadFile
from PIL import Image
import numpy as np
import io
from .response_code import gen_response
# from .middleware import api_ocr_depends,PicItem
# from .file_deal import FileDeal

async def uploadfile_to_ndarray(file: UploadFile) -> np.ndarray:
    content = await file.read()  # 读取二进制数据
    img = Image.open(io.BytesIO(content))  # 通过内存流加载
    # 统一转换为 RGB 格式（避免调色板/灰度图维度问题）
    if img.mode in ("P", "L", "1"):
        img = img.convert("RGB")
    img_array = np.array(img)
    print("图像维度:", img_array.shape) 
    return img_array  # 转换为 uint8 数组 (H×W×3)
def get_model(request: Request):
    return request.app.state.model 


query_router = APIRouter(prefix="/query",tags=["query"])


"""
1 场景查询
2 任务列表查询
3 任务详情查询
"""
    

@query_router.get("/scenes")
async def query_scenes( ):
    f"""
        场景查询
        [
            {"class_id":"1","class_name":"金融单据",
            "scenes": [
                {"scene":1,"name":"基金转换"},
                {"scene":2,"name":"基金转换"}
            ]}]
    """
    # TODO query scene
    scenes = []

    logger.info(f"{scenes} 识别结果 {scenes}")
    
    # 返回 task id
    return gen_response(200, {"scenes": scenes})


@query_router.get("/tasks")
async def query_tasks(page: int = 1, page_size: int = 10,other_info: str = None):

    """
    任务列表查询
    """
    page_info = [{}]
    logger.info(f"{page_info} 识别结果 {page_info}")
    # 返回 task id
    return gen_response(200, {"page_info": page_info})



@query_router.get("/task_info")
async def query_task_info( task_id: str ):

    """
        res = {
        "ori_info": {
            "file_length": 0,
            "file_info": []
        },
        "deal_info": {
            "file_length": 0,
            "file_info": []
        }
    }
    """
    task_info = {}


    logger.info(f"{task_info} 识别结果 {task_info}")
    
    # 返回 task id
    return gen_response(200, {"task_info": task_info})


 
