#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend model
# CREATE_TIME: 2024/3/20 11:47
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from sqlmodel import Field, SQLModel,JSON
from datetime import datetime
from sqlalchemy import DateTime, func,Column
from typing import Optional
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy import Column
from uuid import uuid4
from sqlalchemy.sql import text 
from typing import Optional, Dict, Any 
class BaseModel(SQLModel):
    __abstract__ = True
    created_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )

class Scenes(SQLModel, table=True):
    __tablename__ = "scenes"
    id: int | None = Field(default=None, primary_key=True)
    scene_name: str
    f_id: int|None = None
    
    created_time: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )

class File(SQLModel, table=True):
    __tablename__ = "file"
    id: int | None = Field(default=None, primary_key=True)
    task_id: int
    status: int = 0 # 0-待处理 1-已处理 2 - 失败
    fdfs_id: str
    page: int|None = None
    taltol_page: int|None = None 
    
    created_time: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )
    
class Tasks(BaseModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    

    scene_id: int
    status: str # 0-待处理 1-处理中 2-已完成 3-失败
    task_status: str # 0-待处理 1-处理中 2-已完成 3-失败
    
    created_time:Optional[datetime]   = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )

class Elements(SQLModel, table=True):
    __tablename__ = "elements"
    id: int | None = Field(default=None, primary_key=True)
    scene_id: int
    element_type: Optional[str]
    element_config: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB)  # 使用 PostgreSQL 的 JSONB 类型
    )
    created_time: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )

class Taskresults(SQLModel, table=True):
    __tablename__ = "taskresults"

    id: int | None = Field(default=None, primary_key=True)
    task_id: str
    extracted_data: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB)  # 使用 PostgreSQL 的 JSONB 类型
    )
    data_status: int =0
    
    created_time: datetime | None = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 使用数据库的函数设置当前时间
            nullable=False
        )
    )
    
    updated_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),  # 必须要有默认值！
            onupdate=func.now(),        # 更新时自动设置当前时间
            nullable=False
        )
    )

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)
    
if __name__ == '__main__':
    from sqlmodel import Session, SQLModel, create_engine
    import json
    from dotenv import load_dotenv
    import os, sys
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
    print(sys.path)
    load_dotenv(r"../.env")
    DbConfig = os.getenv("DbConfig")
    print(DbConfig)
    DbConfig = json.loads(DbConfig) 
    SQLModel.metadata.clear() 
    engine = create_engine(f"postgresql+psycopg2://{DbConfig['user']}:{DbConfig['password']}@{DbConfig['host']}:{DbConfig['port']}/{DbConfig['database']}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        scene = Scenes(scene_name="test", f_id=2)
        session.add(scene)
        session.commit()
        session.refresh(scene)
        print(scene)

