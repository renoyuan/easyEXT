"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/celery_task
CREATE_TIME: 2024-04-29 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note:  
"""
import sys,os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
print(sys.path)
from utils.fastdfs import fdfs
file_id = "group1/M00/01/8F/wKgBiGYuDYiAYzoPAABVAcLOz2809.json"
bb = fdfs.download_to_buffer(file_id)
print(bb)