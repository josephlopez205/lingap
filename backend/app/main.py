# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import lgu, barangay, gaps

app = FastAPI(title="LINGAP API")

# CORS — needed since frontend (Vite, port 5173) and backend (port 8000) differ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lgu.router)
app.include_router(barangay.router)
app.include_router(gaps.router)

@app.get("/health")
def health():
    return {"status": "ok"}
