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
from db.op_db import OpTasks,OpTaskresults,OpScenes

async def uploadfile_to_ndarray(file: UploadFile) -> np.ndarray:
    content = await file.read()  # 读取二进制数据
    img = Image.open(io.BytesIO(content))  # 通过内存流加载
    # 统一转换为 RGB 格式（避免调色板/灰度图维度问题）
    if img.mode in ("P", "L", "1", "RGBA"):
        img = img.convert("RGB")
    img_array = np.array(img)
    print("图像维度:", img_array.shape) 
    return img_array  # 转换为 uint8 数组 (H×W×3)

def get_model(request: Request):
    return request.app.state.model 

def get_scenes(request: Request):
    return request.app.state.scenes
def get_db_engine(request: Request):
    return request.app.state.db_engine

invoke_model_router = APIRouter(prefix="/invoke_model",tags=["invoke_model"])

"""
1 上传文件抽取要素
TODO 匹配场景 1 入库
2 查询历史数据
"""
    
# ocr 识别 post ok
@invoke_model_router.post("/extract")
async def extract(  originalFiles: List[UploadFile] ,scene_id: Optional[int] = None,scene_lable: Optional[str] = None,model = Depends(get_model),scenes = Depends(get_scenes),db_engine = Depends(get_db_engine)):

    """
    上传文件抽取要素
    """
    
    print(f"scene_lable is {scene_lable} scenes is {scenes.keys()}")
    
    if not scene_id and not scene_lable:
        return gen_response(619, {"message": "场景不存在"})
    
    if scene_id:
        scene = OpScenes(db_engine).query_scene(id=scene_id)
    else:
        scene = OpScenes(db_engine).query_scene(scene_name=scene_lable)
        
        
    scene_name = scene.scene_name

    if scene_name in scenes:
        key_list = scenes[scene_name]
    else:
        return gen_response(619, {"message": "场景不存在"})
    
    task = OpTasks(db_engine).add_task(scene_id=scene.id,status=0,task_status=0)

    data = model(await uploadfile_to_ndarray(originalFiles[0]),key_list)
    OpTaskresults(db_engine).add_taskresult(task_id=task.id,extracted_data=data,data_status="1")

    OpTasks(db_engine).update_task(task_id=task.id,status=1,task_status=1)

    logger.info(f"{scene_lable} 识别结果 {data}")
    
    # 返回 task id
    return gen_response(200, {"taskSns": data})


 
if __name__ == "__main__":
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(invoke_model_router)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
