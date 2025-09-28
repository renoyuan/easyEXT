# -*- coding: utf-8 -*-

"""
# @Time    : 2022/1/17 0017 14:39
# @Author  : Silva
# @File    : client.py
python3 FastDFS客户端连接 base with pip install py3Fdfs

包下载超时修复:
    vim fdfs_client/storage_client.py
    将 tcp_recv_file 函数中 remain_bytes -= buffer_size  改为 remain_bytes -= recv_size
"""
import os, sys
import traceback
import json

from functools import wraps
sys.path.append('../../')
from fdfs_client.client import Fdfs_client, get_tracker_conf

from loguru import logger
__ALL__ = ['FDFS']

exception_tile = 'Error Msg FastDFS'

fdfs_client_path =  os.path.abspath(os.path.dirname(__file__)) + "/fdfs_client.conf"

def u2b(strings):
    if isinstance(strings, str):
        return strings.encode('utf8')

def b2u(strings):
    if isinstance(strings, bytes):
        return strings.decode('utf8')

def except_wrap(msg='异常信息'):
    '''
    # 异常捕获
    msg用于自定义函数的提示信息
    :param msg: 提示字符
    :return: 异常时返回-1
    '''
    def except_execute(func):
        @wraps(func)
        def execept_print(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                sign = '=' * 60 + '\n'
                print(f'>>>Error Function：\t{func.__name__}\n>>>{msg}：\t{e}')
                print(f'{sign}{traceback.format_exc()}{sign}')
                return -1
        return execept_print
    return except_execute



class FDFS(object):
    def __init__(self, client_file=fdfs_client_path, fdfs_dict={}):
        self.client_file = client_file
        self.fdfs_dict = fdfs_dict
        self.client = self.create_client()

    def create_client(self):
        if self.fdfs_dict:
            trackers = self.fdfs_dict
        else:
            trackers = get_tracker_conf(self.client_file)
        client = Fdfs_client(trackers)
        return client

    @except_wrap(exception_tile)
    def download(self, file_name, file_id):
        '''文件下载'''
        file_id = u2b(file_id)
        ret_download = self.client.download_to_file(file_name, file_id)
        # print(ret_download)
        return ret_download

    @except_wrap(exception_tile)
    def download_to_buffer(self, remote_file_id, offset=0, down_bytes=0):
        '''文件流下载'''
        remote_file_id = u2b(remote_file_id)
        content_bytes = None
        try:
            download_res = self.client.download_to_buffer(remote_file_id, offset=offset, down_bytes=down_bytes)
           
            content_bytes= download_res['Content']
        except Exception as e:
            logger.error(f"download_res:{e} {'='*50} {download_res}")
            
        return content_bytes
    
    @except_wrap(exception_tile)
    def upload(self, file_name):
        '''上传本地文件'''
        ret_upload = self.client.upload_by_filename(file_name)
        return ret_upload
    
    def upload_data(self, data, data_type='json'):
        """上传多种文件格式"""
        if data_type == 'file':
            ret_upload = fdfs.upload(data)
        else:
            if data_type in ['json', 'data', 'dict']:
                if not isinstance(data, bytes):
                    data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            elif data_type in ['jpg', 'img', 'png']:
                IO = BytesIO()
                img = Image.fromarray(cv2.cvtColor(data, cv2.COLOR_BGR2RGB))
                # img = Image.fromarray(data)
                img.save(IO, format='PNG')
                data = IO.getvalue()
                # 图片最终转成jpg后缀
                data_type = 'jpg'
            else:
                print('data_type 错误')
                return None
            ret_upload = self.upload_by_buffer(data, file_ext_name=data_type)
        # 检验 fastdfs 操作
        if ret_upload == -1:
            print(f'data_type 错误 ret_upload {ret_upload}')
            return None
        else:
            result_file_id = b2u(ret_upload['Remote file_id'])
            return result_file_id
    
    @except_wrap(exception_tile)
    def upload_by_buffer(self, filebuffer, file_ext_name='jpg', meta_dict=None):
        '''上传文件流'''
        file_id = None
        ret_upload = self.client.upload_by_buffer(filebuffer, file_ext_name=file_ext_name, meta_dict=meta_dict)
        # print(f"upload_by_buffer:{upload_res} {'>'*50}",)
        try:
            file_id = b2u(ret_upload['Remote file_id'])
        except:
            logger.error(f"upload_by_buffer:{ret_upload} {'='*50}")
        return file_id

    @except_wrap(exception_tile)
    def delete(self, file_id):
        '''删除指定文件'''
        file_id = u2b(file_id)
        ret_delete = self.client.delete_file(file_id)
        return ret_delete


def multy_test():
    from threading import Thread
    fdfs = FDFS()
    t_list = []
    for i in range(60):
        file_id = "group1/M00/00/3F/wKgBSWHlIEmAKQKUAAV0qzMQXts346.pdf"
        download_file = f"download_wKgBSWHlIEmAKQKUAAV0qzMQXts346_{i}.pdf"
        t = Thread(target=fdfs.download, args=(download_file, file_id))
        t.start()
        t_list.append(t)
    for t in t_list:
        t.join()
        # print(t.result)


if __name__ == "__main__":
    from dotenv import load_dotenv
    env_path = r"../.env"
    load_dotenv(env_path)
    fdfs = FDFS(fdfs_dict=json.loads(os.getenv("FastDFSConfig")) )
    upload_file = "F:\opensource\easyEXT\doc\架构.png"
   
    
    # 测试上传 
    f = open(upload_file,"rb")
    bytes_c = f.read()
    
    # upload_res = fdfs.upload(upload_file) # 本地文件上传
    file_id = fdfs.upload_by_buffer(bytes_c, file_ext_name='png') # 文件流上传
    
    # 测试下载
    # download_res = fdfs.download_to_buffer(file_id)
    content_bytes = fdfs.download_to_buffer(file_id)
    with open("11.jpg","wb") as f:
        f.write(content_bytes)
    


   

    # '{'{'Remote file_id': b'group1/M00/00/3F/wKgBSWHlIEmAKQKUAAV0qzMQXts346.pdf', 'Content': 'download_wKgBSWHlIEmAKQKUAAV0qzMQXts346.pdf', 'Download size': '349.17KB', 'Storage IP': b'192.168.1.73'}'
    # upload
    # '{'Group name': b'group1', 'Remote file_id': b'group1/M00/00/3F/wKgBSWHqaaWAJq1TAAV0qzMQXts907.pdf', 'Status': 'Upload successed.', 'Local file name': 'C:\\Users\\Administrator\\Documents\\H3_AP202201101539534903_1.pdf', 'Uploaded size': '349.17KB', 'Storage IP': b'192.168.1.73'}'