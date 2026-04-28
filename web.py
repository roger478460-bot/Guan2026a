import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
#from google.cloud.firestore_v1.base_query import FieldFilter

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)

from flask import Flask,render_template,request
from datetime import datetime
import random
app = Flask(__name__)


@app.route("/")
def index():
    link =  "<h1>歡迎進入王冠元的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於冠元</a><hr>"
    link += "<a href=/welcome?u=冠元&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/math>數學運算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<a href=/read4>老師查詢</a><hr>"
    link += "<a href=/sp1>爬蟲課程</a><hr>"
    link += "<a href=/movie>即將上映的電影</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><br>"
    link += "<br><a href=/movie2>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    link += "<br><a href=/movie3>查詢電影</a><br>"
    return link


@app.route("/read")
def read():
    db = firestore.client()
    
    Temp = ""
    collection_ref = db.collection("靜宜資管2026a")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()
    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"


    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"

@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 


@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    result = "<h1>電影關鍵字查詢</h1>"
    # 顯示查詢表單
    result += """
    <form method="POST">
        <input type="text" name="keyword" placeholder="請輸入電影名稱關鍵字">
        <button type="submit">查詢</button>
    </form>
    <hr>
    """
    
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        # 取得所有電影資料
        docs = db.collection("電影").get()
        
        found = False
        result += f"<h2>查詢結果：{keyword}</h2>"
        for doc in docs:
            movie = doc.to_dict()
            # 判斷輸入的關鍵字是否在電影標題中
            if keyword in movie.get("title", ""):
                found = True
                result += f"""
                <div style='margin-bottom:10px;'>
                    <a href='{movie.get('hyperlink')}' target='_blank'>{movie.get('title')}</a><br>
                    上映日期: {movie.get('showDate')}
                </div>
                """
        if not found:
            result += "抱歉，找不到相關電影。"
            
    result += "<br><a href='/'>回首頁</a>"
    return result


@app.route("/read4", methods=["GET", "POST"])
def read4():
    if request.method == "POST":
        keyword = request.form.get("keyword")
        db = firestore.client()
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()
       
        result = f"<h1>查詢結果</h1>"
        result += f"<p>您查詢的關鍵字是：{keyword}</p><hr>"
       
        found = False
        for doc in docs:
            user = doc.to_dict()
            # 實作圖片中的邏輯：判斷關鍵字是否在老師姓名中
            if keyword in user.get("name", ""):
                found = True
                result += f"● {user['name']} 老師的研究室在 {user.get('lab', '未知')}<br>"
       
        if not found:
            result += "抱歉，找不到符合條件的老師。"
           
        result += "<br><br><a href='/read4'>重新查詢</a> | <a href='/'>回首頁</a>"
        return result
    else:
        # 顯示查詢介面
        html = """
        <h1>查詢老師研究室</h1>
        <form method="POST">
            <label>請輸入老師姓名關鍵字：</label>
            <input type="text" name="keyword">
            <button type="submit">查詢</button>
        </form>
        <br><a href="/">回首頁</a>
        """
        return html


@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁</a>"


@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    now = year + "/" + month + "/" + day
    return render_template("today.html", datetime = str(now))

@app.route("/sp1")
def sp1():
    R = ""
    url = "https://guan2026a.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select("td a")

    for item in result:
        R += item.text + "<br>" + item.get("href") + "<br><br>"
    return R

# 在 web.py 中新增這個路由import requests
from bs4 import BeautifulSoup



if __name__ == "__main__":
    app.run()
