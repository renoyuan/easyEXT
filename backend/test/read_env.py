
"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/test
CREATE_TIME: 2024-05-09 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note: 读取.env  
"""
from dotenv import load_dotenv

# 指定.env文件的路径，如果不指定，默认在同一目录下寻找
load_dotenv('../.env')

# 现在你可以像使用os.getenv一样访问环境变量
import os
# database_url = os.getenv('DATABASE_URL')
for key, value in os.environ.items():
    print(f"{key}: {value}")