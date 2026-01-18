from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import game

app = FastAPI(title="Qwixx API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router, prefix="/api/game", tags=["game"])


@app.get("/")
async def root():
    return {"message": "Welcome to Qwixx API"}
