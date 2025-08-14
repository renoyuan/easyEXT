#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend op_db
# CREATE_TIME: 2024/3/20 18:43
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 数据操作
import os
import uuid
import hashlib

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from db_model.model import engine, User, Task, File, ModelInfo, Scene, Element, PostProcess

class OPDBBase(object):
    """
    所有操作返回格式统一为 list[obj]|obj|None
    """
    def __init__(self):

        self.format_map = {
            "jpg": 0, "jpeg": 1,
            "png": 2,  "tif": 3,
            "pdf": 4, "doc": 5,
            "json": 6,  "ofd": 7,
           
        }
        
        self.file_type_map = {
            0:"original_file", 1:"split_img",
            
            2:"ocr_deal_img", 3:"ocr_json",
            
            4:"ocr_merge_json",  5:"format_ocr_json",
           
            6:"format_table_ocr_json",  7:"ext_json",
           
            8:"ext_merge_json",  9:"format_ext_json",
           
            10:"seal_res_json", 11:"word2pdf"
            
        }
        
        self.task_type_map = {
           0:"要素抽取", 1:"ocr识别", 
           2:"表格识别", 3:"印章识别" 
        }
        
        self.task_sub_type_map = {
           0: "调用ocr", 1: "调用抽取", 
           2: "merge", 3: "调用印章" 
        }
        self.model_type_map = {
           0: "ocr", 1: "抽取", 
           2: "印章" 
        }
        
    def gen_uuid(self,):
        return str(int(uuid.uuid1().int) % (10 ** 19))
    
def gen_uuid():
    return str(int(uuid.uuid1().int) % (10 ** 19))


class OPUser(OPDBBase):
    def auth_user(self, account: str, password: str):
        stmt = select(User).where(User.account == account, User.password == password)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            return query
    
    def query_user_scenes(self, user_id):
        """用户场景"""
        stmt = select(User).where(User.id == user_id)    
        with Session(engine) as session:
            user = session.scalars(stmt).first()
            scenes = user.scenes
            logger.debug(f"scenes{scenes}")
         
            return scenes   
            
        
    def get_admin(self,account="admin"):
        stmt = select(User).where(User.account == account)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            return query
        
    def add_scenes(self,user_id,scene_id):
        """添加用户场景"""
        stmt1 = select(User).where(User.id == user_id)
        stmt2 = select(Scene).where(Scene.id == scene_id)
        with Session(engine) as session:
            
            user = session.scalars(stmt1).first()
            
            scene = session.scalars(stmt2).first()
            user.scenes.append(scene)
            session.add(user)
            session.commit()
        
    def query_user(self, user_id=None, account=None):
        if not any([user_id,account]):
            return None
        if user_id:
            stmt = select(User).where(User.id == user_id)  
        elif account:
            stmt = select(User).where(User.account == account)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            return query
   


    def string_to_md5(self, input_string):
        m = hashlib.md5()
        m.update(input_string.encode('utf-8'))  
        return m.hexdigest()


    def insert_user(self, account: str, pwd: str, isadmin:int=0,**args):
        user = self.query_user(account=account)
        if not user:
            logger.info(f" 不存在user")
            with Session(engine) as session:
                name = args.get("name","")
                account = account
                phone = args.get("phone","")
                password =  self.string_to_md5(pwd)
                # print(password)
                enable_password = pwd 
                user = User(account=account, password=password, enable_password=enable_password, phone=phone,
                    name=name, is_admin=isadmin)
                session.add(user)
                session.commit()
                return user
        else:
            logger.info(f"{user} 已存在")
            return user


