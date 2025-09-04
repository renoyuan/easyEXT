#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend api
# CREATE_TIME: 2024/3/20 11:46
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 10 个接口
from asyncio import Task
import json
from typing import Optional,List,Union

from fastapi import APIRouter, UploadFile, Request, Depends
from loguru import logger


from fastapi import UploadFile
from PIL import Image
import numpy as np
import io

from sqlalchemy.sql import elements
from .response_code import gen_response

from db.op_db import OpTasks,OpTaskresults,OpScenes


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

def get_db_engine(request: Request):
    return request.app.state.db_engine
"""
1 场景查询
2 任务列表查询
3 任务详情查询
"""
    

@query_router.get("/scenes")
async def query_scenes( db_engine = Depends(get_db_engine)):
    """
        场景查询
        [
            {"class_id":"1","class_name":"金融单据",
            "scenes": [
                {"scene":1,"name":"基金转换"},
                {"scene":2,"name":"基金转换"}
            ]}]
    """
    
    scenes = []
    scenes = OpScenes(db_engine).query_all_scenes()
    logger.info(f"{scenes} 识别结果 {scenes}")
    
    # 返回 task id
    return gen_response(200, {"scenes": scenes})


@query_router.get("/tasks")
async def query_tasks(scene_id:int=None,status:int=None,page:int=1,page_size:int=20,db_engine = Depends(get_db_engine)):



    """
    任务列表查询
    """
    page_info = [{}]
    tasks,total = OpTasks(db_engine).select_task(scene_id=scene_id,status=status,page=page,page_size=page_size)
    page_info = tasks
    logger.info(f"{page_info} 识别结果 {page_info}")
    # 返回 task id
    return gen_response(200, {"page_info": page_info})



@query_router.get("/task_info")
async def query_task_info( task_id: str|int ,db_engine = Depends(get_db_engine)):


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
    task_info = OpTaskresults(db_engine).query_taskresult(int(task_id))
    scene_elements = OpTasks(db_engine).query_element(int(task_id))
    # 要素信息 场景配置 模板 list
    element_config = scene_elements["element_config"]
    extracted_data =task_info["extracted_data"]

    logger.info(f"{task_id} element_config {element_config} 识别结果 {task_info}")
    return gen_response(200, {"element_config":element_config,"task_info": [extracted_data]})



 
