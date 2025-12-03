import os
import aiofiles
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # 新增：處理靜態檔案
from fastapi.responses import HTMLResponse  # 新增：回傳 HTML 網頁
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

app = FastAPI()

# ==========================================
# [新增] 資料庫設定 (依照白板 Page 3)
# ⚠️ 請將 <password> 換成你的真正密碼
# ==========================================
MONGODB_URI = "mongodb+srv://yinchi:yinchi1234@cluster0.1tlpsco.mongodb.net/?appName=Cluster0"
DB_NAME = "emogo_db"

# --- 掛載資料夾，讓影片可以透過網址被下載 ---
# 這樣做之後，存放在 data/ 的檔案就可以透過 /files/檔名 來存取
os.makedirs("data", exist_ok=True) # 確保資料夾存在
app.mount("/files", StaticFiles(directory="data"), name="files")

# [保留] 原本的 CORS 設定 (這部分完全沒變)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False, # 注意：老師原本範例是 False，若前端有問題可改 True
    allow_methods=["*"],
    allow_headers=["*"],
)

# [新增] 啟動時連線資料庫 (白板要求的標準寫法)
@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    app.mongodb = app.mongodb_client[DB_NAME]
    print("MongoDB Connected")

# [新增] 關閉時斷開連線
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()
    print("MongoDB Disconnected")

# [保留] 根目錄測試 (稍微修改回傳內容以確認部署成功)
@app.get("/")
def index():
    return {"message": "EmoGo Backend is running!"}

# --- 1. Vlog 功能 ---
@app.post("/upload-vlog/")
async def upload_vlog(file: UploadFile = File(...)):
    file_path = os.path.join("data", file.filename)
    # 存檔
    async with aiofiles.open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk: break
            await buffer.write(chunk)

    # 產生下載連結 URL
    # 注意：在 Render 上，我們用相對路徑 /files/檔名 即可
    download_url = f"/files/{file.filename}"

    vlog_data = {
        "filename": file.filename,
        "path": file_path,
        "download_url": download_url, # 存入下載連結方便查詢
        "type": "vlog"
    }
    await app.mongodb["vlogs"].insert_one(vlog_data)
    return {"status": "Vlog saved", "download_url": download_url}

# --- 2. Sentiment 功能 ---
# 定義情緒資料的格式
class SentimentModel(BaseModel):
    timestamp: str
    emotion: str     # 例如: "Happy", "Sad"
    score: float     # 例如: 0.95

@app.post("/upload-sentiment/")
async def upload_sentiment(data: SentimentModel):
    # 將資料轉成字典並寫入 'sentiments' collection
    await app.mongodb["sentiments"].insert_one(data.dict())
    return {"status": "Sentiment saved", "data": data}

# --- 3. GPS 功能 (新增) ---
# 定義 GPS 資料的格式
class GPSModel(BaseModel):
    timestamp: str
    latitude: float
    longitude: float

@app.post("/upload-gps/")
async def upload_gps(data: GPSModel):
    # 將資料轉成字典並寫入 'gps' collection
    await app.mongodb["gps"].insert_one(data.dict())
    return {"status": "GPS saved", "data": data}

# --- 4. 匯出功能 (回傳 HTML 網頁) ---
@app.get("/export-data", response_class=HTMLResponse)
async def export_data():
    # 撈取資料
    vlogs = await app.mongodb["vlogs"].find().to_list(100)
    sentiments = await app.mongodb["sentiments"].find().to_list(100)
    gps = await app.mongodb["gps"].find().to_list(100)

    # 產生 Vlog 表格列 (包含下載連結)
    vlog_rows = ""
    for v in vlogs:
        # 如果舊資料沒有 download_url，就動態產生一個
        url = v.get("download_url", f"/files/{v.get('filename', '')}")
        vlog_rows += f"""
        <tr>
            <td>{v.get('filename', 'N/A')}</td>
            <td><a href="{url}" download>Download Video</a></td>
            <td>{str(v.get('_id'))}</td>
        </tr>
        """

    # 產生 Sentiment 表格列
    sentiment_rows = ""
    for s in sentiments:
        sentiment_rows += f"<tr><td>{s.get('timestamp')}</td><td>{s.get('emotion')}</td><td>{s.get('score')}</td></tr>"

    # 產生 GPS 表格列
    gps_rows = ""
    for g in gps:
        gps_rows += f"<tr><td>{g.get('timestamp')}</td><td>{g.get('latitude')}</td><td>{g.get('longitude')}</td></tr>"

    # 組裝完整的 HTML
    html_content = f"""
    <html>
        <head>
            <title>EmoGo Backend Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h2 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
                th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
                th {{ background-color: #f4f4f4; }}
                a {{ color: blue; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>EmoGo Data Dashboard</h1>
            <p>This page lists the collected data from the EmoGo App.</p>

            <h2>1. Vlogs (Click to Download)</h2>
            <table>
                <tr><th>Filename</th><th>Action</th><th>ID</th></tr>
                {vlog_rows}
            </table>

            <h2>2. Sentiments</h2>
            <table>
                <tr><th>Timestamp</th><th>Emotion</th><th>Score</th></tr>
                {sentiment_rows}
            </table>

            <h2>3. GPS Coordinates</h2>
            <table>
                <tr><th>Timestamp</th><th>Latitude</th><th>Longitude</th></tr>
                {gps_rows}
            </table>
        </body>
    </html>
    """
    return html_content