class OpTask(OPDBBase):


    def new_sub_task(self, task_id, t_type=1, sub_type=0, model_label="2",file_id=None,ori_file_id=None,need_merge=0):
        """添加二级任务"""
        stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            p_task = session.scalars(stmt).first()
            sub_task = Task(
                uuid=self.gen_uuid(),
                parent_id=task_id,
                t_type=t_type,
                status=1,
                sub_type=sub_type,
                ori_file_count=1,
                file_count=1,
                model_label=model_label,
                user_id=p_task.user_id,
                file_id=file_id,
                ori_file_id=ori_file_id,
                merge=need_merge
            )
            session.add(sub_task)
            session.commit()
            return sub_task.instance_to_dict()
        
    def query_sub_task(self,task_id):
        """查询子任务"""
        stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            sub_task  = task.sub_task
            print("sub_task",sub_task)
            if sub_task:
                return [sub_task.instance_to_dict() for sub_task in sub_tasks]
        
        
    def query_parent_task(self,task_id):
        """查询父任务"""
        stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            parent_task  = task.parent_task
            print("parent_task",parent_task)
            if parent_task:
                return    parent_task.instance_to_dict()
        
    def update_task_status(self, task_id, status=2):
        """更新任务状态"""
        stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            task.status = status
            session.commit()
            return task.instance_to_dict()
        
    def check_upstream_ocr_merge_status(self,task_id, sub_type_label=2,ori_file_id=None):
        """
        检查ocr_merge 任务是否执行完毕
        ext 中调用
        ori_file_id 文档级别查询
        """
        stmt = select(Task).where(Task.id == task_id)
        file_stmt = select(File).where(File.id == ori_file_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            sub_task = task.sub_task
            
            if ori_file_id:
                logger.info(f"ori_file_id {ori_file_id}")
                file = session.scalars(file_stmt).first()
                task_count = 1
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3] and i.ori_file_id==ori_file_id] 
            else:
                task_count = task.ori_file_count
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3]] 
                    
            if task_count == len(sub_task):
                logger.info(f"check_upstream_ocr_merge_status - 子任务全部完成")
                return True
            else:
                logger.info(f"check_upstream_ocr_merge_status - 存在子任务未完成 task_count {task_count} len(sub_task)  { len(sub_task)}")
        
    def check_upstream_ocr_status(self,task_id, sub_type_label=0,ori_file_id=None):
        """
        检查ocr 任务是否执行完毕
        merge_ocr 中调用
        ori_file_id 文档级别查询        
        """
        stmt = select(Task).where(Task.id == task_id)
        file_stmt = select(File).where(File.id == ori_file_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            sub_task = task.sub_task
            
            if ori_file_id:
                file = session.scalars(file_stmt).first()
                task_count = file.length
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3] and i.ori_file_id==ori_file_id] 
            else:
                task_count = task.file_count
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3]] 
                    
            if task_count == len(sub_task):
                logger.info(f"子任务全部完成")
                return True
            else:
                logger.info(f"存在子任务未完成")
                    
    def check_upstream_ext_status(self, task_id, sub_type_label=1, ori_file_id=None):
        """
        检查ext 任务是否执行完毕
        ext_merge task 中调用
        ori_file_id 文档级别查询 
        """
        stmt = select(Task).where(Task.id == task_id)
        file_stmt = select(File).where(File.id == ori_file_id)
    
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            sub_task = task.sub_task
            
            if ori_file_id:
                file = session.scalars(file_stmt).first()
                task_count = 1
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3] and i.ori_file_id==ori_file_id] 
            else:
                task_count = task.ori_file_count
                sub_task = [i for i in sub_task if i.sub_type==sub_type_label and i.status in [2,3]] 
                    
            if task_count == len(sub_task):
                logger.info(f"子任务全部完成")
                return True
            else:
                logger.info(f"存在子任务未完成")
    
        
        
    def query_sub2_task(self,task_id):
        """查询子任务"""
        stmt = select(Task).where(Task.parent_id == task_id)
        with Session(engine) as session:
            sub_tasks = session.scalars(stmt)
            if sub_tasks:
                return [sub_task.instance_to_dict() for sub_task in sub_tasks]
            return
        
    def query_model_info(self,task_id):
        """查询父任务"""
        stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            sub_tasks = session.scalars(stmt)
            if sub_tasks:
                return [sub_task.instance_to_dict() for sub_task in sub_tasks]
            return
        
    def query_succeed_task(self,task_id):
        stmt = select(Task).where(Task.id == task_id, Task.status == 2, Task.parent_id==None)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            if task:
                files = OpFile().query_all_file(task_id)
                return files
            else:
                return
    
    def query_task(self,task_id=None,uuid=None):
        """获取任务信息"""
        if uuid:
            stmt = select(Task).where(Task.uuid == uuid)
        else:
            stmt = select(Task).where(Task.id == task_id)
        with Session(engine) as session:
            task = session.scalars(stmt).first()
            if task:
                return task.instance_to_dict()
            else:
                return

    def inser_ocr_task(self, task_info, user_id,task_type=0,scene_label="2",model_label=None,needMerge=0):
        """插入ocr任务"""
        with Session(engine) as session:
            # 先查询场景 
            scene = OpScene().query_scene_info(scene_label=scene_label)
            scene_id = scene["id"]
            model_info = OpScene().query_model_info(scene_label=scene["id"])
                
            
            # 创建任务
            task = Task(
                uuid=str(int(uuid.uuid1().int) % (10 ** 19)),
                t_type=task_type,scene_id=scene_id,
                ori_file_count=task_info["ori_info"]["file_length"],
                file_count=task_info["deal_info"]["file_length"],
                user_id=user_id,
                model_label=model_label,
                merge=1 if needMerge else 0
            )
            session.add(task)
            session.flush()

            # 插入文件 
            ori_files = [File(t_type=0, t_type_name=self.file_type_map[0], page_no=file["page"],
                              ori_page_no=file["ori_page"], length=file["length"], file_url=file["fdfs_id"],
                              file_name=file["filename"], format=self.format_map[file["file_type"]], task_id=task.id)
                         for
                         file in task_info["ori_info"]["file_info"]]

            session.add_all(ori_files)
            session.flush()
            logger.info(f"task_info{task_info}")
            logger.info(f"task_info{task_info}")
            
            # 插入依赖文件
            deal_files = [File(t_type=1, t_type_name=self.file_type_map[1], page_no=file["page"],
                               ori_page_no=file["ori_page"],length=file["length"], file_url=file["fdfs_id"],
                               file_name=file["filename"], format=self.format_map[file["file_type"]],
                               parent_id=ori_files[file["ori_file_no"]].id, task_id=task.id)
                          for
                          file in task_info["deal_info"]["file_info"]]
            session.add_all(deal_files)

            session.commit()
            return task.instance_to_dict(), [file.instance_to_dict() for file in ori_files], [file.instance_to_dict()  for file in deal_files]


    def insert_ext_task(self, task_info, user_id, scene_id=None, task_type=1, model_label=None,needMerge=0):
        """插入ext任务"""
        # 查场景信息
        with Session(engine) as session:
            task = Task(
                uuid=str(int(uuid.uuid1().int) % (10 ** 19)),
                t_type=task_type,
                ori_file_count=task_info["ori_info"]["file_length"],
                file_count=task_info["deal_info"]["file_length"],
                user_id=user_id,scene_id=scene_id,
                model_label=model_label,
                merge=1 if needMerge else 0
            )
            session.add(task)
            session.flush()

            ori_files = [File(t_type=0, page_no=file["page"], length=file["length"], file_url=file["fdfs_id"],
                              file_name=file["filename"], format=self.format_map[file["file_type"]], task_id=task.id)
                         for
                         file in task_info["ori_info"]["file_info"]]

            session.add_all(ori_files)
            session.flush()

            deal_files = [File(t_type=1, page_no=file["page"], length=file["length"], file_url=file["fdfs_id"],
                               file_name=file["filename"], format=self.format_map[file["file_type"]],
                               parent_id=ori_files[file["ori_file_no"]].id, task_id=task.id)
                          for
                          file in task_info["deal_info"]["file_info"]]
            session.add_all(deal_files)

            session.commit()
            return task.instance_to_dict(), [file.instance_to_dict() for file in ori_files], [file.instance_to_dict()  for file in deal_files]

  
        
