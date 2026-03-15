from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "DocThread Backend is Online and ready to build!"}