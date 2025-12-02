import os, aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/",response_class=PlainTextResponse)
def index(greet: str = "", name: str = ""):
    return f"{greet} {name}"

@app.post("/upload-async/")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join("data", file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    async with aiofiles.open(file_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)  # async read
            if not chunk:
                break
            await buffer.write(chunk)            # async write

    return {
        "filename": file.filename,
        "saved_to": file_path,
    }

@app.post("/upload-sync/")
def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join("data/", file.filename)
    with open(file_path, "wb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)  # 1MB
            if not chunk:
                break
            buffer.write(chunk)

    return {
        "filename": file.filename,
        "saved_to": file_path,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