class OpFile(OPDBBase):
            
    def insert_ocr_res(self, task_id, file_info, img_file_id, llm_page_json_id):
        """插入ocr结果"""
        with Session(engine) as session:
            img_file = File(t_type=2,t_type_name=self.file_type_map[2], page_no=file_info["page_no"],
                 ori_page_no=file_info["ori_page_no"],        
                 length=file_info["length"], file_url=img_file_id,
                 file_name=file_info["file_name"], format=self.format_map["jpg"],
                 parent_id=file_info["parent_id"], 
                 
                 task_id=task_id)
            json_file = File(t_type=3,t_type_name=self.file_type_map[3], page_no=file_info["page_no"], 
                             ori_page_no=file_info["ori_page_no"], length=file_info["length"], 
                             file_url=llm_page_json_id, file_name=os.path.splitext(file_info["file_name"])[0]+".json",
                             format=self.format_map["json"], 
                            
                            parent_id=file_info["parent_id"],task_id=task_id)
            session.add_all([img_file, json_file])
            session.commit()


    def query_doc_ocr_merge_json(self, task_id, parent_id=None):
        """查询指定文档的ocr merge json"""
        if parent_id:
            stmt = select(File).where(File.task_id == task_id, File.parent_id==parent_id, File.t_type==4)
        else: # 合并结果
            stmt = select(File).where(File.task_id == task_id, File.page_no==-1, File.t_type==4)
            
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            
            if query:
                query = query.instance_to_dict() 
                logger.info(f"query{query}")
                return query
            
    def query_ocr_merge_json(self, task_id):
        """查询ocr merge json"""
        stmt = select(File).where(File.task_id == task_id, File.page_no==-1, File.t_type==4)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            logger.info(f"task_id{task_id}")
            if query:
                query = query.instance_to_dict() 
                logger.info(f"query{query}")
                return query
                  
    def insert_file(self, task_id, file_info):
        """插入文件"""
        with Session(engine) as session:
            file = File(t_type=file_info["t_type"],t_type_name=self.file_type_map[file_info["t_type"]], page_no=file_info["page_no"], length=file_info["length"], file_url=file_info["file_url"],
                file_name=file_info["file_name"], format=self.format_map[file_info["format"]],
                parent_id=file_info["parent_id"], task_id=task_id)
           
            session.add(file)
            session.commit()
            
    def insert_ext_res(self, task_id, file_info, ext_file_id):
        """插入ext结果"""
        with Session(engine) as session:
            json_file = File(t_type=7,t_type_name=self.file_type_map[7], page_no=file_info["page_no"], length=file_info["length"], file_url=ext_file_id,
                            file_name=os.path.splitext(file_info["file_name"])[0]+".json", format=self.format_map["json"],
                            parent_id=file_info["parent_id"],task_id=task_id)
            session.add_all([img_file, json_file])
            session.commit()
            
    def query_all_file(self, task_id):
        """查询该任务下所有文件按文件类别分类"""
        stmt = select(File).where(File.task_id == task_id)
        files_dict = {}
        with Session(engine) as session:
            files = session.scalars(stmt)
            if files:
                files = [i.instance_to_dict() for i in files]
                # print("files",files)
                # 按文件类别 分类 按page 排序
                files_dict = {
                    "ori_file": [file for file in files if file["t_type"] == 0], 
                    "deal_img": [file for file in files if file["t_type"] == 1],
                    "ocr_img": [file for file in files if file["t_type"] == 2],
                    "ocr_json": [file for file in files if file["t_type"] == 3],
                    "ocr_merge_json": [file for file in files if file["t_type"] == 4],
                    "format_ocr_json": [file for file in files if file["t_type"] == 5],
                    "format_table_ocr_json": [file for file in files if file["t_type"] == 6],
                    "ext_json": [file for file in files if file["t_type"] == 7],
                    "ext_merge_json": [file for file in files if file["t_type"] == 8],
                    "format_ext_json": [file for file in files if file["t_type"] == 9],
                    "seal_res": [file for file in files if file["t_type"] == 10],
                    "word2pdf": [file for file in files if file["t_type"] == 11],
                }
                for i in files_dict.values():
                    if i:
                        i.sort(key=lambda x: x["page_no"])
                # print("files_dict", files_dict)
        return files_dict


