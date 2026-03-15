from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "DocThread API is ready to receive requests."
    }

@app.get("/api/test")
def test_endpoint():
    return {"data": "This is sample data from the Python backend!"}