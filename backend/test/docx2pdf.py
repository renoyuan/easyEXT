from spire.doc import *

# 加载Word文档
document = Document()
document.LoadFromFile("关于中国人寿养老保险股份有限公司养老金产品的提示.docx")

# 保存为PDF
document.SaveToFile("output.pdf", FileFormat.PDF)