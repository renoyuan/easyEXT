#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: /home/yss/idp_backend/backend/utils/fastdfs
#CREATE_TIME: 2024-03-26 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  

from .client import FDFS
fdfs_dict = {'host_tuple': ("192.168.1.136",), 'port': int(22122), 'timeout': 5,
             "use_connection_pool": True, "pool_size":10,'name': 'Tracker Pool'}
fdfs=FDFS(fdfs_dict=fdfs_dict)