class OpScene(OPDBBase):
    
    def query_key_map(self, scene_label=None, scene_id=None ):
        """获取字段子映射关系"""
        if scene_id:
            stmt = select(Scene).where(Scene.id == scene_id)
        elif scene_label:
            stmt = select(Scene).where(Scene.scene_label == scene_label)
        with Session(engine) as session:
            scene = session.scalars(stmt).first()
            
            if scene:
                elements = scene.element
                elements = [i.instance_to_dict()  for i in elements  ]
                logger.info(f"elements {elements}")
                return elements
            
    def query_scene_info(self, scene_label=None, scene_id=None ):
        """获取场景信息"""
        if scene_id:
            stmt = select(Scene).where(Scene.id == scene_id)
        elif scene_label:
            stmt = select(Scene).where(Scene.scene_label == scene_label)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            
            if query:
                query = query.instance_to_dict() 
                logger.info(f"query{query}")
                return query
            
    def query_model_info(self, scene_label=None, scene_id=None ):
        """获取关联的模型的信息"""
        if scene_id:
            stmt = select(Scene).where(Scene.id == scene_id)
        elif scene_label:
            stmt = select(Scene).where(Scene.scene_label == scene_label)
        else:
            return 
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            if not query:
                return
            model = query.model
            if not model:
                return
            else:
                models_res = model.instance_to_dict() 
            
                return models_res
               
    def insert_scene(self,  scene_label=None,**kwargs):
        """新增场景信息"""
        scene = self.query_scene_info(scene_label=scene_label)
        # stmt = select(Scene).where(Scene.id == scene_id)
        if scene:
            logger.info(f"{scene} 已存在")
            return  scene
        with Session(engine) as session:
            scene = Scene(scene_label=scene_label, scene=kwargs.get("scene",""),
                          scene_cn=kwargs.get("scene_cn",""), 
                          model_label=kwargs.get("model_label","") 
                          )
            session.add(scene)
           
            session.commit()
            
            # 所有场景被创建的时候理应给到admin 权限
            admin = OPUser().get_admin()
            logger.info(f"{admin}")
            OPUser().add_scenes(admin.id,scene.id)
            scene = scene.instance_to_dict() 
            return scene


