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
from pathlib import Path

from fastapi import UploadFile
from PIL import Image
import numpy as np
import io
from .response_code import gen_response
from db.op_db import OpTasks,OpTaskresults,OpScenes
from utils.types_enum import TaskStatusEnum,FileTypeEnum,TaskPhaseEnum,FileStatusEnum
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
def get_fdfs(request: Request):
    return request.app.state.fdfs

def get_db_engine(request: Request):
    return request.app.state.db_engine

def get_tools(request: Request):
    tools = {}
    tools["fdfs"] = request.app.state.fdfs
    tools["db_engine"] = request.app.state.db_engine
    tools["scenes"] = request.app.state.scenes
    tools["model"] = request.app.state.model
    return tools

invoke_model_router = APIRouter(prefix="/invoke_model",tags=["invoke_model"])

"""
1 上传文件抽取要素
TODO 匹配场景 1 入库
2 查询历史数据
"""
    
# ocr 识别 post ok
@invoke_model_router.post("/extract")
async def extract(  originalFiles: List[UploadFile] ,scene_id: Optional[int] = None,scene_lable: Optional[str] = None,tools = Depends(get_tools)):

    """
    上传文件抽取要素
    """
    fdfs = tools["fdfs"]
    db_engine = tools["db_engine"]
    scenes = tools["scenes"]
    model = tools["model"]
    
    print(f"scene_lable is {scene_lable} scenes is {scenes.keys()}")
    
    if not scene_id and not scene_lable:
        return gen_response(619, {"message": "场景不存在"})
    
    if scene_id:
        scene = OpScenes(db_engine).query_scene(scene_id=scene_id)
        scene_lable = scene.scene_name if scene else ""
    else:
        scene = OpScenes(db_engine).query_scene(scene_name=scene_lable)
        
    if not scene:
        return gen_response(619, {"message": "场景不存在"})
        
    scene_name = scene.scene_name

    if scene_name in scenes:
        key_list = scenes[scene_name]
    else:
        return gen_response(619, {"message": "场景不存在"})
    
    # 业务逻辑
    
    
    
    # 1 任务入库
    task = OpTasks(db_engine).add_task(scene_id=scene.id,status=TaskStatusEnum.PENDING.value,phase=TaskPhaseEnum.PRE_PROCESSING.value)
    
    # 2 文件入库
    file_count = len(originalFiles)
    for page,originalFile in enumerate(originalFiles):
        content = await originalFile.read() 
        filename = originalFile.filename
        
        file_extension_pathlib = Path(filename).suffix[1:] 
        file_id = fdfs.upload_by_buffer(content, file_extension_pathlib) # 文件流上传
        if not file_id :
            return gen_response(619, {"message": "文件上传失败"})
        else:
            file_type = FileTypeEnum.get_file_type_by_suffix(file_extension_pathlib)
        OpTasks(db_engine).add_taskfile(task_id=task.id,file_id=file_id,status =FileStatusEnum.ORIGINAL.value ,file_type=file_type,file_name=filename,taltol_page=file_count,page=page)  
      
    
    # TODO 异步处理
    # 3 模型调用
    OpTasks(db_engine).update_task(task_id=task.id,status=TaskPhaseEnum.MODEL_PROCESSING.value,phase=TaskPhaseEnum.MODEL_PROCESSING.value)
    data = None
    # data = model(await uploadfile_to_ndarray(originalFiles[0]),key_list)
    
   
    # 5 状态更新&结果入库
    
    OpTaskresults(db_engine).add_taskresult(task_id=task.id,extracted_data=data,data_status=TaskStatusEnum.COMPLETED.value)

    OpTasks(db_engine).update_task(task_id=task.id,status=TaskStatusEnum.COMPLETED.value,phase=TaskStatusEnum.COMPLETED.value)

    logger.info(f"{scene_lable} 识别结果 {data}")
    
    # 6 返回结果
    return gen_response(200, {"taskSns": data})


 
if __name__ == "__main__":
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(invoke_model_router)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
