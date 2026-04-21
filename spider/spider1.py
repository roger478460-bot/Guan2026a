import requests
from bs4 import BeautifulSoup

url = "https://guan2026a.vercel.app/about"
Data = requests.get(url)
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select("#pic")

for item in result:
	print(item.text)
	print(item.get("src"))
	print()

