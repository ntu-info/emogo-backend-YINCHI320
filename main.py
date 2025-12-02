import os
import aiofiles
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient # 新增：資料庫驅動

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

# [修改] 上傳功能：基於原本的 /upload-async/ 修改
# 老師原本的邏輯是單純存檔，我們加入「寫入資料庫」的動作
@app.post("/upload-vlog/")
async def upload_video(file: UploadFile = File(...)):
    # 1. [保留] 原本的存檔邏輯
    file_path = os.path.join("data", file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiofiles.open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)  # async read
            if not chunk:
                break
            await buffer.write(chunk)            # async write

    # 2. [新增] 將紀錄寫入 MongoDB (作業核心要求)
    # 我們把檔名、路徑記錄下來
    vlog_data = {
        "filename": file.filename,
        "path": file_path,
        "type": "vlog"
    }
    await app.mongodb["vlogs"].insert_one(vlog_data)

    return {
        "filename": file.filename,
        "saved_to": file_path,
        "status": "Saved to MongoDB"
    }

# [新增] 資料匯出 API (作業 Required)
# 這是老師範例裡沒有，但作業說明要求一定要有的
@app.get("/export-data")
async def export_data():
    vlogs = await app.mongodb["vlogs"].find().to_list(100)
    # 轉換 ObjectId 為字串
    for doc in vlogs:
        doc["_id"] = str(doc["_id"])
    return {"vlogs": vlogs}