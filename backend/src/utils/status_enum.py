"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: F:\\opensource\\easyEXT\\backend\\src\\utils
CREATE_TIME: 2025-09-22
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno
note: 状态
"""
from enum import Enum
class TaskStatusEnum(Enum):
    """任务状态枚举"""
    PENDING = 0    # 待处理
    PROCESSING = 1 # 处理中
    COMPLETED = 2  # 已完成
    CANCELLED = 3  # 已取消
    FAILED = 4  # 处理失败
    TIMEOUT =5   # 处理超时
    DELETED = 6  # 已删除