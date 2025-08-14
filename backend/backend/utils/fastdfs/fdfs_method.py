#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: /home/yss/idp_backend/backend/utils/fastdfs
#CREATE_TIME: 2024-03-26 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  
import os, sys, json, time

sys.path.append("/home/reno/idp_ocr/")
sys.path.append("/home/reno/idp_ocr/app_ocr")
sys.path.append("/home/reno/idp_ocr/app_ocr/utils")


from io import BytesIO
from PIL import Image
from loguru import logger

from uni_utils import b2u
from utils.fastdfs import FDFS


def coast_time(func):
    '''
    计算对象执行耗时
    '''
    def fun(*agrs, **kwargs):
        t = time.perf_counter()
        result = func(*agrs, **kwargs)
        logger.info(f'function {func.__name__} coast time: {(time.perf_counter() - t)*1000 :.2f} ms')
        return result
    return fun

fdfs = FDFS()

@coast_time
def download_file(ocr_param, static_folder):
    # 下载文件至本地
    from app_ocr.utils.api_ocr_common import OcrApiCommon
    file_path, output_path = OcrApiCommon.getFilePath(static_folder, ocr_param['file_name'],  ocr_param['task_id'], ocr_param.get('page'))
    ret_download = fdfs.download(file_path, ocr_param['file_id'])
    return file_path, output_path, ret_download

@coast_time
def upload_data(data, data_type='json'):
    if data_type == 'file':
        ret_upload = fdfs.upload(data)
    else:
        if data_type in ['json', 'data', 'dict']:
            if not isinstance(data, bytes):
                data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        elif data_type in ['jpg', 'img', 'png']:
            IO = BytesIO()
            img = Image.fromarray(data)
            img.save(IO, format='PNG')
            data = IO.getvalue()
            # 图片最终转成jpg后缀
            data_type = 'jpg'
        else:
            print('data_type 错误')
            return None
        ret_upload = fdfs.upload_by_buffer(data, file_ext_name=data_type)
    # 检验 fastdfs 操作
    if ret_upload == -1:
        return None
    else:
        result_file_id = b2u(ret_upload['Remote file_id'])
        return result_file_id

if __name__ == '__main__':

    data = "/home/yhy/百年保险资产-净值型保险资管产品申购确认单-0.json"
    aa = fdfs.download_to_buffer(b"group1/M00/00/00/wKgBiGVxVEmAXYMWAAPXUTTCAHs031.jpg")
    print(aa)
    # ret_upload = upload_data(data, data_type='file')
    # print(ret_upload)
    # upload >> "{'Group name': b'group1', 'Remote file_id': b'group1/M00/03/75/wKgBSWJouVuAGOX3AAAAlzDoKbs6847.py', 'Status': 'Upload successed.', 'Local file name': '__init__.py', 'Uploaded size': '151B', 'Storage IP': b'192.168.1.73'}"