class OpModel(OPDBBase):
    def get_info(self, model_label="2", model_id=None):
        """获取模型信息"""
        if model_id:
            stmt = select(ModelInfo).where(ModelInfo.id == model_id)
        else:
            stmt = select(ModelInfo).where(ModelInfo.model_label == model_label)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            if query:
                return query.instance_to_dict()
            
    def correlate_scene(self, model_id, scene_ids=None ):
        model_stmt = select(ModelInfo).where(ModelInfo.id == model_id)
        scent_stmt = select(Scene).filter(Scene.id.in_(scene_ids))
        with Session(engine) as session:
            model = session.scalars(model_stmt).first()
            scene_all = session.scalars(scent_stmt).all()
            
            for scene in scene_all:
                logger.info(f"model: {model} correlate_scene: {scene}")
                model.scenes.append(scene)
                session.add(model)
                session.commit()
            
    def insert_model(self, model_label="",model_name="", url=""):
        """新增模型信息"""
        model = self.get_info(model_label=model_label)
        
        if model and model["url"]==url:
            logger.info(f"{model} 已存在")
            return model
        with Session(engine) as session:
            
            
            model = ModelInfo(model_label=model_label, url=url, model_name=model_name)
            session.add(model)
            session.flush()
            session.commit()
       
            return   model.instance_to_dict()  

        
