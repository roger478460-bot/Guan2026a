import requests
from bs4 import BeautifulSoup
from google import genai

from google.genai import types
from google.genai import types

from flask import Flask, render_template, request,make_response, jsonify
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

client = genai.Client()


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
    link += "<a href=/read>讀取Firestore資料(根據lab遞減排序,取前4)</a><hr>"
    link += "<a href=/movie2>讀取近期上映的電影，寫入Firestore</a><hr>"
    link += "<a href=/movie3>查詢電影</a><hr>"
    link += "<a href=/road>路口事故統計</a><hr>"
    link += "<a href=/weather?city=臺中市>天氣預報</a><hr>"
    link += "<a href=/rate>本週新片進DB</a><hr>"
    link += "<a href=/demo>Demo 聊天機器人</a><hr>"
    return link


@app.route("/read")
def read():
    db = firestore.client()
    collection_ref = db.collection("靜宜資管2026a")
    
    # 執行抓取
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()
    
    data_list = list(docs) # 將結果轉成清單
    count = len(data_list) # 計算抓到幾筆
    
    Temp = f"<h1>資訊管理導論</h1>"
    Temp += f"<p>系統偵測：目前抓到 {count} 筆資料</p><hr>"
    
    for doc in data_list:
        Temp += f"資料內容：{str(doc.to_dict())}<br><br>"

    Temp += "<a href=/>回到網站首頁</a>"
    return Temp

@app.route('/ask', methods=['GET', 'POST']) 
def ask():
    if request.method == "POST":
        user_prompt = request.form.get('prompt', '')
        if not user_prompt:
            return "請輸入內容", 400
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=user_prompt,
            )
            return response.text
        except Exception as e:
            return f"發生錯誤: {str(e)}", 500

    else:    
        # 當使用者直接打開網頁 (GET) 時，顯示輸入框畫面
        return render_template("ask.html")

@app.route("/AI")
def AI():
    # 每次使用者拜訪該路徑時，直接使用全域的 client 呼叫模型
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents='我想查詢靜宜大學資管系的評價？',
    )
    
    # 回傳生成的文字
    return response.text

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

@app.route("/demo")
def demo():
    return render_template("demo.html")

@app.route("/messenger")
def messenger():
    return render_template("messenger.html")


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

