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
    
class FileTypeEnum(Enum):
    """文件类型枚举"""
    UNKNOWN = -1  # 未知类型
    IMG = 0  # 图片
    PDF = 1  # PDF
    DOC = 2  # Word文档
    XLS = 3  # Excel文档
    PPT = 4  # PowerPoint文档
    TXT = 5  # 文本文件
    XLSX = 6  # Excel文档（xlsx格式）
    PPTX = 7  # PowerPoint文档（pptx格式）
    DOCX = 8  # Word文档（docx格式）
    XLSX = 9  # Excel文档（xlsx格式）
    PPTX = 10  # PowerPoint文档（pptx格式）
    OTHER = 99 # 其他类型
    
class TaskPhaseEnum(Enum):
    """任务阶段枚举"""
    PRE_PROCESSING = 0    # 预处理
    MODEL_PROCESSING = 1 # 模型处理
    POST_PROCESSING = 2  # 后处理
    REVIEW = 3  # 人工审核
