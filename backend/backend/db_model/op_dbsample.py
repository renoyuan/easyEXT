#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend op_db
# CREATE_TIME: 2024/3/20 18:43
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from .model import engine, User, Scene, ModelInfo, Task, File, MSGTask, Element, PostProcess, EleValue
from sqlalchemy.orm import Session

with Session(engine) as session:
    spongebob = User(
        name="spongebob",
        fullname="Spongebob Squarepants",
        addresses=[Address(email_address="spongebob@sqlalchemy.org")],
    )
    sandy = User(
        name="sandy",
        fullname="Sandy Cheeks",
        addresses=[
            Address(email_address="sandy@sqlalchemy.org"),
            Address(email_address="sandy@squirrelpower.org"),
        ],
    )
    patrick = User(name="patrick", fullname="Patrick Star")
    session.add_all([spongebob, sandy, patrick])
    session.commit()
################## 查
from sqlalchemy import select

session = Session(engine)

stmt = select(User).where(User.name.in_(["spongebob", "sandy"])) # 相当于生成了查询语句

for user in session.scalars(stmt): # 执行查询是 session.scalars(stmt)
    print(user)
# 多表查询
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "sandy")
    .where(Address.email_address == "sandy@sqlalchemy.org")
)
sandy_address = session.scalars(stmt).one()
# 这里 sandy_address 就相当于Address 的并集了User 的内容

##################### 改
stmt = select(User).where(User.name == "patrick")
patrick = session.scalars(stmt).one()
patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))
sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

session.commit()

############## 删除
sandy = session.get(User, 2)
sandy.addresses.remove(sandy_address) # 确认后删除
session.flush()  # 提交 flush 相当于暂存提高 性能 减少 commit 减少资源消耗 这里使用flush 确认remove删除 否则不会删除
session.delete(patrick) # 立刻删除
session.commit()