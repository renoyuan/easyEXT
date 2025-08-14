# idp_backend

使用python 后端服务作为模型调度系统的替代方案

## 功能实现

使用消息机制 实现对现有 ocr 表格识别 要素抽取 模型调用 

接口见 doc/赢时胜OCR外部调用接口文档v1.4.5.docx

## 代码模块
backend/celery_task -- 消息任务

backend/db_model -- 数据库

backend/api -- api接口


## 任务
关于任务队列

ocr 任务

merge_ocr 任务

ext 任务

merge_ext 任务

关于任务超时

ocr 任务 5s

merge_ocr 任务  ocr * num + 5s

ext 任务

merge_ocr + 5s~1000s

merge_ext 任务

ext * num  + 5s


## 数据库迁移
1. 安装 Alembic
pip install alembic

2. 初始化 Alembic
alembic init alembic

3. 创建迁移脚本
alembic revision --autogenerate -m "Your message here"

4. 应用迁移脚本
alembic upgrade head

插入初始数据
运行脚本 backend/db_model/insert_data.py

## 部署

后端服务启动
python main.py

消息任务启动 win上启动加上 -P eventlet

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue1 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue2 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue3 --concurrency=1

python -m celery  -A celery_task:app worker --loglevel=INFO -Q queue4 --concurrency=1

