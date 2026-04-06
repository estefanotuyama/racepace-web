from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.routers import sessions, events, drivers, laps, admin, pitwall_ai
from backend.db.database import create_db_and_tables

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="RacePace Backend",
              description="API For viewing F1 driver lap times, session results and more.")
app.include_router(events.router)
app.include_router(sessions.router)
app.include_router(drivers.router)
app.include_router(laps.router)
app.include_router(admin.router)
app.include_router(pitwall_ai.router)

origins = [
    "https://f1racepace.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables(populating=False)

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Connection successful"}

@app.get("/favicon.ico")
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")  # ✅ correct
