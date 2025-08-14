#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend gen_uuid
# CREATE_TIME: 2024/3/20 17:56
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
import uuid

# 生成 UUID
# unique_id = uuid.uuid4()
unique_id = uuid.uuid1()

# 转换为 19 位数字唯一 ID
# print(int(unique_id.int))
unique_id_digits = int(uuid.uuid1().int) % (10**19)

print("Unique ID:", unique_id_digits)