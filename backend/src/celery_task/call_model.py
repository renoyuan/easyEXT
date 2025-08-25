"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/celery_task
CREATE_TIME: 2024-04-08 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note: 调用模型  
"""
import requests

from loguru import logger

class CallModel(object):
    def __init__(self,):
        # 请求ocr任务
        self.ocr_config = {
                "_name": "2",
                "merge_ocr_json": True,
                "ocr_max_length": 256,
                "replace_with_sup": True,
                "only_supp_ocr": True,
                "add_supp_ocr": True,
                "modify_line": False,
                "add_transpose_supp": False,
                "visible_transpose_supp": False,
                "just_transpose_supp": False,
                "do_check_angle": True,
                "remove_seal": False,
                "do_avoid_vertical_textblocks": False
            }

    def call_ocr_model(self, url, info):
        req = {
            "element_id": "2",
            "gpu_id": "0",
            "input_path": "",  # /home/guoshou/forecaest_new/test_dir/2.png
            "task_id": info["task_id"],
            "file_name": info["file_name"],
            "file_id": info["file_url"],  # group1/M01/3D/A9/rBIHD2TtjIaAGGtKAA3zyhqlS2c436.jpg
            "page": info["page_no"],
            "ocr_config": self.ocr_config,
            "double_pdf": None}
        try:
            logger.info(f"调用ocr{url}")
            res = requests.post(url=url, json=req).json()
            if res["code"] not in ["0", 0]:
                logger.info(f"调用ocr{url}异常 {getattr(res,'msg')} {getattr(res,'code')} ")
                return  100, None
            logger.info(f"调用ocr{url}成功")
            return 200, res["data"]
        except Exception as e:
            
            logger.info(f"调用ocr{url}异常 {e}")
            return  100, None

    def call_ext_model(self, url, info, model_label):
        req = {'element_id': model_label, 'file_name': info["file_name"], 'gpu_id': '1', 'input_path': None, 
               'ocr_file_id': info["file_url"], 'ocr_json': None}
        try:
            logger.info(f"调用ocr{url}")
            res = requests.post(url=url, json=req).json()
            if res["code"] not in ["0", 0]:
                logger.info(f"调用ocr{url}异常 msg: {getattr(res,'msg',None)} code: {getattr(res,'code',None)} ")
                return  100, None
            logger.info(f"调用ocr{url}成功")
            return 200, res["data"]
        except Exception as e:
            
            logger.info(f"调用ocr{url}异常 {e}")
            return  100, None




