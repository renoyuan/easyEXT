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

from db_model.op_db import  OPUser

op_user = OPUser()
user = op_user.auth_user("yss001", "e10adc3949ba59abbe56e057f20f883e")

if __name__ == "__main__":
    pass