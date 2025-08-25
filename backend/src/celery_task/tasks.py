#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend test
# CREATE_TIME: 2024/3/22 16:47
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: test任务
import time
import traceback
import requests

from celery import Celery
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from celery.backends.sqlalchemy import SQLAlchemyBackend

from utils.fastdfs import fdfs
from db_model.op_db import OPUser, OpTask, OpModel,OpFile
from .call_model import CallModel
from .task_info import TaskTools

# app = Celery('hello', broker='amqp://guest@localhost//')
# 1 当前模块名称 2 boker 即代理的配置信息
app = Celery('celery_task', backend='redis://192.168.1.137:6380/1') # , backend='redis://192.168.1.137:6380/0'
app.conf.broker_url = 'redis://192.168.1.137:6380/0'

# 初始化 SQLAlchemy 部分
USER = "root"
PWD = "Tlrobot123."
IP = "192.168.1.137"
PORT = "3306"
DB_NAME = "idp"
engine_text = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'
app.conf.backend = engine_text.format(USER, PWD, IP, PORT, DB_NAME)
engine = create_engine(engine_text.format(USER, PWD, IP, PORT, DB_NAME), echo=True)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
from utils.fastdfs import fdfs

# app.result_backend = engine_text


# 定义任务路由
app.conf.task_routes = {
    'celery_task.tasks.ocr_task': {'queue': 'queue1'},
    'celery_task.tasks.ext_task': {'queue': 'queue2'},
    'celery_task.tasks.merge_ocr_task': {'queue': 'queue3'},
    'celery_task.tasks.merge_ext_task': {'queue': 'queue4'},
    'celery_task.tasks.seal': {'queue': 'queue5'},
}

# 测试任务
@app.task
def hello():
    logger.debug("hello world ")
    return "hello world "

# python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue1 --concurrency=1
# 调用ocr模型
@app.task
def ocr_task(task_id, file_info, length=None, need_merge=0):
    """
    :param task_id:
    :param file_info:
    :param length:
    need_merge 
    :return:
    """
    # 查询任务信息
    task = OpTask().query_task(task_id)


    # 判断场景 0要素抽取 1ocr识别 2表格识别 3印章识别 t_type 主任务类型  sub_type 子任务类型
    t_type = task["t_type"]

    # 新增一个调用ocr二级任务
    sub_task = OpTask().new_sub_task(task_id, t_type=t_type, sub_type=0, model_label="2",
                                     file_id=file_info["id"],ori_file_id=file_info["parent_id"],need_merge=need_merge)
    
    logger.info(f"execute ocr_task task_id: {task_id} sub_task_id: {sub_task['id'] }  need_merge: {need_merge}")
    try:
        # 获取模型信息
        model_info = OpModel().get_info(model_label="2")
        url = model_info["url"]
        # 启动任务
        _ = OpTask().update_task_status(task_id, 1)
            
        logger.debug(f"file_info{file_info}")
        
        # 调用ocr 模型
        msg_code, ocr_res = CallModel().call_ocr_model(url, file_info)

        # 任务失败 子任务  
        if msg_code!=200 :  
            _ = OpTask().update_task_status(sub_task["id"], 3)
            logger.error(f"ocr task {sub_task['id']} faild --> ocr msg_code {msg_code} ")
            return
        else:
            # 上传ocr json文件， 图片
            img_file_id = ocr_res["img_file_id"]
            llm_page_json_id = ocr_res["llm_page_json_id"] # 直接用这个参数
            OpFile().insert_ocr_res(task_id, file_info, img_file_id, llm_page_json_id)
            logger.info(f"ocr task {sub_task['id']} success")
            _ = OpTask().update_task_status(sub_task["id"], 2)
            return
    except Exception as e:
        logger.error(f"f{traceback.format_exc()}")
        _ = OpTask().update_task_status(sub_task["id"], 3)
    return

