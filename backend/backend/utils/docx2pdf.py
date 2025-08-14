"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/utils
CREATE_TIME: 2024-05-09 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note:  word2pdf
"""
from spire.doc import *


def  word2pdf(w_p,p_p):
    document = Document() # 加载Word文档
    document.LoadFromFile(w_p) # "关于中国人寿养老保险股份有限公司养老金产品的提示.docx"

    # 保存为PDF
    document.SaveToFile(p_p, FileFormat.PDF) # "output.pdf"