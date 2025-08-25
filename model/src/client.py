from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="no-key-required"
)

response = client.completions.create(
    model="Qwen2-7B",
    prompt="量子计算的核心优势是",
    max_tokens=150,
    temperature=0.7
)
print(response.choices[0].text)