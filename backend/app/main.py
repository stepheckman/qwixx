from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.game import router as game_router

app = FastAPI(title="Qwixx API")

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:7003", "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game_router, prefix="/game")

@app.get("/")
def root():
    return {"message": "Welcome to Qwixx API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
