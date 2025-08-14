#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend api
# CREATE_TIME: 2024/3/20 11:46
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 10 个接口
import json
from typing import Optional,List,Union

from fastapi import APIRouter, UploadFile, Request, Depends
from loguru import logger

from db_model.op_db import OPUser, OpTask,OpFile, OpScene
from utils.gen_token import create_jwt_token
from .response_code import gen_response
from .middleware import api_ocr_depends,PicItem
from .file_deal import FileDeal
from celery_task import ocr_task,ext_task,merge_ext_task,merge_ocr_task

from utils.serialize import OCRSeralize
from utils.read_img import read_img_info
from utils.fastdfs import fdfs

router = APIRouter()

"""
1 要素抽取 post
/draw/draw/doExtract?templateId=10001&pageNumber=0&needMerge=0&rotate=0&sealErasure=0
from originalFiles 
2 ocr 识别 post 
/draw/draw/doOCR?sealErasure=0&rotate=0
from originalFiles 
3 表格识别 post
draw/draw/checkTable?rotate=0
from originalFiles
4 印章识别 post
/draw/draw/recognizeSeal
from originalFiles
5  要素抽取结果查看 get 
/data/review/getExtractResult?taskSn=1216685860045586432
6  OCR识别结果查看 get 
/draw/fileTask/getOcrResult?taskSn=1214628782816755712
7 表格识别结果查看 get
/draw/fileTask/getTableResult?taskSn=1213479389036150784
8 印章识别结果查看 get
/draw/fileTask/getRecognizeSealResult?taskSn=1213212653636419584
9 获取图片 post
/draw/pdf/picParentTaskSnPageBatch?taskSn=1216685860045586432
10 获取token post
/exuser/user/login?account=yss001&password=e10adc3949ba59abbe56e057f20f883e
"""



def scene_auth(user_id,scene_label):
    """场景鉴权"""
    scenes = OPUser().query_user_scenes(user_id)
    if scenes:
        scenes_match = [scene_label==scene.scene_label for scene in scenes]
        logger.debug(f"scenes_match: {scenes_match}")
        if  any(scenes_match):
            return True
        else:
            return False
    else:
        return False
    
# ocr 识别 post ok
@router.post("/draw/draw/doOCR", tags=["task"])
async def ocr(rotate: Optional[int], sealErasure: Optional[int] , originalFiles: List[UploadFile], scene_label:Optional[str]="2", gv: dict = Depends(api_ocr_depends)):
    """
        res = {
        "ori_info": {
            "file_length": 0,
            "file_info": []
        },
        "deal_info": {
            "file_length": 0,
            "file_info": []
        }
    }
    """
    logger.debug(f"gv: {gv}")
   
    #  场景鉴权 
    if not scene_auth(gv["user_id"], scene_label):
        return gen_response(605)
    
    
    # 文件预处理 pdf识别  拆页 TODO 图片旋转 印章消除
    file_info = await FileDeal()(originalFiles, rotate, sealErasure )
    logger.debug(f"file_info{file_info}")
    
    # 生成任务上传文件
    task, ori_files, deal_files = OpTask().inser_ocr_task(file_info, gv["user_id"], task_type=1, scene_label=scene_label, model_label=scene_label)
    
    #  ocr 消息任务
    task_id = task["id"]  # 多个文件多个task_id
    task_uuid = task["uuid"]  # 多个文件多个task_id
    length = len(deal_files)
    for deal_file in deal_files:
        ocr_task.delay(task_id, deal_file,length)
    
    
    # 调用 merge_ocr_task多次调用先是文档级别然后全部的
    for ori_file in ori_files:
        merge_ocr_task.delay(task_id, ori_file=ori_file, terminus=0)
    merge_ocr_task.delay(task_id, terminus=1)
   
    
    # 返回 task id
    return gen_response(200, {"taskSns": task_uuid})


 
