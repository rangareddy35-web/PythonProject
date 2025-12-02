from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "API is live!"}

@app.post("/test")
def test(data: dict):
    return {"received": data}