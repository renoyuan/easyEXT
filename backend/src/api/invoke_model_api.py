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


invoke_model_router = APIRouter(prefix="/invoke_model",tags=["invoke_model"])

"""
1 上传文件抽取要素
TODO 匹配场景 1 入库
2 查询历史数据
"""
    
# ocr 识别 post ok
@invoke_model_router.post("/extract")
async def extract( scene: Optional[int], originalFiles: List[UploadFile] ,model = Depends(get_model)):
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
    key_list=["客户","基金名称","基金代码", "申请时间","确认时间", "基金转换金额", "基金转换份额", "交易类别", "手续费", "网点"]
    data = model.extract(await uploadfile_to_ndarray(originalFiles[0]),key_list)

    logger.info(f"{scene} 识别结果 {data}")
    
    # 返回 task id
    return gen_response(200, {"taskSns": data})


 
