[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/e7FBMwSa)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-2e0aaae1b6195c2367325f4f02e2d04e9abb55f0b24a779b69b11b9e10269abc.svg)](https://classroom.github.com/online_ide?assignment_repo_id=21909330&assignment_repo_type=AssignmentRepo)


## 1. Data Export URI 
Download/view all collected data (Vlogs, Sentiments, & GPS):

👉 **[View Export Data](https://emogo-backend-yinchi320.onrender.com/export-data)**

免費版伺服器似乎只要一段時間沒人連線，就會把硬碟重置，之前上傳到 data/ 資料夾的影片都會消失。所以即使網頁上還留著檔名，點下去卻找不到檔案、沒辦法成功下載影片。

要測試下載功能，要麻煩老師當下先上傳一次影片，再到這個網址測試下載功能。

## 2. API Documentation & Testing
Upload test data using the interactive Swagger UI here:

👉 **[API Docs / Swagger UI](https://emogo-backend-yinchi320.onrender.com/docs)**

## 3. Gemini

👉 **[Gemini](https://gemini.google.com/share/d1f1c762daff)**




---



# Deploy FastAPI on Render

Use this repo as a template to deploy a Python [FastAPI](https://fastapi.tiangolo.com) service on Render.

See https://render.com/docs/deploy-fastapi or follow the steps below:

## Manual Steps

1. You may use this repository directly or [create your own repository from this template](https://github.com/render-examples/fastapi/generate) if you'd like to customize the code.
2. Create a new Web Service on Render.
3. Specify the URL to your new repository or this repository.
4. Render will automatically detect that you are deploying a Python service and use `pip` to download the dependencies.
5. Specify the following as the Start Command.

    ```shell
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```

6. Click Create Web Service.

Or simply click:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/render-examples/fastapi)

## Thanks

Thanks to [Harish](https://harishgarg.com) for the [inspiration to create a FastAPI quickstart for Render](https://twitter.com/harishkgarg/status/1435084018677010434) and for some sample code!

