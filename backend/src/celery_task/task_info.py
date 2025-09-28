"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/celery_task
CREATE_TIME: 2024-04-10 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note: 任务的具体实现  
"""
import json 
import time 
import requests 
import sys,os
import copy
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
print(sys.path)
from loguru import logger

from db_model.op_db import OPUser, OpTask, OpModel, OpFile
# from utils.fastdfs import FDFS
from utils.fastdfs import fdfs


# fdfs_dict = {'host_tuple': ("192.168.1.136",), 'port': int(22122), 'timeout': 5,
#              "use_connection_pool": False} # , "pool_size":10,'name': 'Tracker Pool'
# fdfs=FDFS(fdfs_dict=fdfs_dict)

class TaskTools(object):
    def check_upstream_status(self, task_id, upstream_sub_type_label, ori_file_id=None,start_time=None, timeout=None):
        """
        检查上游任务是否全部完成
        upstream_sub_type_label 上游类别标识
        ori_file_id 原始文件id
        start_time 开始时间
        timeout 超时时间
        
        ocr & ext
        """
        logger.info(f"upstream_sub_type_label {upstream_sub_type_label}")
        
        # 等待上游任务完成 
        while True:
            # check ocr task status
            if upstream_sub_type_label==0: #  ocr_merge 中调用
                if ori_file_id: # 文档内ocr 是否全部完成 
                      
                    finish = OpTask().check_upstream_ocr_status(task_id, upstream_sub_type_label,ori_file_id=ori_file_id)
                else: 
                    finish = OpTask().check_upstream_ocr_status(task_id, upstream_sub_type_label)
                    
            # check ocr_merge task status      
            elif upstream_sub_type_label==2: #   ext 中调用 
                if ori_file_id: 
                    finish = OpTask().check_upstream_ocr_merge_status(task_id, upstream_sub_type_label,ori_file_id=ori_file_id)
                else:
                    finish = OpTask().check_upstream_ocr_merge_status(task_id, upstream_sub_type_label)
                    
            # check ext task status 
            elif upstream_sub_type_label==1: # 判断ext_task  ext_merge 中调用
                if ori_file_id: # 单个文件ext 结果
                    finish = OpTask().check_upstream_ext_status(task_id, upstream_sub_type_label, ori_file_id=ori_file_id) 
                else:
                    finish = OpTask().check_upstream_ext_status(task_id, upstream_sub_type_label) 
                    
            elif upstream_sub_type_label==3: # ext merge 暂没有下游任务
                pass 
            
           
            if finish:
                return True
            time.sleep(0.1)
            
            # 判断超时
            if (time.time() - start_time) > timeout:
                logger.info(f"任务超时 timeout")
                return False
         
               
            
    def fdfs_upload_data(self,json_list):
        # 上传文件
        json_list_file_id = fdfs.upload_data(json_list)
        return json_list_file_id
    
    def fdfs_download_ocr_page(self,fdfs_file_id):
        """下载ext_rese json"""
        fast_http = "http://192.168.1.136:8888/"
        fd_result = fdfs.download_to_buffer(fdfs_file_id)
        
        # logger.info(f" fd_result {fd_result} url {fdfs_file_id}")
        
        if fd_result == -1:
            url = fast_http + fdfs_file_id
            logger.info(f" fastdfs 连不上  使用 http 下载 {url}")
            ocr_json = json.loads(requests.get(url).content) 
        else:
            ocr_json = json.loads(fd_result['Content'])
        ocr_json_page = ocr_json[0]
        ocr_json_page.pop("llm_data", None) 
        return ocr_json_page
    
    def fdfs_download_ext_res(self,fdfs_file_id):
        """下载ocr page json"""
        fast_http = "http://192.168.1.136:8888/"
        fd_result = fdfs.download_to_buffer(fdfs_file_id)
        
        logger.info(f" fd_result {fd_result} url {fdfs_file_id}")
        
        if fd_result == -1:
            url = fast_http + fdfs_file_id
            logger.info(f" fastdfs 连不上  使用 http 下载 {url}")
            ext_res = json.loads(requests.get(url).content) 
        else:
            ext_res = json.loads(fd_result['Content'])
        ext_res = ext_res.get("_merge", {})
        
        return ext_res
    
    def merge_ext(self,dict_merge,doc_ext_json):
        """合并多次抽取结果"""
        for key, values in doc_ext_json.items():
            if key in dict_merge:
                dict_merge[key].extend(values)
            else:
                dict_merge[key] = values
        
    def deal_ext_merge(self,task_id, sub_type):
        """
        合并抽取结果
        
        """
        
        files = OpFile().query_all_file(task_id)
        

        file_t_type = 8 # extr_merge_json 
        ext_json = files["ext_json"] # parent_id
       
        file_info =             {
            "t_type":file_t_type,
            "page_no":-1,"ori_page_no":-1,
            "length":len(files['ocr_json']),"file_url":None,
            "file_name":f"{task_id}_{'ext' if sub_type else 'ocr'}_merge.json", "format":"json",
            "parent_id":None, "task_id":task_id
        }
        
        if len(ext_json)>1: # 合并
            #  merge_ocr_json & doc_merge_ocr_json 并入库
            logger.info(f"ext_json {ext_json}")
            
            # 下载 ext_dict
            ext_dict = {"_merge":{}}
            for ext in ext_json:
                try:
                    doc_ext_json = self.fdfs_download_ext_res(ext["file_url"])
                except Exception as e:
                    logger.error(f"fdfs_download_doc_ext_json error ")
                    logger.error(f"{e}")
                    doc_ext_json = {}
                finally:
                    self.merge_ext(ext_dict["_merge"], doc_ext_json)
                    
            # 上传文件
            json_list_file_id = fdfs.upload_data(ext_dict)
            file_info["file_url"] = json_list_file_id
        elif len(ext_json) == 1:  # 直接使用原始结果
            file_info["file_url"] = ext_json[0]["file_url"]
        else:
            return
            
        #  入库保存 
        file = OpFile().insert_file(task_id,file_info)
   
            
    
    
    def deal_ocr_merge(self,task_id,ori_file_id=None, sub_type=0):
        """
        合并任务
        获取所有对应文件并合并 
        生成文档级别和总的合并文件
        
        """
        fast_http = "http://192.168.1.136:8888/"
        files = OpFile().query_all_file(task_id)
        

        file_t_type = 4 # ocr_merge_json
        ocr_jsons_info = files["ocr_json"] # parent_id
        
        ori_files = files["ori_file"] # id
        page_no = -1
        
        # 构建入库数据
        insert_file_info = {
            "t_type":file_t_type,
            "page_no":-1 ,"ori_page_no":-1 ,
            "length":len(ocr_jsons_info),"file_url":None,
            "file_name":f"{task_id}_{'ext' if sub_type else 'ocr'}_merge.json", "format":"json",
            "parent_id":None, "task_id":task_id
        }
        
        if ori_file_id: # 文档级别合并
            for idx, i in enumerate(ori_files):
                if i["id"] == ori_file_id:
                    page_no = idx
            ocr_jsons_info = [i for i in ocr_jsons_info if i["parent_id"] ==ori_file_id ]
            insert_file_info["page_no"] = page_no
            insert_file_info["ori_page_no"] = -1
            insert_file_info["length"] = len(ocr_jsons_info)
            insert_file_info["parent_id"] = ori_file_id
        
        json_list = []
            
        for page, info in enumerate(ocr_jsons_info):
            
            file_url_id = info.get("file_url")
            parent_id = info["parent_id"]
        
            # 下载ocr 结果 
            try:
                page_json = self.fdfs_download_ocr_page(file_url_id)
                page_json["pageNo"] = page
            except Exception as e:
                logger.error(f"fdfs_download_ocr_page error ")
                logger.error(f"{e}")
                page_json = {}
            finally:
                json_list.append(page_json)
                    
    
        
            
            
        # 上传文件 merge_ocr_json & doc_merge_ocr_json 并入库
        # logger.info(f"json_list {json_list}")
        
        
        # 上传文件
        json_list_file_id = fdfs.upload_data(json_list)
            
        insert_file_info["file_url"] = json_list_file_id
            

                
        #  入库保存 
        file = OpFile().insert_file(task_id,insert_file_info)
           
                
            
        return 
                 
    def deal_merge(self,task_id, sub_type):
        """
        合并任务
        获取所有对应文件并合并 
        生成文档级别和总的合并文件
        
        """
        fast_http = "http://192.168.1.136:8888/"
        files = OpFile().query_all_file(task_id)
        
        if sub_type:
            file_t_type = 8
            jsons = files["ext_json"] # 可能会有改动
        else:
            file_t_type = 4 # ocr
            jsons = files["ocr_json"]
        
        urls = [i["file_url"] for i in jsons]
        json_list = []
        
        for page, url in enumerate(urls):
            if url:
                fd_result = fdfs.download_to_buffer(url)
                if fd_result == -1:
           
           
                    # return json_preview(None, 104)
                    # 尝试http 下载 fastdfs 连不上 
                    print("fastdfs 连不上  使用 http 下载",url)
                
                    url = fast_http + url
                    
                    ocr_json = json.loads(requests.get(url).content) 
                    ocr_json_page = ocr_json[0]
                    ocr_json_page.pop("llm_data",None) 
                    json_list.append(ocr_json_page)
                else:
        
                    logger.info(f" fd_result {fd_result} url {url}")
                    try:
                        ocr_json = json.loads(fd_result['Content'])
                        ocr_json_page = ocr_json[0]
                        ocr_json_page.pop("llm_data",None) 
                        json_list.append(ocr_json_page)
                    except:
                        json_list.append({})
            else:
                json_list.append({})
                
        # 上传文件
        logger.info(f" json_list {json_list}")
        print("==="*100,id(fdfs))
        json_list_file_id = fdfs.upload_data(json_list)
        
        #  入库保存 
        
        file_info = {
            "t_type":file_t_type,
            "page_no":-1,"ori_page_no":-1,
            "length":len(urls),"file_url":json_list_file_id,
            "file_name":f"{task_id}_{'ext' if sub_type else 'ocr'}_merge.json", "format":"json",
            "parent_id":None, "task_id":task_id
        }
        file = OpFile().insert_file(task_id,file_info)
        return 
    
    
class TaskExecute(object):
    def __init__(self,):
        pass
    
    def execute_ocr(task_id, file_info, length):
        """
        0 判断场景 ocr/table 要素抽取
        1 获取 ocr 接口&构造 ocr 参数
        2 调用 ocr
        3 入库
        4 整合ocr 结果 并序列化 入库
        5 调用抽取模型
        :param task_id:
        :param file_info:
        :param length:
        :return:
        """
        # 新增一个二级任务
        sub_task = OpTask().new_sub_task(task_id)
        # 查询任务信息
        task = OpTask().query_task(task_id)
        # 获取模型信息
        model_info = OpModel().get_info(task_id)
        url = f"http://{model_info.ip}:{model_info.port}{model_info.api_path}"

        # 调用ocr 模型
        cur_page = file_info["page_no"]
        if cur_page ==0: # 启动任务
            _ = OpTask().update_task_status(task_id, 1)
            
        msg_code, ocr_res = CallModel().call_ocr_model(url, file_info)

        # 任务失败 子任务 流程结束 
        if msg_code!=200 :  
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

        # 上传ocr json文件， 图片
        img_file_id = ocr_res["img_file_id"]
        llm_page_json_id = ocr_res["llm_page_json_id"]
        OpFile().insert_ocr_res(task_id, file_info, img_file_id, llm_page_json_id)

        # 判断场景
        t_type = task["t_type"]
        # print("t_type",t_type)
        if t_type == 0:  
            if False: # 合并抽取情况
                # TODO 仅在最后一页执行找到所有页的结果 合并上传再请求模型
                pass
            else:
                call_ext.delay(task_id, file_info, length) # 调用要素抽取场景
        if t_type in [1,2] and (file_info["page_no"] + 1 == length): # ocr 识别以及表格识别
            _ = OpTask().update_task_status(task_id, 2)
        return