@app.route("/weather", methods=["GET", "POST"])
def weather():
    # 預設城市
    city = "臺中市"
    
    # 如果使用者是透過按下「查詢」按鈕（POST）進來的
    if request.method == "POST":
        city = request.form.get("city")
    # 如果使用者是點擊連結（GET）進來的
    else:
        city = request.args.get("city") or "臺中市"

    # 處理「台」與「臺」並抓取資料
    city = city.replace("台", "臺")
    url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName={city}"
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    Data = requests.get(url, verify=False)
    
    # 建立頁面內容
    R = "<h1>三十六小時天氣預報</h1>"
    
    # 加入「輸入表單」
    R += f"""
    <form method="POST" action="/weather">
        <label>請輸入欲查詢的縣市：</label>
        <input type="text" name="city" placeholder="例如：臺北市" value="{city}">
        <button type="submit">查詢</button>
    </form>
    <hr>
    """
    
    try:
        json_data = json.loads(Data.text)
        records = json_data["records"]["location"][0]
        # Wx (天氣現象)
        weather_state = records["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        # PoP (降雨機率)
        rain_chance = records["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        
        R += f"<h3>{city} 目前天氣預報：</h3>"
        R += f"天氣狀況：{weather_state}<br>"
        R += f"降雨機率：{rain_chance} %<br>"
    except:
        R += f"<h3>暫時無法取得「{city}」的天氣資訊</h3>"
        R += "請確保輸入完整的縣市名稱（如：臺南市）。"

    R += "<br><br><a href=/>回到網站首頁</a>"
    return R


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

@app.route("/road")
def road():
    url = "https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    Data = requests.get(url, verify=False)
    Data.encoding = "utf-8"
    JsonData = json.loads(Data.text)

    # 1. 進行排序：根據「總件數」從大到小排序
    # 因為原始資料的總件數可能是字串，所以要用 int() 轉換後再比較
    SortedData = sorted(JsonData, key=lambda x: int(x["總件數"]), reverse=True)

    # 2. 取前 10 筆
    Top10 = SortedData[:10]

    R = "<h1>台中市十大肇事路口統計</h1>"
    R += "<ol>"  # 使用有序列表標籤，會自動顯示 1. 2. 3...
    
    for item in Top10:
        R += f"<li><b>{item['路口名稱']}</b>：總共發生 {item['總件數']} 件事故</li>"
    
    R += "</ol>"
    R += "<br><a href=/>回到網站首頁</a>"
    return R

@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    now = year + "/" + month + "/" + day
    return render_template("today.html", datetime = str(now))

@app.route("/webhook", methods=["POST"])
def webhook():
    # 1. 取得 Dialogflow 傳來的 JSON 資料
    req = request.get_json(force=True)
    
    # 2. 取得 Intent 的 Action 名稱 (確保與 Dialogflow 設定一致)
    action = req["queryResult"]["action"]
    
    if action == "rateChoice":
        # 3. 取得 Dialogflow 解析出的參數 (電影分級)
        # 注意：如果 Dialogflow 傳來的是 "G", "P", "F2" 等，我們需要對應到資料庫裡的中文
        rate = req["queryResult"]["parameters"]["rate"]
        
        # 為了保證查詢成功，可以做一個簡單的轉換（如果你的參數是英文縮寫的話）
        rate_map = {
            "G": "普遍級",
            "P": "保護級",
            "F2": "輔12級",
            "F5": "輔15級",
            "R": "限制級"
        }
        # 如果傳進來的是 G，就轉換成 普遍級；如果已經是中文就維持原樣
        search_rate = rate_map.get(rate, rate)

        # 4. 準備回應的開頭（作業要求顯示姓名）
        info = f"我是王冠元設計的電影聊天機器人。您查詢的分級是：{search_rate}。\n\n"
        
        # 5. 連接 Firestore 查詢
        db = firestore.client()
        collection_ref = db.collection("本週新片含分級")
        
        # 查詢條件：rate 欄位等於使用者選擇的分級
        docs = collection_ref.where("rate", "==", search_rate).get()
        
        movie_titles = []
        for doc in docs:
            movie_data = doc.to_dict()
            title = movie_data.get("title")
            link = movie_data.get("hyperlink")
            
            # 把名稱和網址接在一起，用換行 (\n) 隔開比較美觀
            movie_titles.append(f"🎬 {title}\n連結：{link}")
        
        # 6. 組合最終訊息
        if movie_titles:
            info += "本週上映的相關電影有：\n" + "、".join(movie_titles)
        else:
            info += f"抱歉，目前本週新片中沒有找到 {search_rate} 的電影。"

        # 7. 回傳給 Dialogflow
        return make_response(jsonify({"fulfillmentText": info}))
        
    # 修正：如果 action 是 input.unknown，或者是空字串、或是任何沒對接到的動作
    elif action == "input.unknown" or action == "":
        instruction_text = (
            "你是一個熱心且知識豐富的專業智慧助理。"
            "對於使用者的提問，請回覆重點的關鍵字，不要重述問題。"         
        )

        ai_config = types.GenerateContentConfig(
            max_output_tokens=500, 
            system_instruction=instruction_text
        )

        response = client.models.generate_content(
            model='gemini-3.1-flash-lite', 
            contents=req["queryResult"]["queryText"],
            config=ai_config,
        )

        if response.text:
            info = response.text
        else:
            info = "抱歉，我現在無法生成回應，請稍後再試。"

        # ✨【超級重點】注意這個 return 的縮排！必須在 elif 裡面！
        return make_response(jsonify({"fulfillmentText": info}))

    # 只有上面所有條件都不符合（例如收到了非空值的其他自訂 action），才會跑到這裡
    return make_response(jsonify({"fulfillmentText": f"動作未定義 (收到的 Action 是: {action})"}))


@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

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



if __name__ == "__main__":
    app.run()
