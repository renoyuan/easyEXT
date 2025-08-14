#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend test_db
# CREATE_TIME: 2024/3/27 14:32
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from db_model.op_db import  OPUser,OpScene,OpTask,OpFile
if __name__ == "__main__":
    # op_user = OPUser()
    # user = op_user.auth_user("yss001", "e10adc3949ba59abbe56e057f20f883e")
    # op_scene = OpScene()
    # scene = op_scene.query_scene_info("gsyl001")
    # scene = op_scene.query_key_map("test_ext")
    # op_task = OpTask()
    # scene = op_task.query_sub2_task(97)
    # scene = op_task.query_parent_task(98)
    op_file = OpFile()
    op_file.query_doc_ocr_merge_json(896, 1585)
    # op_file.query_ocr_merge_json(799)
    print(111)