# python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue2 --concurrency=1
# 调用抽取模型
@app.task
def ext_task(task_id,  length, ori_file_id=None, need_merge=0):
    """
    调用抽取模型 任务
    输入 待抽取json文件
    ori_file_id 单文档抽取
    """
    # 查询任务&新增一个二级任务
    task = OpTask().query_task(task_id)  
    sub_task = OpTask().new_sub_task(task_id, t_type=0, sub_type=1,ori_file_id=ori_file_id,need_merge=need_merge)
    logger.info(f"execute ext_task task_id: {task_id} sub_task_id{sub_task['id']} length: {length} ori_file_id {ori_file_id} need_merge{need_merge}")
    

    # 获取模型信息
    model_label = task["model_label"]
    model_info = OpModel().get_info(model_label=model_label)
    url = model_info["url"]
    logger.info(f"model_label {model_label} url{url}")
    
    # 启动任务
    _ = OpTask().update_task_status(sub_task["id"], 1)
        
    try:
        # 等待上游ocr 任务完成 生成ocr merge 文件 
        task_tool = TaskTools()
        start_time = time.time()
        
        if ori_file_id: # 单文档抽取 
            timeout = task["file_count"] * 5  + 5 + 5 #设置超时时间
            upstream_status = task_tool.check_upstream_status(task_id, 2, ori_file_id,start_time=start_time,timeout=timeout) # True成功 Flase 失败 
            if upstream_status:
                #  获取doc_ocr_merge 文件
                ocr_merge_file_info = OpFile().query_doc_ocr_merge_json(task_id, parent_id=ori_file_id)
            else:
                logger.error(f"task faild timeout {sub_task['id']}")
                _ = OpTask().update_task_status(sub_task["id"], 3) 
                return
            
        else: # 合并抽取 输入ocr_merge
            timeout = task["file_count"] * 5  + 5 + 5 #设置超时时间
            upstream_status = task_tool.check_upstream_status(task_id, 2,start_time=start_time,timeout=timeout) # True成功 Flase 失败 
        
            if upstream_status:
                #  获取 ocr_merge 文件
                ocr_merge_file_info = OpFile().query_ocr_merge_json(task_id)
            else:
                logger.error(f"task faild timeout {sub_task['id']}")
                _ = OpTask().update_task_status(sub_task["id"], 3) # 任务失败
                return
            
        logger.info(f"ocr_merge_file_info {ocr_merge_file_info}")
        if not ocr_merge_file_info:
            logger.info(f"task faild ocr_merge_file_info {ocr_merge_file_info} is None")
            _ = OpTask().update_task_status(sub_task["id"], 3) 
            return
        
        # 调用抽取模型
        call_code, ext_res = CallModel().call_ext_model(url, ocr_merge_file_info, model_label)
        

        
        # 更新任务状态 流程结束 
        if call_code != 200:  
            _ = OpTask().update_task_status(sub_task["id"], 3)
        
        else:
                
            #  上传ext_json文件 & 入库 
            json_list_file_id = fdfs.upload_data(ext_res)
            file_info = {
                "t_type":7,
                "page_no":ocr_merge_file_info["page_no"],"ori_page_no":ocr_merge_file_info["ori_page_no"],
                "length":ocr_merge_file_info["length"] ,"file_url":json_list_file_id,
                "file_name":ocr_merge_file_info["file_name"].replace("merge","ext"), "format":"json",
                "parent_id":ocr_merge_file_info["parent_id"], "task_id":task_id
            }
            
            OpFile().insert_file(task_id, file_info)
            
            _ = OpTask().update_task_status(sub_task["id"], 2)  
    except Exception as e:
        logger.error(f"f{traceback.format_exc()}")
        _ = OpTask().update_task_status(sub_task["id"], 3)
    return 

# python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue3 --concurrency=1
# 调用merge
@app.task
def merge_ocr_task(task_id, ori_file=None, terminus=0,sub_type_label=0,need_merge=1):
    """
    合并  ocr json 
    ori_file 代表文档级别的合并
    terminus 是否终节点
    sub_type 0调用ocr 1 要素抽取
    
    ocr ext 
    merge_docs 
    """
    
    # 查询任务信息
    op_task = OpTask()
    task = op_task.query_task(task_id)
    t_type = task["t_type"]
    
    # 创建ocr_merge子任务    
    sub_task = op_task.new_sub_task(task_id, t_type=t_type, sub_type=2,file_id=ori_file["id"] if ori_file else None,
                                    ori_file_id=ori_file["id"]if ori_file else None,need_merge=need_merge)
    
    logger.info(f"execute merge_ocr_task task_id: {task_id} sub_task_id {sub_task['id']} need_merge{need_merge}")
    logger.info(f" ori_file {ori_file} terminus: {terminus} sub_type_label: {sub_type_label} ")
    try:
        task_tool = TaskTools()
        start_time = time.time()
        
        # 检查&等待上游依赖结果 
        #设置超时时间
        timeout = (ori_file["length"] * 5 + 5 +1000) if ori_file else  (task["file_count"] * 5 + 5 +1000) 
        upstream_status = task_tool.check_upstream_status(task_id,0,ori_file_id= ori_file["id"] if ori_file else None ,
                                                            start_time=start_time,timeout=timeout) 
        
        # 等待结束
        if upstream_status:
            # 合并文件
            
            task_tool.deal_ocr_merge(task_id, ori_file_id=ori_file["id"] if ori_file else None ,sub_type=0)  
           
            # 更新任务状态
            op_task.update_task_status(sub_task["id"], 2)
            if terminus:
                op_task.update_task_status(task_id, 2)
                logger.info(f"主任务{task_id} 结束")
            logger.info(f"ocr merge {sub_task['id']}结束")
        else:
            logger.error(f"task timeout {sub_task['id']}")
            # 更新任务状态
            _ = OpTask().update_task_status(sub_task["id"], 3) 
            if terminus:
                op_task.update_task_status(task_id, 3)
            logger.info(f"ocr merge {sub_task['id']} 超时")
            return
            
    except Exception as e:
        logger.error(f"f{traceback.format_exc()}")
        _ = OpTask().update_task_status(sub_task["id"], 3)

