#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend op_db
# CREATE_TIME: 2024/3/20 18:43
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 数据操作
import os,sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import uuid
import hashlib
from sqlalchemy.orm import joinedload
from loguru import logger
from sqlmodel import SQLModel, Field, create_engine, Session, select,func
from typing import Optional
from sqlalchemy.sql.expression import and_
from db.model import Scenes,Tasks,Taskresults,Elements,File


class OPDBBase(object):
    """
    所有操作返回格式统一为 list[obj]|obj|None
    """
    def __init__(self,engine):

        self.engine =engine

        
    def gen_uuid(self,):
        return str(int(uuid.uuid1().int) % (10 ** 19))
    def gen_uuid4(self,):
        return str(uuid.uuid4())




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

    def query_all_scenes_map(self,):
        scenes_map = {}
        with Session(self.engine) as session:
            statement = select(Scenes)
            # 执行查询
            results = session.exec(statement)
            # 获取所有结果并返回一个包含所有 Hero 对象的列表
            all_scenes = results.all()
            if not all_scenes:
                return scenes_map
            else:
                for scene in all_scenes:
                    scenes_map[scene.id] = scene.scene_name
                return scenes_map

    def query_scene(self,scene_id=None,scene_name=None):
        with Session(self.engine) as session:
            if scene_id:
                statement = select(Scenes).where(Scenes.id == int(scene_id))
            elif scene_name:
                statement = select(Scenes).where(Scenes.scene_name == scene_name)
            results = session.exec(statement)
            scene = results.first()
            return scene

        
            
class OpElements(OPDBBase):
    def query_element_scene(self,scene_id):
        with Session(self.engine) as session:
            statement = select(Elements).where(Elements.scene_id == int(scene_id))
            results = session.exec(statement)
            element = results.first()
            return element

class OpTasks(OPDBBase):
    def add_taskfile(self,task_id,file_id,status  ,file_type,file_name,taltol_page,page):
        with Session(self.engine) as session:
            taskfile = File(task_id=task_id,fdfs_id=file_id,status=status,file_type=file_type,file_name=file_name,taltol_page=taltol_page,page=page)
            session.add(taskfile)
            session.commit()
            session.refresh(taskfile)
    def add_task(self,scene_id,status,phase=0):
       
        with Session(self.engine) as session:
            task = Tasks(scene_id=scene_id,status=status,phase=phase)
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    
    def select_task(self,scene_id=None,status=None,page:int=1,page_size:int=20):
        with Session(self.engine) as session:
         

            statement =   select(Tasks)
            scenes_map =   OpScenes(self.engine).query_all_scenes_map()

            
                        
            if scene_id:
                statement = statement.where(Tasks.scene_id == scene_id)
            if status:
                statement = statement.where(Tasks.status == status)
            statement = statement.order_by(Tasks.created_time.desc())
            
            # 获取总数(不考虑分页)
            total = 0
           
            total = len(session.exec(statement).all())
            
            # 计算分页偏移量
            offset = (page - 1) * page_size
            
            
          
            
            # 应用分页
            statement = statement.offset(offset).limit(page_size)
            # 执行查询
            results = session.exec(statement)
            
            tasks = results.all()
            # 处理 时间 格式 新增场景id-名映射关系
            processed_tasks = []
            for task in tasks:
                # 1. 格式化时间字段（直接修改模型实例的属性）
                task.updated_time = task.updated_time.strftime("%Y-%m-%d %H:%M:%S")
                task.created_time = task.created_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 2. 将模型实例转为字典（保留格式化后的时间）
                task_dict = task.model_dump()
                
                # 3. 从 scenes_map 中获取场景名称（添加默认值避免 KeyError）
                task_dict["scene_name"] = scenes_map.get(task.scene_id, "未知场景")  # 关键优化点
                
                processed_tasks.append(task_dict)

            return processed_tasks,total
    
    def select_task_by_status(self,status):
        with Session(self.engine) as session:
            statement = select(Tasks).where(Tasks.status == status)
            results = session.exec(statement)
            tasks = results.all()
            return tasks
        
    def query_element(self,task_id):
        with Session(self.engine) as session:
            statement = select(Tasks).where(Tasks.id == task_id)
            results = session.exec(statement)
            task = results.first()
            scenes = OpElements(self.engine).query_element_scene(task.scene_id)
            scenes = scenes.model_dump()

            return scenes
        
    def query_task(self,task_id):
        with Session(self.engine) as session:
            statement = select(Tasks).where(Tasks.id == task_id)
            results = session.exec(statement)
            task = results.first()
            return task
        
    def update_task(self,task_id,status,phase):
        with Session(self.engine) as session:
            statement = select(Tasks).where(Tasks.id == task_id)
            results = session.exec(statement)
            task = results.first()
            if task:
                task.status = status
                task.phase = phase
                session.add(task)
                session.commit()
                session.refresh(task)
                return task
            else:
                return None

class OpTaskresults(OPDBBase):
    def add_taskresult(self,task_id,extracted_data,data_status):
        with Session(self.engine) as session:
            taskresult = Taskresults(task_id=task_id,extracted_data=extracted_data,data_status=data_status)
            session.add(taskresult)
            session.commit()
            session.refresh(taskresult)
            return taskresult
        
    def query_taskresult(self,task_id):
        with Session(self.engine) as session:
            statement = select(Taskresults).where(Taskresults.task_id == str(task_id))
            results = session.exec(statement)
            taskresult = results.first()
            taskresult.updated_time = taskresult.updated_time.strftime("%Y-%m-%d %H:%M:%S")
            taskresult.created_time = taskresult.created_time.strftime("%Y-%m-%d %H:%M:%S")
            task_info = taskresult.model_dump()
            return task_info
        
    def update_taskresult(self,task_id,extracted_data,data_status):
        with Session(self.engine) as session:
            statement = select(Taskresults).where(Taskresults.task_id == task_id)
            results = session.exec(statement)
            taskresult = results.first()
            if taskresult:
                taskresult.extracted_data = extracted_data
                taskresult.data_status = data_status
                session.add(taskresult)
                session.commit()
                session.refresh(taskresult)
                return taskresult
            else:
                return None



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

    
