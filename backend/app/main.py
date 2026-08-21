from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


app = FastAPI(
    title="Mirai Economic Intelligence API",
    description="Backend API for the Mirai Economic Intelligence Platform.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Mirai API is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Mirai Economic Intelligence API",
    }