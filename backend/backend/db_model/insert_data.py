"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/backend/db_model
CREATE_TIME: 2024-04-15 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note:  
"""
"""
1.2 新增脚本数据库插入场景数据
1 场景 - 模型 - 要素 -后处理
2 场景 - 用户
"""
import os, sys
root_p = os.path.abspath(os.path.dirname (os.path.dirname(__file__)))
print(root_p)
sys.path.insert(0,root_p )

from loguru import logger

from model import User, Scene, ModelInfo 
from op_db import OPUser,OpScene,OpModel,OpElement,OpPostProcess

class InsertData(object):
    def __init__(self,):
        pass
    
    def insert_init_data(self,):
        """
        1 插入admin用户信息
        2 插入基础场景信息
        3 插入基础模型信息
        关联对应信息
        """
        # 插入admin用户信息
        user = OPUser().insert_user( account="admin", pwd="123456",isadmin=1,name="admin",)
        logger.info(f"insert user ok")
        
        # 插入基础场景信息 ocr 要素抽取 && 关联 用户-场景
        scene_ocr = OpScene().insert_scene(scene_label="2",scene="ocr",scene_cn="ocr识别")
        scene_ext = OpScene().insert_scene(scene_label="test_ext",scene="test_ext",scene_cn="测试场景")
        
        
        # 插入基础模型信息 
        ocr_m = OpModel().insert_model(model_label="2",model_name="ocr识别",
                                     url="http://192.168.1.131:1101/api/model/ocr", )
        ext_m = OpModel().insert_model(model_label="test_scene",model_name="测试抽取",
                                     url="http://192.168.1.131:1102/api/model/predict")
        # 关联  场景-模型
        OpModel().correlate_scene(ocr_m["id"],[scene_ocr.get("id"),scene_ext.get("id")])
        
        OpModel().correlate_scene(ext_m["id"],[ scene_ext.get("id")])
       
        # 插入要素信息
        ele_list = [
            {
                "ele_label":"test_key",
                "model_ele_label":"test_key",
                "ele_cn":"测试要素",
                "scene_id":scene_ext.get("id"),
            }
    
        ]
        ele_m_s = OpElement().insert_ele(ele_list=ele_list )
        postpro_infos = [{**i, "element_id": i["id"]} for i in ele_m_s]
        logger.info(f"insert ele ok")
        # 插入后处理信息
        postpros = OpPostProcess().insert_postprocess(postpro_infos=postpro_infos )
        logger.info(f"insert postpros ok")
    
    def create_user(self,user_info,scene_info):
        """
        创建用户并关联场景
        """
        user = OPUser().insert_user(user_info["account"], user_info["pwd"])
        
        for scene_ in scene_info:
            OPUser().add_scenes(user.id, scene_["id"])
        

        
if __name__ == "__main__":
    # InsertData().insert_init_data()
    InsertData().create_user({"account":"yss001","pwd":"123456"},[{"id":8},{"id":9}])