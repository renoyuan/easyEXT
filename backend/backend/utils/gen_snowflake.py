#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend gen_snowflake
# CREATE_TIME: 2024/3/20 17:37
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from snowflake import Snowflake

# 创建一个Snowflake实例
snowflake = Snowflake()

# 生成一个唯一ID
unique_id = snowflake.generate().generate_id()

print(unique_id)
1214648983520149504