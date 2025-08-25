#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: idp_backend file_deal
# CREATE_TIME: 2024/3/27 19:06
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note: 文件处理 1 图像旋转 2 印章消除 3 pdf/ofd 解析  4 pdf/ofd 拆页 5 文件上传
from typing import List,Optional
import io
import os
import uuid

import fitz
from PIL import Image
from fastapi import UploadFile,Query
import numpy as np
from utils.fastdfs import fdfs


def pdf2img(pdfbytes):
    image_list = []

    doc = fitz.open(stream=pdfbytes, filetype="pdf")

    for page in doc:
        rotate = int(0)
        zoom_x, zoom_y = 1.6, 1.6
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        image = np.ndarray((pix.height, pix.width, 3), dtype=np.uint8, buffer=pix.samples)
        image = Image.fromarray(image)
        byte_stream = io.BytesIO()
        image.save(byte_stream, format='PNG') #, format='JPEG'
        
        image_list.append(byte_stream.getvalue())

    return image_list


class FileDeal(object):
    def tif_deal(self, contents):
        with Image.open(io.BytesIO(contents)) as img:
            # 创建一个 BytesIO 对象，用于保存 JPEG 字节数据
            jpeg_byte_stream = io.BytesIO()

            # 将图像保存为 JPEG 格式，并将结果写入 BytesIO 对象中
            img.convert("RGB").save(jpeg_byte_stream, format="JPEG")

            # 获取 JPEG 字节数据
            jpeg_bytes = jpeg_byte_stream.getvalue()
            return jpeg_bytes

    def process_data(self, filename, contents, page, file_type="", container=None, fdfs_id="", f_fdfs_id="", ori_page=0, ori_file_no=0):
        """文件上传"""
        # file_uuid = uuid.uuid4()
        file_type = file_type if file_type else os.path.splitext(filename)[1][1:].lower()
        if fdfs_id:
            fdfs_id = fdfs_id
        else:
            res_upload = fdfs.upload_by_buffer(contents, file_type)
            fdfs_id = res_upload['Remote file_id'].decode("utf-8") if res_upload != -1 else ""
            assert fdfs_id, "fastdfs 异常上传文件失败"
        print("==="*100,id(fdfs))
        fdfs_id = fdfs_id if fdfs_id else fdfs.upload_by_buffer(contents, file_type)['Remote file_id'].decode("utf-8")
        print("ori_page",ori_page)
        file_info = {
            "filename": filename,
            # "file_uuid": file_uuid,
            "file_type": file_type,
            "fdfs_id": fdfs_id,
            "page": page,
            "ori_page": ori_page, # 源文件中的page
            "ori_file_no": ori_file_no, # 源文件索引号
            "length": 1,
        }
        if f_fdfs_id:
            file_info["f_fdfs_id"] = f_fdfs_id
        container.append(file_info)
        return fdfs_id

    async def __call__(self, originalFiles: List[UploadFile], rotate: Optional[int] = 0, sealErasure: Optional[int] = 0, ):
        # todo  异常处理后面管可能需要统一加
        res = {
            "ori_info": {
                "file_length": 0,
                "file_info": []
            },
            "deal_info": {
                "file_length": 0,
                "file_info": []
            }
        }
        print(originalFiles)
        file_length = 0
        deal_file_length = 0
        res["ori_info"]["file_length"] = file_length
        res["deal_info"]["file_length"] = deal_file_length

        for  ori_no, file in enumerate(originalFiles) :
            filename = file.filename
            contents = await file.read()
            file_type = os.path.splitext(filename)[1][1:].lower()

            fdfs_id = self.process_data(filename, contents, file_length, file_type, res["ori_info"]["file_info"], "", "", ori_file_no=ori_no)
            file_length +=1
            # 根据文件类型 处理文件
            if file_type in ["jpg", "png", "jpeg"]:

                _ = self.process_data(filename, "", deal_file_length, file_type, res["deal_info"]["file_info"], fdfs_id,
                                      fdfs_id,ori_file_no=ori_no)
                deal_file_length += 1

            elif file_type in ["tif", ]:
                jpeg_bytes = self.tif_deal(contents)
                _ = self.process_data(os.path.splitext(filename)[0] + ".jpg", jpeg_bytes, deal_file_length, "jpg", res["deal_info"]["file_info"], "",
                                      fdfs_id,ori_file_no=ori_no)
                deal_file_length += 1

            elif file_type in ["pdf", ]:
                pdf_img = pdf2img(contents)
                res["ori_info"]["file_info"][-1]["length"] = len(pdf_img)
                for img_no, img in enumerate(pdf_img):
                    img_name = os.path.splitext(filename)[0] + f"_{img_no}" + ".jpg"
                    _ = self.process_data(img_name, img, deal_file_length, "jpg",
                                          res["deal_info"]["file_info"], "",
                                          fdfs_id,ori_page=img_no,ori_file_no=ori_no)
                    deal_file_length += 1
            else:
                # 不支持类型
                print(f"不支持类型{filename}")
                pass
        
        res["ori_info"]["file_length"] = file_length
        res["deal_info"]["file_length"] = deal_file_length
        return res

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__))))
    FileDeal