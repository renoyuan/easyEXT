#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend model
# CREATE_TIME: 2024/3/20 11:47
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from datetime import datetime
from typing import Optional, List

from sqlalchemy import create_engine, ForeignKey, String, func, Table, Column, Integer, Index
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship,backref

USER = "root"
PWD = "Tlrobot123."
IP = "192.168.1.137"
PORT = "3306"
DB_NAME = "idp"
engine_text = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'
engine = create_engine(engine_text.format(USER, PWD, IP, PORT, DB_NAME), echo=False)
# engine = create_engine(engine_text.format(USER, PWD, IP, PORT, DB_NAME), echo=True)


class Base(DeclarativeBase):
    __abstract__ = True
    # 定义共有属性
    id: Mapped[int] = mapped_column(primary_key=True)
    created_time: Mapped[datetime] = mapped_column(insert_default=func.now(), default=datetime.utcnow,
                                                   comment="创建时间")
    updated_time: Mapped[datetime] = mapped_column(insert_default=func.now(), default=datetime.utcnow,
                                                   comment="更新时间")
    is_del = mapped_column(TINYINT(), insert_default=0, comment="0存在 1删除")

    def __repr__(self) -> str:
        return f"{self.__tablename__} (id={self.id!r}"

    def instance_to_dict(self):
        # 定义一个函数将实例转换为字典
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


#  权限表
user_scene_association = Table('user_scene_association', Base.metadata,
                              
                               Column('user', Integer, ForeignKey('user.id', ondelete='CASCADE'), primary_key=True ),
                               Column('scene', Integer, ForeignKey('scene.id', ondelete='CASCADE'), primary_key=True )
                               )

# 场景-模型 关联信息
scene_model_association = Table('scene_model_association', Base.metadata,
                                
                                Column('scene_id', Integer, ForeignKey('scene.id', ondelete='CASCADE'), primary_key=True),
                                Column('model_info_id', Integer, ForeignKey('model_info.id', ondelete='CASCADE'), primary_key=True)
                                )


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String(999), comment="姓名")
    phone: Mapped[Optional[str]] = mapped_column(String(999), comment="手机号")
    account: Mapped[str] = mapped_column(String(999), unique=True, comment="账号")
    password: Mapped[str] = mapped_column(String(999), comment="密码MD5加密")
    enable_password: Mapped[str] = mapped_column(String(999), comment="明文密码")
    is_admin: Mapped[int] = mapped_column(insert_default=0, comment="0否 1是")

    # 场景 *>*  任务 1>*
    
    # 多对多 back_populates="users" 
    scenes: Mapped[Optional[List["Scene"]]] = relationship(
        "Scene", secondary=user_scene_association,
        backref = "users" , cascade=None
        )
                                                          

    tasks: Mapped[Optional[List["Task"]]] = relationship(back_populates="user", cascade="")



class Scene(Base):
    __tablename__ = "scene"
    scene_label = Column(String(999), unique=True, comment="对外提供场景标识")
    model_label: Mapped[Optional[str]] = mapped_column(String(999), comment="默认模型标识")
    scene: Mapped[Optional[str]] = mapped_column(String(999), comment="场景名")
    scene_cn: Mapped[Optional[str]] = mapped_column(String(999), comment="场景名中文")
    # scene_model: Mapped[Optional[str]] = mapped_column(String(999), comment="调用模型场景名")

    # 关联 user *>* user 中已经定义  model 1>1  element 1>*  task 1>*
    
    # users: Mapped[Optional[List["User"]]] = relationship( 
    #      secondary=user_scene_association,
    #     back_populates="scenes", cascade=None
    # )
   
    models: Mapped[Optional[List["ModelInfo"]]] = relationship(
        "ModelInfo", secondary=scene_model_association,
        back_populates="scenes", cascade=None
    )

    element: Mapped[Optional[List["Element"]]] = relationship(
        back_populates="scene", cascade="")

    tasks: Mapped[Optional[List["Task"]]] = relationship(back_populates="scene", cascade="")