# python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue4 --concurrency=1
# 调用merge
@app.task
def merge_ext_task(task_id, merge_sub_type=0, need_merge=1):
    """
    合并  ocr json 以及 ext json 
    sub_type 0调用ocr 1 要素抽取
    
    ocr ext 
    
    只更新状态 模型返回结果已经足够了
    """
    
    
    # 查询任务信息
    op_task = OpTask()
    task = op_task.query_task(task_id)
    t_type = task["t_type"]
    
    # 创建merge子任务
    sub_task = op_task.new_sub_task(task_id, t_type=t_type, sub_type=3, need_merge=need_merge)
    
    logger.info(f"execute merge_ext_task task_id: {task_id} sub_task_id{sub_task['id']} merge_sub_type: {merge_sub_type} need_merge: {need_merge}")
    
    try:
        task_tool = TaskTools()
        start_time = time.time()
        timeout = task["file_count"] * 5 + 5 + 5 #设置超时时间
        logger.info(f"timeout{timeout}")
        # 检查&等待上游依赖结果 
        upstream_status = task_tool.check_upstream_status(task_id, merge_sub_type, need_merge,start_time=start_time, timeout=timeout) # True成功 Flase 失败 
        
        if upstream_status:
            task_tool.deal_ext_merge(task_id, 1) # 合并
            
            # 更新任务状态
            op_task.update_task_status(sub_task["id"], 2)
            op_task.update_task_status(task_id, 2)
        
        else:
            logger.error(f"task timeout {sub_task['id']}")
            op_task.update_task_status(sub_task["id"], 3)
            op_task.update_task_status(task_id, 3)

       
    except Exception as e:
        logger.error(f"f{traceback.format_exc()}")
        _ = OpTask().update_task_status(sub_task["id"], 3)
        
# python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue5 --concurrency=1
# 印章识别
@app.task
def seal():
        # 新增一个二级任务
    sub_task = OpTask().new_sub_task(task_id, t_type=0, sub_type=0)
    # 查询任务信息
    task = OpTask().query_task(task_id)
    # 获取模型信息
    model_info = OpModel().get_info(task_id)
    url = model_info.url

    # 调用抽取模型
    cur_page = file_info["page_no"]
    if cur_page ==0: # 启动任务
        _ = OpTask().update_task_status(task_id, 1)
    
    # 调用抽取模型
    msg_code, ext_res = CallModel().call_ext_model(url, file_info)
    
    # 任务失败 子任务 流程结束 
    if call_code != 200:  
        _ = OpTask().update_task_status(sub_task["id"], 3)
        if file_info["page_no"] + 1 == length:  # 任务失败 主任务 流程亦结束
            # 两种情况 1 部分任务缺失 成功 2 全部任务缺失 失败
            sub_tasks = OpTask().query_sub_task(task_id)
            if all(list(filter(lambda sub_task: True if sub_task["status"] == 3 else False, sub_tasks))):
                _ = OpTask().update_task_status(task_id, 3)
            else:
                _ = OpTask().update_task_status(task_id, 2)
        return
    else:
        _ = OpTask().update_task_status(sub_task["id"], 2)
    
    # 上传ext json文件， 图片
    img_file_id = ocr_res["img_file_id"]
    llm_page_json_id = ocr_res["llm_page_json_id"]
    OpFile().insert_ocr_res(task_id, file_info, img_file_id, llm_page_json_id)
    
    # 更新任务状态
    _ = OpTask().update_task_status(task_id, 2)
    return "seal "

# 定时任务
@app.task
def db_split():
    #TODO 定期切割数据库去掉不需要的数据 task file ele_value msg_task
    print("db_split")
    return "db_split "

