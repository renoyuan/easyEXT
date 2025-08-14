
# 初始化 PaddleOCR 实例
def ocr():
    from paddleocr import PaddleOCR
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
    

def tructur():
    
    from pathlib import Path
    from paddleocr import PPStructureV3

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
    
    
def extract():
    import time
    api_key="bce-v3/ALTAK-AB87SxCYXswPlU9oSB0mo/5cb2270048c2722a3b623b53f77179bf27da0231"  # your api_key
    from paddleocr import PPChatOCRv4Doc
    t1 = time.time()

    chat_bot_config = {
        "module_name": "chat_bot",
        "model_name": "ernie-3.5-8k",
        "base_url": "https://qianfan.baidubce.com/v2",
        "api_type": "openai",
        "api_key": api_key,  # your api_key
    }

    retriever_config = {
        "module_name": "retriever",
        "model_name": "embedding-v1",
        "base_url": "https://qianfan.baidubce.com/v2",
        "api_type": "qianfan",
        "api_key": api_key,  # your api_key
    }

    pipeline = PPChatOCRv4Doc(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False
    )

    visual_predict_res = pipeline.visual_predict(
        input="/home/en/reno/paddle-pipeline-demo/input/基金转换.jpg",
        # input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/vehicle_certificate-1.png",
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

        mllm_predict_res = pipeline.mllm_pred(
            input="https://paddle-model-ecology.bj.bcebos.com/paddlex/imgs/demo_image/vehicle_certificate-1.png",
            key_list=["驾驶室准乘人数"],
            mllm_chat_bot_config=mllm_chat_bot_config,
        )
        mllm_predict_info = mllm_predict_res["mllm_res"]

    visual_info_list = []
    for res in visual_predict_res:
        visual_info_list.append(res["visual_info"])
        layout_parsing_result = res["layout_parsing_result"]

    vector_info = pipeline.build_vector(
        visual_info_list, flag_save_bytes_vector=True, retriever_config=retriever_config
    )
    chat_result = pipeline.chat(
        key_list=["客户","基金名称","基金代码", "申请时间","确认时间", "基金转换金额", "基金转换份额", "交易类别", "手续费", "网点"],
        # key_list=["驾驶室准乘人数"],
        visual_info=visual_info_list,
        vector_info=vector_info,
        mllm_predict_info=mllm_predict_info,
        chat_bot_config=chat_bot_config,
        retriever_config=retriever_config,
    )
    
    print(chat_result)
    print("time cost: ", time.time() - t1)
extract()