class ModelInfo(Base):
    __tablename__ = "model_info"
    model_label: Mapped[str] = mapped_column(String(999), comment="模型标识")
    model_name: Mapped[Optional[str]] = mapped_column(String(999), comment="模型名称")
    model_type: Mapped[Optional[int]] = mapped_column(insert_default=0, comment="模型类型 0 ocr 1要素抽取 2印章识别  ")
    url: Mapped[Optional[str]] = mapped_column(String(999),insert_default="", comment="url")
    default_para: Mapped[Optional[str]] = mapped_column(String(999), comment="场景名")
    
    # 关联场景 Scene 1>1
    scenes: Mapped[Optional[List["Scene"]]] = relationship(
        "Scene", secondary=scene_model_association,
        back_populates="models", cascade=None
    )
 


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[int] = mapped_column(String(19), comment="19 位数字唯一 uuid")
    idx_uuid = Index('idx_name', uuid)
    status: Mapped[int] = mapped_column(insert_default=0, comment="任务状态 0 待执行 1执行中 2完成 3失败 ")
    t_type: Mapped[int] = mapped_column(comment="任务类型 0要素抽取 1ocr识别 2表格识别 3印章识别")
    sub_type: Mapped[Optional[int]] = mapped_column(comment="二级任务类型 0调用ocr 1调用nlp/llm 2format")
    
    file_count: Mapped[int] = mapped_column(comment="文件数量")
    ori_file_count: Mapped[int] = mapped_column(comment="原始文件数量")
    
    file_id: Mapped[Optional[int]] = mapped_column(insert_default=None, comment="输入文件id 只在子任务中记录")
    ori_file_id: Mapped[Optional[int]] = mapped_column(insert_default=None, comment="原始文件id 只在子任务中记录")
    
    model_label: Mapped[Optional[str]] = mapped_column(String(999), comment="调用模型标识")
    merge: Mapped[int] = mapped_column(insert_default=1, comment="否0 是1 是否合并")
    
    # 关联 sub_task 场景 用户 消息 文件 抽取结果
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('task.id', ondelete='SET NULL'), comment="父级任务标识")
    
    parent_task: Mapped[Optional["Task"]] = relationship(back_populates="sub_task", remote_side=[id]) # remote_side 表示为多对一 唯一的那一边
    sub_task: Mapped[Optional[List["Task"]]] = relationship(foreign_keys=[parent_id], back_populates="parent_task")
    
    # 关联场景信息
    scene_id: Mapped[Optional[int]] = mapped_column('scene_id', Integer, ForeignKey('scene.id', ondelete='SET NULL'))
    scene: Mapped["Scene"] = relationship(back_populates="tasks", cascade="")

    user_id: Mapped[Optional[int]] = mapped_column('user_id', Integer, ForeignKey('user.id', ondelete='SET NULL'))
    user: Mapped["User"] = relationship(back_populates="tasks", cascade="")
    
    msg_task: Mapped[List["MSGTask"]] = relationship(back_populates="task", cascade="")

    files: Mapped[List["File"]] = relationship(back_populates="task", cascade="")

    ele_value: Mapped[Optional[List["EleValue"]]] = relationship(back_populates="task", cascade="")


class File(Base):
    __tablename__ = "file"
    id: Mapped[int] = mapped_column(primary_key=True)

    t_type: Mapped[int] = mapped_column(comment=""" 文件类别
                                        0 original_file  1 split_img  2 ocr_deal_img 3 ocr_json 
                                        4 ocr_merge_json 5 format_ocr_json  6  format_table_ocr_json
                                        7  ext_json   8  ext_merge_json  9 format_ext_json  10 seal_res_json 11 word2pdf
                                        """
                                        )
    t_type_name: Mapped[Optional[str]] = mapped_column(String(999), insert_default="", comment="文件类别名")
    page_no: Mapped[int] = mapped_column(insert_default=0, comment="页码")
    ori_page_no: Mapped[int] = mapped_column(insert_default=0, comment="在原文件中的页码")
    length: Mapped[Optional[int]] = mapped_column(insert_default=1, comment="文件长度")
    file_url: Mapped[str] = mapped_column(String(999), comment="fastdfs_url")
    file_name: Mapped[str] = mapped_column(String(999), comment="文件名")
    format: Mapped[int] = mapped_column(comment="文件格式 0jpg 1jpeg 2png 3tif 4pdf 5doc 6json")

    # 自关联
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('file.id', ondelete='SET NULL'), nullable=True,
                                                     comment="原文件标识")
    parent_file: Mapped[Optional["File"]] = relationship( back_populates="sub_file", remote_side=[id]) #原始文件标识 多文件区分的时候可以用到
    sub_file: Mapped[Optional[List["File"]]] = relationship(foreign_keys=[parent_id], back_populates="parent_file") #原始文件标识 多文件区分的时候可以用到

    # 关联 任务 消息
    task_id: Mapped[Optional[int]] = mapped_column('task_id', Integer, ForeignKey('task.id', ondelete='SET NULL'), nullable=True)  # 只关联主任务
    task: Mapped["Task"] = relationship(back_populates="files", cascade="")  # 只关联主任务

    ele_value: Mapped[Optional["EleValue"]] = relationship(back_populates="file", cascade="")  # 关联要素结果

    msg_task: Mapped[Optional["MSGTask"]] = relationship(back_populates="file", uselist=False, cascade="")  # 一对一