# OCR识别结果查看 ok
@router.get("/draw/fileTask/getOcrResult", tags=["future"])
async def get_ocr_res(taskSn: Union[int|str],  gv: dict = Depends(api_ocr_depends)):
    """
    1 查看任务状态 
    2 序列化 结果 
    """
    user_id = gv["user_id"]
    task = OpTask().query_task( uuid = int(taskSn))
    
    res_data = {
            "taskSn": taskSn,
            "templateId": "2",
            "taskStatus": 0,
            "totalPage": None,
            "dataGroup": None, # 没用？
            "pageJsons": None,
        }
    logger.info(f"task  {task}")
    if not task:
        return  gen_response(615)
    elif task["status"] in [0,1]:

        return  gen_response(200, res_data)

    elif task["status"] == 3:
        return  gen_response(617)

    
    res_data["taskSn"] = str(taskSn)
    res_data["totalPage"] = task["file_count"]
    res_data["taskStatus"] = 1 # //0:任务进行中；1：任务成功；2：任务失败
    
    file_qury = OpFile().query_all_file(task["id"])
    format_ocr_json = file_qury["format_ocr_json"]
    
    if format_ocr_json:
        logger.info(f"format_ocr_json  exists")
        format_ocr_url = format_ocr_json[0].get("file_url")
        
        fd_result = fdfs.download_to_buffer(format_ocr_url)
        try:
            seralize_ocr_json_list = json.loads(fd_result['Content'])
            
        except:
            return gen_response(618)
        res_data["pageJsons"] = seralize_ocr_json_list
        
    else:
        file_ocr_json = file_qury["ocr_json"]
        # print("file_ocr_json",file_ocr_json)
        ocr_merge_json = file_qury["ocr_merge_json"]
        if ocr_merge_json:
            file_url = ocr_merge_json[0].get("file_url")
            fd_result = fdfs.download_to_buffer(file_url)
            ocr_json_list = json.loads(fd_result['Content'])
        else:
            return gen_response(618)
       
        
        logger.debug(f"ocr_json_list{ocr_json_list}")
        # 序列化ocr 并上传到 fastdfs 
        seralize_ocr_json_list  = OCRSeralize()("o2o",ocr_json=ocr_json_list)   
        res_data["pageJsons"] = seralize_ocr_json_list
        seralize_ocr_file_id = fdfs.upload_data(seralize_ocr_json_list)
        
        #  入库保存 
        file_info = {
            "t_type":5, "page_no": -1,
            "length":res_data["totalPage"],"file_url":seralize_ocr_file_id,
            "file_name":f"{taskSn}_ocr_merge.json", "format":"json",
            "parent_id":None, "task_id":task["id"]
        }
        OpFile().insert_file(task["id"],file_info)
    
    return gen_response(200, res_data)


# 3 表格识别 post ok
@router.post("/draw/draw/checkTable", tags=["task"])
async def check_table(rotate: Optional[int] = 0, sealErasure: Optional[int] = 0 ,scene_label:Optional[str]="2", originalFiles: List[UploadFile]=None, gv: dict = Depends(api_ocr_depends)):
  
    #  场景鉴权 
    if not scene_auth(gv["user_id"], scene_label):
        return gen_response(605)
    
    # 文件预处理 pdf识别  拆页 图片旋转 印章消除
    file_info = await FileDeal()(originalFiles, rotate, sealErasure )
    # print("file_info", file_info)
    
    # 生成任务子任务上传文件
    task, ori_files, deal_files = OpTask().inser_ocr_task(file_info, gv["user_id"],scene_label=scene_label)
    # 发送 ocr 消息
    # print("task", task)
    task_id = task["id"]  # 多个文件多个task_id
    task_uuid = task["uuid"]  # 多个文件多个task_id
    length = len(deal_files)
    for deal_file in deal_files:
        ocr_task.delay(task_id, deal_file,length)
        
    # 调用 merge_ocr_task多次调用先是文档级别然后全部的
    for ori_file in ori_files:
        merge_ocr_task.delay(task_id, ori_file=ori_file, terminus=0)
    merge_ocr_task.delay(task_id, terminus=1)
    return gen_response(200, {"taskSns": task_uuid})