class OpElement(OPDBBase):
    def query_scene_ele_all(self,  scene_id=None, ):
        """获取场景要素信息"""
        stmt = select(Element).where(Element.scene_id == scene_id)
        with Session(engine) as session:
            query = session.scalars(stmt)
            if query:
                query_all = [i.instance_to_dict()  for i in query]
                logger(f"query_all{query_all}")
                return query_all
    
    def query_scene_ele_info(self, ele_label ,  scene_id=None, ):
        """获取场景要素信息"""
        stmt = select(Element).where(Element.scene_id == scene_id,Element.ele_label==ele_label)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            if query:
                query = query.instance_to_dict() 
                logger.info(f"query{query}")
                return query
            
    def query_ele_info(self, ele_id=None ):
        """获取要素信息"""
        stmt = select(Element).where(Element.id == ele_id)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            if query:
                query = query.instance_to_dict() 
                logger.info(f"query{query}")
                return query
            
    def judge_exist(self,scene_id, ele_labe,is_group=0 ):
        """
        插入前判断存在
        scene_id 下同一个element_label is_group 必须不同
        """
        stmt = select(Element).where(Element.scene_id == scene_id, ele_labe==ele_labe, is_group==is_group)
        with Session(engine) as session:
            query = session.scalars(stmt).first()
            if query:
                query = query.instance_to_dict() 
                logger.info(f"judge_exist: {query}")
                return query
         
                
        
    def insert_ele(self,  ele_list=None):
        """新增要素信息有组的需要先插入组要素"""
        print(ele_list) 
        if not ele_list:
            return
        with Session(engine) as session:
            
            ele_all = []
            for i in ele_list:
                # TODO 查询是否重复了 同一个场景下一个要素label 必须唯一
                judge_exist = self.judge_exist(i.get("scene_id"), i.get("ele_label"),is_group=i.get("is_group",0))
                if judge_exist:
                    continue
                else:
                    ele_all .append (
                    Element(
                        ele_label=i.get("ele_label"), model_ele_label=i.get("model_ele_label"),
                        ele_cn=i.get("ele_cn"), is_group=i.get("is_group",0),
                        t_type=i.get("t_type"), status=i.get("status",0),
                        scene_id=i.get("scene_id"), group_id=i.get("group_id"),
                            ) 
                    
                    )
            session.add_all(ele_all)
            session.flush()
            ele_all_info = [i.instance_to_dict() for i in ele_all]
            session.commit()
            
            return ele_all_info


class OpPostProcess(OPDBBase):
    def query_postprocess(self, element_ids=None,):
        """获取后处理信息"""
        if not element_id:
           return 
        
        stmt = select(PostProcess).filter(PostProcess.element_id.in_(element_ids))
        with Session(engine) as session:
            query = session.scalars(stmt)
            
            if query:
                query_all = [que.instance_to_dict() for que in query] 
                logger.info(f"query_all :\n{query_all}")
                return query_all
    
    def insert_postprocess(self,  postpro_infos=None,**kwargs):
        """新增后处理信息"""
        if not postpro_infos:
            return
        with Session(engine) as session:
            postpros = [
                PostProcess(path=info.get("path",""), element_id=info.get("element_id"),
                            ) for info in postpro_infos
                        ]
                  
            session.add_all(postpros)
            session.flush()
            postpros_info = [i.instance_to_dict() for i in postpros]
            session.commit()
            return postpros

if __name__ == "__mian__":
    import os, sys

    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
    print(sys.path)
    op_user = OPUser()
    user = op_user.auth_user("yss001", "e10adc3949ba59abbe56e057f20f883e")