class MSGTask(Base):
    __tablename__ = "msg_task"
    msg_info: Mapped[str] = mapped_column(String(999), comment="任务信息")
    status: Mapped[int] = mapped_column(comment="任务状态")
    # 关联 任务以及文件
    task_id: Mapped[Optional[int]] = mapped_column('task_id', Integer, ForeignKey('task.id', ondelete='SET NULL'))
    task: Mapped["Task"] = relationship(back_populates="msg_task", cascade="")

    file_id: Mapped[Optional[int]] = mapped_column('file_id', Integer, ForeignKey('file.id', ondelete='SET NULL'))
    file: Mapped["File"] = relationship(back_populates="msg_task", uselist=False, cascade="")


class Element(Base):
    __tablename__ = "element"
    id: Mapped[int] = mapped_column(primary_key=True)
    ele_label: Mapped[str] = mapped_column(String(999), comment="对外输出要素标识")
    model_ele_label: Mapped[Optional[str]] = mapped_column(String(999), comment="模型中标识")
    ele_cn: Mapped[str] = mapped_column(String(999), comment="要素标识中文")
    is_group: Mapped[int] = mapped_column(comment="是否编组")
    t_type: Mapped[int] = mapped_column(insert_default=0, comment="要素类型 0 单值 1 多值 2 组标识")
    status: Mapped[int] = mapped_column(comment="状态")

    # 关联 场景 多对一  后处理一对一 以及 要素结果 一对多

    scene_id: Mapped[Optional[int]] = mapped_column('scene_id', Integer, ForeignKey('scene.id', ondelete='SET NULL'))
    scene: Mapped["Scene"] = relationship(back_populates="element")
    
    # 后处理
    post_process: Mapped["PostProcess"] = relationship(back_populates="element", cascade="")
    
    # 自关联形成组
    group_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('element.id', ondelete='SET NULL'), comment="关联组标识")
    group_ele: Mapped[Optional["Element"]] = relationship(foreign_keys=[group_id], remote_side=[id])
    
    ele_value: Mapped[Optional[List["EleValue"]]] = relationship(back_populates="element", cascade="")


class PostProcess(Base):
    __tablename__ = "post_process"
    path: Mapped[str] = mapped_column(String(999), comment="后处理路径")
    # 关联 要素
    element_id: Mapped[Optional[int]] = mapped_column('element_id', Integer, ForeignKey('element.id', ondelete='SET NULL'))
    element: Mapped["Element"] = relationship(back_populates="post_process", cascade="")


class EleValue(Base):
    __tablename__ = "ele_value"
    id: Mapped[int] = mapped_column(primary_key=True)
    page: Mapped[int] = mapped_column(insert_default=0, comment="页码")
    pos: Mapped[str] = mapped_column(String(999), comment="坐标")
    value: Mapped[Optional[str]] = mapped_column(String(999), insert_default="", comment="要素值")

    # 关联 任务 文件 要素 group
    task_id: Mapped[Optional[int]] = mapped_column('task_id', Integer, ForeignKey('task.id', ondelete='SET NULL'))
    task: Mapped["Task"] = relationship(back_populates="ele_value", cascade="")

    file_id: Mapped[Optional[int]] = mapped_column('file_id', Integer, ForeignKey('file.id', ondelete='SET NULL'))
    file: Mapped["File"] = relationship(back_populates="ele_value", cascade="")

    element_id: Mapped[Optional[int]] = mapped_column('element_id', Integer, ForeignKey('element.id', ondelete='SET NULL'))
    element: Mapped["Element"] = relationship(back_populates="ele_value", cascade="")

    group_id: Mapped[Optional[int]] = mapped_column('ele_value_id', Integer, ForeignKey('ele_value.id', ondelete='SET NULL'))
    group: Mapped[Optional["EleValue"]] = relationship(foreign_keys=[group_id], remote_side=[id])


if __name__ == "__main__":
    # 创建表格
    Base.metadata.create_all(engine)
