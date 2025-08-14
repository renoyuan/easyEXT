#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend serialize
# CREATE_TIME: 2024/3/20 11:48
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 序列化格式
from loguru import logger

class OCRSeralize(object):
    def __init__(self,):
        self.modes = ["merge","o2o","o2t","ext","seal"]
        
    def merge(ocr_json):
        """将多页ocr结果合并"""
        pass
    
    def o2o(self, ocr_json):
        """ocr结果转换"""
        "转换为 文档 -> 页码 -> line 先默认一个文档"
        new_ocr_json = []
        for ocr_page in ocr_json:
            new_ocr_page = {}
            new_ocr_page["pageNo"] = ocr_page["pageNo"]
            new_ocr_page["pageStartIndex"] = 0
            new_ocr_page["docId"] = ocr_page["docID"]
            new_ocr_page["pageEndIndex"] = len(ocr_page["lineList"])
            paragraphs = [] #文档内页
            paragraph = {} #文档内页
            paragraph["paraId"] = ocr_page["docID"]
            paragraph["paraNo"] = ocr_page["pageNo"]
            lineList = ocr_page["lineList"]
            lines = []
            for cell in lineList:
                print("cell",cell)
                new_cell = {}
                new_cell["sortNo"] = cell.get("sortNo") if cell.get("sortNo") else cell["lineNo"]
                new_cell["rowNo"] = cell.get("rowNo") if cell.get("rowNo") else cell["lineNo"]
                new_cell["lineNo"] = cell["lineNo"]
                new_cell["lineStartIndex"] = 0
                new_cell["lineEndIndex"] = len(cell["objContent"])
                new_cell["objContent"] = cell["objContent"]
                new_cell["lineId"] = cell["lineId"]
                new_cell["objPos"] = cell["objPos"]
                new_cell["objType"] = cell["objType"]
                new_cell["objType_postpreprocess"] = cell.get("objType_postpreprocess") if cell.get("objType_postpreprocess") else cell["objType"] 
                lines.append(new_cell)
            paragraph["lines"] = lines
            paragraphs.append(paragraph)
            new_ocr_page["paragraphs"] = paragraphs
            new_ocr_json.append(new_ocr_page)
        return new_ocr_json
    
    def o2t(self, ocr_json):
        """ocr结果转换table 只保留table块"""
        new_ocr_json = []
        for ocr_page in ocr_json:
            new_ocr_page = {}
            new_ocr_page["pageNo"] = ocr_page["pageNo"]
            new_ocr_page["pageStartIndex"] = 0
            new_ocr_page["docId"] = ocr_page["docID"]
            new_ocr_page["pageEndIndex"] = len(ocr_page["lineList"])
            paragraphs = [] #文档内页
            paragraph = {} #文档内页
            paragraph["paraId"] = ocr_page["docID"]
            paragraph["paraNo"] = ocr_page["pageNo"]
            lineList = ocr_page["lineList"]
            lines = []
            for cell in lineList:
                print("cell",cell)
                new_cell = {}
                if cell["objType"] != "table":
                    continue
                else:
                    new_cell["cells"] = cell["cells"]
                new_cell["sortNo"] = cell.get("sortNo") if cell.get("sortNo") else cell["lineNo"]
                new_cell["rowNo"] = cell.get("rowNo") if cell.get("rowNo") else cell["lineNo"]
                new_cell["lineNo"] = cell["lineNo"]
                new_cell["lineStartIndex"] = 0
                new_cell["lineEndIndex"] = len(cell["objContent"])
                new_cell["objContent"] = cell["objContent"]
                new_cell["lineId"] = cell["lineId"]
                new_cell["objPos"] = cell["objPos"]
                new_cell["objType"] = cell["objType"]
                new_cell["objType_postpreprocess"] = cell.get("objType_postpreprocess") if cell.get("objType_postpreprocess") else cell["objType"] 
                lines.append(new_cell)
            paragraph["lines"] = lines
            paragraphs.append(paragraph)
            new_ocr_page["paragraphs"] = paragraphs
            new_ocr_json.append(new_ocr_page)
        return new_ocr_json
    
    def gen_template(self,key_map):
        """
        [
            {key:
            {"elementValue":None,
            "objPosList":None,
            "page":None,
            "model_key":None,
            "groub":None,
            
        }}]
        """
        
        template = []
        for i in key_map.value():
            pass
        
    def gen_key_map(self,elements):
        """ 
        """
        elements_dicts = {i["id"]: i for i in elements }
        key_map = {}
        is_groups = {i["id"]: i for i in elements if i["is_group"] }
        if is_groups:
            # 找组内的元素
            is_groups_keys = list(is_groups.keys())
            cell_keys = []
            for k,v in elements_dicts.items():
                group_id =  v["group_id"]
                if group_id and group_id in is_groups:
                    cell_keys.append(k)
                    if is_groups[group_id].get("group"):
                        is_groups[group_id].get("group")[k]=v
                    else:
                        is_groups[group_id]["group"]={k:v}
                   
            # 删除多于的
            for key in is_groups_keys:
                _=elements_dicts.pop(key,None)
            for key in cell_keys:
                _=elements_dicts.pop(key,None)
            # 合并 
            elements_dicts.update(is_groups)
            key_map = elements_dicts
        else:
            key_map = {v["ele_label"]: v for v in elements_dicts.values()}
        
            
        return key_map
    
    def ext(self,ocr_json=None, ext_json=None, elements=None):
        """
        ext结果转换
        1 格式转换 ext 格式转换
        2 关联ocr 中的坐标 
        retruen  ext_list[{"key1":{
            "elementValue":"",
            "objPosList":[[y,x,h,w,pos_list],] // 可能多个坐标
            "page":0
        },
        {"key2":{}}
        
        }]
        """
        key_map = self.gen_key_map(elements)
        template = None
        ext_json=ext_json.get("_merge")
        max_lenth = len(max(ext_json.values()))
        finally_ext_json = []
        for idx in range(max_lenth):
            cell_list = {}
            for v in key_map.values():
                if v.get("is_group"): # TODO 编组要素 模型中 不分组 
                    pass
                else:
                    cur_key_lenth = len(ext_json[v.get("model_ele_label", [])])
                    model_ele_dict = ext_json[v.get("model_ele_label")][idx] if  idx < cur_key_lenth else ""
                    logger.info(f"model_ele_dict {model_ele_dict}")
                    cell_list[v["ele_label"]] = {
                        "elementValue":model_ele_dict["value"],
                        "objPosList":[],
                        "page":0,
                    }
            finally_ext_json.append(cell_list)
        return finally_ext_json
        
    
    def seal(ocr_json):
        """seal结果转换"""
        pass
    
    def __call__(self, mode:str, ocr_json=None, ext_json=None,elements=None):
        if mode not in self.modes:
            return 200
        elif mode == "merge":
            res  = self.merge()
        elif mode == "o2o":
            res  = self.o2o(ocr_json)
            return res
        elif mode == "o2t":
            res  = self.o2t(ocr_json)
            return res
        elif mode == "ext":
            res  = self.ext(ocr_json=ocr_json, ext_json=ext_json,elements=elements)
            logger.info(f"ext_res {res}")
            return res
        elif mode == "seal":
            res  = self.seal()
        return res
        
        
