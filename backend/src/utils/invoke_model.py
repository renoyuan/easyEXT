
import os
from pathlib import Path

from dotenv import load_dotenv
from paddleocr import PaddleOCR
from paddleocr import PPChatOCRv4Doc
from paddleocr import PPStructureV3
from loguru import logger


from .tools import timeit

from abc import ABC, abstractmethod

api_key = os.getenv("paddle_api_key")

class InvokeModelBase():
    @abstractmethod
    def _invoke_model(self,*args,**kwargs):
        """
        强制子类实现的抽象方法
        """
        pass
    
    @abstractmethod
    def _postprocessing(self,model_res):
        """
        后处理
        """
        pass

    def __call__(self,*args,**kwargs):
        """
        调用模型
        """

        return self._postprocessing(self._invoke_model(*args,**kwargs))


class InvokeModel(InvokeModelBase):
    """
    该类用于封装模型调用相关的功能，可根据传入的模型名称初始化，并执行模型的抽取操作。
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = os.getenv("paddle_api_key")
        self.chat_bot_config = {
            "module_name": "chat_bot",
            "model_name":"ernie-3.5-8k",
            # "model_name": "Qwen3-8B", #"ernie-3.5-8k",
            "base_url": "https://qianfan.baidubce.com/v2",
            # "base_url": "http://localhost:8000/v1",#"https://qianfan.baidubce.com/v2",
            "api_type": "openai",
            # "api_key": "EMPTY",# self.api_key,  # your api_key
            "api_key": self.api_key,  # your api_key
        }
        self.retriever_config = {
            "module_name": "retriever",
            # "model_name": "Qwen3-Embedding-0.6B", #"embedding-v1",
            "model_name": "embedding-v1",
            "base_url": "https://qianfan.baidubce.com/v2",
            # "base_url": "http://localhost:8000/v1", #"https://qianfan.baidubce.com/v2",
            "api_type":"qianfan",
            # "api_type": "openai",# "qianfan",
            "api_key": self.api_key,  # your api_keyself
            # "api_key": "EMPTY",#self.api_key,  # your api_keyself
        }
        self.pipeline = PPChatOCRv4Doc(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            retriever_config={"debug": True}
        )
        
    @timeit
    def extract(self,input,key_list):
        # ocr
        visual_predict_res = self.pipeline.visual_predict(
            input=input,
            use_common_ocr=True,
            use_seal_recognition=True,
            use_table_recognition=True,
        )

        mllm_predict_info = None
        use_mllm = False
        
        # 如果使用多模态大模型，需要启动本地 mllm 服务，可以参考文档：https://github.com/PaddlePaddle/PaddleX/blob/release/3.0/docs/pipeline_usage/tutorials/vlm_pipelines/doc_understanding.md 进行部署，并更新 mllm_chat_bot_config 配置。
        if use_mllm:
            mllm_chat_bot_config = {
                "module_name": "chat_bot",
                "model_name": "PP-DocBee",
                "base_url": "http://127.0.0.1:8080/",  # your local mllm service url
                "api_type": "openai",
                "api_key": "api_key",  # your api_key
            }

            mllm_predict_res = self.pipeline.mllm_pred(
                input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/vehicle_certificate-1.png",
                key_list=["驾驶室准乘人数"],
                mllm_chat_bot_config=mllm_chat_bot_config,
            )
            mllm_predict_info = mllm_predict_res["mllm_res"]

        visual_info_list = []
        for res in visual_predict_res:
            visual_info_list.append(res["visual_info"])
            layout_parsing_result = res["layout_parsing_result"]

        logger.info(f"layout_parsing_result {layout_parsing_result} \n")
        # 构建向量
        vector_info = self.pipeline.build_vector(
            visual_info_list, flag_save_bytes_vector=True, retriever_config=self.retriever_config
        )
        logger.info(f"vector_info {vector_info}\n")
        # 调用模型
        chat_result = self.pipeline.chat(
            key_list=key_list,
            visual_info=visual_info_list,
            vector_info=vector_info,
            mllm_predict_info=mllm_predict_info,
            chat_bot_config=self.chat_bot_config,
            retriever_config=self.retriever_config,
        )
        return chat_result

    def _invoke_model(self,input,key_list):

       return self.extract(input,key_list)
    def _postprocessing(self,model_res):
        """
        后处理
        """
        finally_res = []
        finally_res.append(model_res["chat_res"])

        return finally_res

    # 初始化 PaddleOCR 实例
    def ocr(self,):
        
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False)
        print(ocr)
        # 对示例图像执行 OCR 推理 
        result = ocr.predict(
            input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/general_ocr_002.png")
            
        # 可视化结果并保存 json 结果
        for res in result:
            res.print()
            res.save_to_img("output")
            res.save_to_json("output")
    

    def structur(self,):
        


        pipeline = PPStructureV3(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False
        )

        # For Image
        output = pipeline.predict(
            input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/pp_structure_v3_demo.png",
            )

        # 可视化结果并保存 json 结果
        for res in output:
            res.print() 
            res.save_to_json(save_path="output") 
            res.save_to_markdown(save_path="output") 
    




    
if __name__=="__main__":
    env_path = r"F:\opensource\easyEXT\backend\src\.env"
    load_dotenv(env_path)
    key_list=["客户","基金名称","基金代码", "申请时间","确认时间", "基金转换金额", "基金转换份额", "交易类别", "手续费", "网点"]
    img_paht=r"F:\opensource\easyEXT\doc\jijinzhuanhuan.jpg"
    invoke_model = InvokeModel("PPChatOCRv4Doc")
    print(invoke_model.extract(img_paht,key_list))