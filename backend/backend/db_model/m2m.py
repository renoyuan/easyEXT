#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend m2m
# CREATE_TIME: 2024/3/21 18:57
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# 中间表表示学生和课程之间的关联关系
student_course_association = Table('student_course_association', Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id')),
    Column('course_id', Integer, ForeignKey('courses.id'))
)

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    courses = relationship("Course", secondary=student_course_association, back_populates="students")

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    students = relationship("Student", secondary=student_course_association, back_populates="courses")

# 创建数据库引擎和会话
engine = create_engine('mysql+pymysql://root:Tlrobot123.@192.168.1.137:3306/idp?charset=utf8mb4')
Session = sessionmaker(bind=engine)
session = Session()

# 创建表结构
Base.metadata.create_all(engine)

# 插入一些数据
student1 = Student(name='Alice')
student2 = Student(name='Bob')
course1 = Course(name='Math')
course2 = Course(name='Physics')

student1.courses.append(course1)
student1.courses.append(course2)
student2.courses.append(course2)

session.add_all([student1, student2, course1, course2])
session.commit()

# 查询学生所选的课程
print(student1.courses)
print(student2.courses)
