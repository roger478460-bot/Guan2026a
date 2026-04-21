import requests
from bs4 import BeautifulSoup

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

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

# 在 web.py 的開頭導入必要的套件 (如果還沒導入)
import requests
from bs4 import BeautifulSoup

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

# 在 web.py 中新增這個路由
@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    # 準備一個字串來存放結果
    movies_html = "<h1>即將上映電影</h1>"
    
    for item in result:
        # 加上防呆機制，避免爬蟲找不到標籤時崩潰
        img_tag = item.find("img")
        a_tag = item.find("a")
        
        if img_tag and a_tag:
            title = img_tag.get("alt")
            link = "https://www.atmovies.com.tw" + a_tag.get("href")
            movies_html += f"<div><a href='{link}' target='_blank'>{title}</a></div>"
    
    movies_html += "<br><br><a href='/'>回首頁</a>"
    return movies_html


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x, dep = y)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是:" + user + "; 密碼為:" + pwd
        return result
    else:
        return render_template("account.html")

@app.route("/math", methods=["GET", "POST"])
def math():
    if request.method == "POST":
        try:
            # 從表單取得資料並轉型
            x = float(request.form["x"])
            y = float(request.form["y"])
            opt = request.form["opt"]
            result = None

            # 你的邏輯處理
            if opt == "/" and y == 0:
                res_text = "錯誤：除數不能為 0"
            else:
                match opt:
                    case "+": result = x + y
                    case "-": result = x - y
                    case "*": result = x * y
                    case "/": result = x / y
                    case _: res_text = "輸入的運算符號不正確"
                
                if result is not None:
                    res_text = f"{x} {opt} {y} 的結果是 {result}"
            
            return f"<h1>計算結果</h1><p>{res_text}</p><a href='/math'>重新計算</a> | <a href='/'>回首頁</a>"

        except ValueError:
            return "<h1>輸入錯誤</h1><p>請確保你輸入的是數字</p><a href='/math'>返回</a>"
    else:
        return render_template("math.html")
@app.route('/cup', methods=["GET"])
def cup():
    # 檢查網址是否有 ?action=toss
    #action = request.args.get('action')
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        # 0 代表陽面，1 代表陰面
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        # 判斷結果文字
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)


if __name__ == "__main__":
    app.run()
