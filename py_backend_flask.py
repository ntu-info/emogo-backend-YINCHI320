from flask import Flask, request

app = Flask(__name__)

@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

@app.get("/")
def index():
    greet = request.args.get("greet", "")
    name = request.args.get("name", "")
    return f"{greet} {name}"

if __name__ == "__main__":
    app.run(host="localhost", port=8000)

