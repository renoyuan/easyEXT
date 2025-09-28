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

class TaskPhaseEnum(Enum):
    """任务阶段枚举"""
    PRE_PROCESSING = 0    # 预处理
    MODEL_PROCESSING = 1 # 模型处理
    POST_PROCESSING = 2  # 后处理
    REVIEW = 3  # 人工审核
    
class FileStatusEnum(Enum):
    """文件状态枚举"""
    ORIGINAL= 0    # 原始文件
    PROCESSED = 1  # 处理后文件

class FileTypeEnum(Enum):
    """文件类型枚举"""
    UNKNOWN = -1  # 未知类型
    IMG = 0  # 图片
    PDF = 1  # PDF
    DOC = 2  # Word文档
    DOCX = 3  # Word文档（docx格式）
    XLS = 4  # Excel文档
    XLSX = 5  # Excel文档（xlsx格式）
    TXT = 6  # 文本文件
    PPT = 7  # PowerPoint文档
    PPTX = 8  # PowerPoint文档（pptx格式）
    
    
    @staticmethod
    def get_file_type_by_suffix(suffix):
        """
        根据文件后缀名返回对应的文件类型枚举成员。
        参数:
            suffix (str): 文件后缀名，例如 ".txt", "pdf", "DOCX"（不区分大小写，可带或不带点）
        返回:
            FileTypeEnum: 对应的枚举成员，如果未找到则返回 FileTypeEnum.UNKNOWN。
        """
        # 统一处理后缀字符串：转换为小写并确保以点开头（例如 "txt" -> ".txt"）
        suffix = suffix.lower()
        if not suffix.startswith('.'):
            suffix = '.' + suffix

        # 创建一个后缀到枚举成员的映射字典
        suffix_map = {
            '.jpg': FileTypeEnum.IMG.value,
            '.jpeg': FileTypeEnum.IMG.value,
            '.png': FileTypeEnum.IMG.value,
            '.gif': FileTypeEnum.IMG.value,
            '.bmp': FileTypeEnum.IMG.value,
            '.pdf': FileTypeEnum.PDF.value,
            '.doc': FileTypeEnum.DOC.value,
            '.xls': FileTypeEnum.XLS.value,
            '.ppt': FileTypeEnum.PPT.value,
            '.txt': FileTypeEnum.TXT.value,
            '.xlsx': FileTypeEnum.XLSX.value,
            '.pptx': FileTypeEnum.PPTX.value,
            '.docx': FileTypeEnum.DOCX.value,
        }
        # 使用字典的 get 方法查找，未找到则返回 FileTypeEnum.UNKNOWN
        return suffix_map.get(suffix, FileTypeEnum.UNKNOWN.value)
    


