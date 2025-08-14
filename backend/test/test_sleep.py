"""
#!/usr/bin/env python
-*- coding: utf-8 -*-
PROJECT_NAME: /home/yss/idp_backend/test
CREATE_TIME: 2024-04-15 
E_MAIL: renoyuan@foxmail.com
AUTHOR: reno 
note:  测试fastapi 阻塞问题
"""

import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from api import router, auth_middleware


# 创建 FastAPI 应用实例
app = FastAPI()
@app.get("/test")
async def read_users(request: Request):
    sleep_() # 事件循环中导致阻塞
    # await sleep() # ok
    # await sleep_coroutine()  # ok
    return "ok"

async def sleep(): # ok
    await asyncio.sleep(20)

def sleep_(): 
    time.sleep(20)
    
async def sleep_coroutine(): # ok
    # loop = asyncio.get_event_loop()
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, time.sleep, 20)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)