# 表格识别结果查看 ok
@router.get("/draw/fileTask/getTableResult", tags=["future"])
async def get_table_res(taskSn: Union[int|str], gv: dict = Depends(api_ocr_depends)):
    """
    0 进一步鉴权
    1 查看任务状态 
    2 序列化 结果 
    """
    user_id = gv["user_id"]
    task = OpTask().query_task( uuid = int(taskSn))
    res_data = {
            "taskSn": taskSn,
            "templateId": "2",
            "taskStatus": 0,
            "totalPage": None,
            "dataGroup": None,
            "pageJsons": None,
        }
 
    
    if not task:
        return  gen_response(615)
    elif task["status"] in [0,1]:
        return  gen_response(200, res_data)
    elif task["status"] == 3:
        return  gen_response(617)
    
    res_data["taskSn"] = str(taskSn)
    res_data["totalPage"] = task["file_count"]
    res_data["taskStatus"] =1 # //0:任务进行中；1：任务成功；2：任务失败
    
    file_qury = OpFile().query_all_file(task["id"])
    
    format_table_ocr_json = file_qury["format_table_ocr_json"]
    
    if format_table_ocr_json:
        logger.info(f"format_table_ocr_json  exists")
        format_table_ocr_url = format_ocr_json[0].get("file_url")
        
        fd_result = fdfs.download_to_buffer(format_table_ocr_url)
        try:
            seralize_table_ocr_json_list = json.loads(fd_result['Content'])
            
        except:
            return gen_response(618)
        res_data["pageJsons"] = seralize_table_ocr_json_list
    else:
        # 拉取文件并读取 
        file_ocr_json = file_qury["ocr_json"]
        # print("file_ocr_json",file_ocr_json)
        ocr_merge_json = file_qury["ocr_merge_json"]
        if ocr_merge_json:
            file_url = ocr_merge_json[0].get("file_url")
            fd_result = fdfs.download_to_buffer(file_url)
            ocr_json_list = json.loads(fd_result['Content'])
        else:
            return gen_response(618)
        
        print("ocr_json_list", ocr_json_list)
        
        # 序列化ocr并上传
        seralize_ocr_json_list  = OCRSeralize()("o2t",ocr_json=ocr_json_list)   
        res_data["pageJsons"] = seralize_ocr_json_list
        seralize_table_ocr_file_id = fdfs.upload_data(seralize_ocr_json_list)
        
        #  入库保存 
        file_info = {
            "t_type":6,"page_no":-1,
            "length":res_data["totalPage"],"file_url":seralize_table_ocr_file_id,
            "file_name":f"{taskSn}_table_ocr_merge.json", "format":"json",
            "parent_id":None, "task_id":task["id"]
        }
        OpFile().insert_file(task["id"],file_info)
    return gen_response(200, res_data)


# 要素抽取 post
@router.post("/draw/draw/doExtract", tags=["task"])
async def do_extract(templateId:str, pageNumber:int, needMerge:int, rotate:int, sealErasure:int, originalFiles: list[UploadFile], gv: dict = Depends(api_ocr_depends)):
    #  场景鉴权 
    if not scene_auth(gv["user_id"], templateId):
        return gen_response(605)
    # print(originalFiles)
    
    # 获取场景信息
    scene_info = OpScene().query_scene_info(templateId)
    if not scene_info:
        return gen_response(619)
    
    logger.debug(f"{scene_info}")
    
    # 文件预处理 pdf识别  拆页 #TODO 图片旋转 印章消除
    file_info = await FileDeal()(originalFiles, rotate, sealErasure)
    
    # print("file_info", file_info)
    # 通过场景 id 查询对应  生成任务上传文件
    task, ori_files, deal_files = OpTask().insert_ext_task(file_info, gv["user_id"], scene_id=scene_info["id"] ,  task_type=0, model_label=templateId,needMerge=needMerge)
    
    # 发送  消息 生成子任务 
    # print("task", task)
    task_id = task["id"]  # 多个文件多个task_id
    task_uuid = task["uuid"]  # 多个文件多个task_id
    length = len(deal_files)
    
    # 调用ocr_task
    for deal_file in deal_files:
        ocr_task.delay(task_id, deal_file, length,needMerge) # 否则在ocr 结束后调用抽取模型
    
    # 调用 merge_ocr_task多次调用先是文档级别然后全部的
    for ori_file in ori_files:
        merge_ocr_task.delay(task_id, ori_file=ori_file, terminus=0)
    merge_ocr_task.delay(task_id, terminus=0)
    
    # 调用ext_task
    if needMerge: # 合并抽取 ，调用一次
        
        ext_task.delay(task_id,  length)
    else: # 不合并,调用多次
        for ori_file in ori_files:
            ext_task.delay(task_id,  length, ori_file_id=ori_file["id"])
    
    # 调用merge_ext_task
    # 生成 最终结果 合并则直接使用 否则 合并后上传
    merge_ext_task.delay(task_id, merge_sub_type=1) 
    

    return gen_response(200, {"taskSns": [task_uuid]})
  


