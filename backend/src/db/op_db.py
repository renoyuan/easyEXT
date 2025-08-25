#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend op_db
# CREATE_TIME: 2024/3/20 18:43
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 数据操作
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))

import uuid
import hashlib

from loguru import logger
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional

from db.model import Scenes,Tasks,Taskresults


class OPDBBase(object):
    """
    所有操作返回格式统一为 list[obj]|obj|None
    """
    def __init__(self,engine):

        self.engine =engine

        
    def gen_uuid(self,):
        return str(int(uuid.uuid1().int) % (10 ** 19))




class OpScenes(OPDBBase):
    
    def query_all_scenes(self ):
        """
        获取所有场景以及二级场景
        [
            {
                "id":1,
                "category":"金融"
            
            "scenarios":[
                {"id":2,"scene_label":"金融场景1","scene":"金融场景1的描述"},

            ]
            }
        ]
        
        """
        scenes_list = []
        
        with Session(self.engine) as session:
            statement = select(Scenes)
            # 执行查询
            results = session.exec(statement)
            # 获取所有结果并返回一个包含所有 Hero 对象的列表
            all_scenes = results.all()
            if not all_scenes:
                return scenes_list
            else:
                for scene in all_scenes:
                    if not scene.f_id:
                        category = {"id":scene.id,"category":scene.scene_name,"scenarios":[]}
                        for scene in all_scenes:
                             if scene.f_id == category["id"]:
                                category["scenarios"].append({"id":scene.id,"scene_label":scene.scene_name,"scene":scene.scene_name})
                        scenes_list.append(category)
                return scenes_list

    
        
            
    

class OpTasks(OPDBBase):
    pass

class OpTaskresults(OPDBBase):
    pass

if __name__ == "__main__":
    import os, sys

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
    print(sys.path)
    from sqlmodel import Session, SQLModel, create_engine
    import json
    from dotenv import load_dotenv
    import os
    load_dotenv(r"../.env")
    DbConfig = os.getenv("DbConfig")
    print(DbConfig)
    DbConfig = json.loads(DbConfig) 

    engine = create_engine(f"postgresql+psycopg2://{DbConfig['user']}:{DbConfig['password']}@{DbConfig['host']}:{DbConfig['port']}/{DbConfig['database']}")
    SQLModel.metadata.create_all(engine)
    OpScenes = OpScenes(engine)
    scenes = OpScenes.query_all_scenes()
    print(scenes)

    
