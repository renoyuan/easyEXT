#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend test
# CREATE_TIME: 2024/3/22 17:11
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))
print(sys.path)
from celery_task.tasks import hello,call_ocr,call_ext
# task = hello.delay()
call_ocr_task = call_ocr.delay()
call_ext_task = call_ext.delay()


# print(task)
print(call_ocr_task.get(timeout=20))
# print(call_ext_task.get(timeout=10))
# print(assemble_task.get(timeout=10))



