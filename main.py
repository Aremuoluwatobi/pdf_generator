from fastapi import FastAPI

app = FastAPI()


@app.post("/health")
def check_health():
    return {"status": "Hi Aremu"}
