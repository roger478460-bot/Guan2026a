from google import genai

client = genai.Client(api_key='AIzaSyBE6cYXKsjKKyug_6oqz9wx009llCZaz3w')

Question = input("請問您要問AI什麼問題?")

# 直接體驗最新一代的 3.5 Flash 
response = client.models.generate_content(
    model='gemini-3.5-flash',
    contents=Question,
)

print(response.text)
