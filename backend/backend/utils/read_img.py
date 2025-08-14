"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/utils
CREATE_TIME: 2024-04-12 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note: 读取图片  
"""
from io import BytesIO
import base64

# import cv2
from PIL import Image
import numpy as np

from .fastdfs import fdfs


def read_img_info(img_url=None,img_data=None):
    """
    输入图片链接下载图片
    返回图片b64 以及 长宽信息
    """
    img_info = {}
    if img_url:
        res = fdfs.download_to_buffer(img_url)
        if res ==-1:
            logger.warning("fstdfs faild")
            return None
        img_bytes =  res['Content']
        bytes_io = BytesIO(img_bytes)
        image = Image.open(bytes_io)
        width, height = image.size
        img_b64 = str(base64.b64encode(img_bytes),encoding="utf-8")
        
        img_info["base64"] = img_b64
        img_info["width"] = width
        img_info["height"] = height
        return img_info
    elif img_data:
        pass 
    else:
        pass
    