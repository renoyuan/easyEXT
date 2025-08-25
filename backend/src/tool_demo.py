from langchain.tools import Tool
from paddleocr import PPChatOCRv4Doc

# 1. 初始化PPChatOCRv4流水线
pipeline = PPChatOCRv4Doc()

def run_ppchatocrv4(query: str, file_path: str) -> str:
    # 2. 执行PPChatOCRv4抽取
    result = pipeline.chat(key_list=[query], input=file_path)
    return result["chat_res"][query]

# 3. 封装为LangChain Tool
ocr_tool = Tool(
    name="PPChatOCRv4_Extractor",
    func=run_ppchatocrv4,
    description="从图片/PDF中抽取关键信息"
)

# 4. 集成到LangChain Agent
from langchain.agents import initialize_agent
agent = initialize_agent(
    tools=[ocr_tool], 
    llm=llm, 
    agent="zero-shot-react-description"
)
agent.run("从vehicle_certificate.png中提取驾驶室准乘人数")