#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend model
# CREATE_TIME: 2024/3/20 11:47
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from sqlmodel import Field, SQLModel,JSON
from datetime import datetime


class Scenes(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scene_name: str
    f_id: int|None = None

    created_time: datetime | None = None

class Tasks(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    scene_id: int
    status: str
    task_status: str
    created_time: datetime | None = None
    uodate_time: datetime | None = None
     
class Taskresults(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    task_id: str
    extracted_data: int
    data_status: str | None = None
    created_time: datetime | None = None
    
if __name__ == '__main__':
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
    with Session(engine) as session:
        scene = Scenes(scene_name="test", f_id=2)
        session.add(scene)
        session.commit()
        session.refresh(scene)
        print(scene)