# 获得要素抽取结果
@router.get("/data/review/getExtractResult", tags=["future"])
async def getExtractResult(taskSn: int, gv: dict = Depends(api_ocr_depends)):
    """
    0 进一步鉴权
    1 查看任务状态 
    2 序列化 结果 
    接口中没有区分 文档全部合在一起
    """
    user_id = gv["user_id"]
    task = OpTask().query_task( uuid = int(taskSn))
    scene_id = task["scene_id"]
    scene = OpScene().query_scene_info( scene_id = scene_id)
    res_data = {
            "taskSn": scene["scene_label"],
            "templateId": "2",
            "taskStatus": 0,
            "totalPage": None,
            "dataGroup": None,
            "pageJsons": None,
        }
    
    if not task:
        return  gen_response(615)
    elif task["status"] in [0,1]:
        return  gen_response(200, res_data)
    elif task["status"] == 3:
        return  gen_response(617)
    
    res_data["taskSn"] = str(taskSn)
    res_data["totalPage"] = task["file_count"]
    res_data["taskStatus"] =1 # //0:任务进行中；1：任务成功；2：任务失败
    
    file_qury = OpFile().query_all_file(task["id"])
    format_ext_json = file_qury["format_ext_json"]
    
    logger.info(f"format_ext_json {format_ext_json}")
    if format_ext_json:
        logger.info(f"format_ext_json  exists")
        format_ext_json_url = format_ext_json[0].get("file_url")
        
        fd_result = fdfs.download_to_buffer(format_ext_json_url)
        try:
            seralize_ext_json_json_list = json.loads(fd_result['Content'])
            
        except:
            return gen_response(618)
        res_data["pageJsons"] = seralize_ext_json_json_list
    else:
        # 拉取文件并读取 
        ocr_merge_json = file_qury["ocr_merge_json"]
        ext_merge_json = file_qury["ext_merge_json"]
        if ocr_merge_json:
            ocr_file_url = ocr_merge_json[0].get("file_url")
            ext_file_url = ext_merge_json[0].get("file_url")
            fd_result = fdfs.download_to_buffer(ocr_file_url)
            ocr_merge_json_list = json.loads(fd_result['Content'])
            fd_result = fdfs.download_to_buffer(ext_file_url)
            ext_merge_json = json.loads(fd_result['Content'])
        else:
            return gen_response(618)

        # 获取映射关系
        elements = OpScene().query_key_map(scene_id=scene_id) 
        # scene_key_map = OpScene().query_key_map(scene_id=scene_id) 
        # 序列化ocr并上传
        seralize_ext_json_list  = OCRSeralize()("ext",ocr_json=ocr_merge_json_list, 
                                                ext_json=ext_merge_json,elements=elements)   
        logger.info(f"seralize_ext_json_list {seralize_ext_json_list}") 
        res_data["pageJsons"] = seralize_ext_json_list
        seralize_table_ocr_file_id = fdfs.upload_data(seralize_ext_json_list)
        
        #  入库保存 
        file_info = {
            "t_type":9,"page_no":-1,
            "length":res_data["totalPage"],"file_url":seralize_table_ocr_file_id,
            "file_name":f"{taskSn}_ext_merge.json", "format":"json",
            "parent_id":None, "task_id":task["id"]
        }
        OpFile().insert_file(task["id"],file_info)
    return gen_response(200, res_data)


# 印章识别
@router.post("/draw/draw/recognizeSeal", tags=["task"])
async def recognizeSeal(rotate: int, originalFiles: list[UploadFile]):
    return [{"username": "Rick"}, {"username": "Morty"}]


# 印章识别结果查看
@router.get("/draw/fileTask/getRecognizeSealResult", tags=["future"])
async def getRecognizeSealResult(taskSn: int):
    print(taskSn)
    return [{"username": "Rick"}, {"username": "Morty"}]


    
# 获取图片 ing 
@router.post("/draw/pdf/picParentTaskSnPageBatch", tags=["task"])
async def picParentTaskSnPageBatch(taskSn: int,request: Request):
    """
    获取图片
    """
    print(taskSn)
    # await sleep()
    # a = await sleep_coroutine()
    # print(a)
    pages = await request.json()
    print(pages)
    task = OpTask().query_task(uuid=taskSn)
    imgs_res = {}
    if task:
        
        # 判断任务是否完成。完成才操作 
        if task["status"] in [0,1]:
            return gen_response(616)
        elif task["status"] in [3]:
            return gen_response(617)
        
        # 获取任务ocr返回的图片 根据pages 筛选 
        task_files = OpFile().query_all_file(task["id"])
        ocr_img = task_files["ocr_img"]
        if ocr_img:
            for img in ocr_img:
                if img["page_no"] in pages:
                    file_url = img["file_url"]
                    img_info = read_img_info(file_url)
                    imgs_res[img["page_no"]] = {
                        "base64": img_info["base64"],
                        "width": img_info["width"],
                        "height": img_info["height"],
                        "pageNo": img["page_no"]
                    }
            return gen_response(200, imgs_res)
        else:
            return gen_response(601)
        
    else:
        return gen_response(615)

    

# 获取任务

# 生成token ok
@router.post("/exuser/user/login", tags=["task"])
async def read_users(request: Request, account: str, password: str):
    # print(account)
    # print(password)
    # 数据库校验

    op_user = OPUser()
    user = op_user.auth_user(account, password)
    if not user:
        return gen_response(401)
    # 生成token
    user_info = {
        "user_id": user.id,
        "account": account
    }
    token = create_jwt_token(user_info)
    return gen_response(200, {"token": token})
