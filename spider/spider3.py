import requests
from bs4 import BeautifulSoup

url = "https://guan2026a.vercel.app/about"
Data = requests.get(url)
#print(Data.text)
sp = BeautifulSoup(Data.text, "html.parser")
result=sp.select("td a")

for item in result:
	print(item)
	print()

