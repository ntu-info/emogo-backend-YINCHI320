import os
import aiofiles
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel # 新增：用來定義資料格式

app = FastAPI()

# ==========================================
# [新增] 資料庫設定 (依照白板 Page 3)
# ⚠️ 請將 <password> 換成你的真正密碼
# ==========================================
MONGODB_URI = "mongodb+srv://yinchi:yinchi1234@cluster0.1tlpsco.mongodb.net/?appName=Cluster0"
DB_NAME = "emogo_db"


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

# --- 1. Vlog 功能 (原本的) ---
@app.post("/upload-vlog/")
async def upload_vlog(file: UploadFile = File(...)):
    file_path = os.path.join("data", file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiofiles.open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk: break
            await buffer.write(chunk)

    vlog_data = {
        "filename": file.filename,
        "path": file_path,
        "type": "vlog"
    }
    await app.mongodb["vlogs"].insert_one(vlog_data)
    return {"status": "Vlog saved"}

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

# --- 4. 匯出功能 (更新：讀取三種資料) ---
@app.get("/export-data")
async def export_data():
    # 分別撈取三種資料 (各取前 100 筆)
    vlogs = await app.mongodb["vlogs"].find().to_list(100)
    sentiments = await app.mongodb["sentiments"].find().to_list(100)
    gps = await app.mongodb["gps"].find().to_list(100)

    # 處理 ObjectId 轉字串
    for doc in vlogs: doc["_id"] = str(doc["_id"])
    for doc in sentiments: doc["_id"] = str(doc["_id"])
    for doc in gps: doc["_id"] = str(doc["_id"])

    return {
        "vlogs": vlogs,
        "sentiments": sentiments,
        "gps": gps
    }