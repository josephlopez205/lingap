from fastapi import FastAPI

app = FastAPI(title="Lingap API")


@app.get("/health")
def health():
    return {"status": "ok"}
