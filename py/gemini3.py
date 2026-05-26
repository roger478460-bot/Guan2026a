import os
from google import genai

# 1. 複製你的金鑰，並在後面加上 .strip() 防止任何隱形空白
raw_key = "AIzaSyBE6cYXKsjKKyug_6oqz9wx009llCZaz3w"
correct_key = raw_key.strip()

# 2. 注入環境變數
os.environ["GEMINI_API_KEY"] = correct_key

# 3. 初始化 Client
client = genai.Client()

# 4. 開始對話
chat = client.chats.create(model="gemini-2.5-flash")
response1 = chat.send_message('靜宜資管有什麼特色')
print(response1.text)