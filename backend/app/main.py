"""FastAPI application entrypoint and routing registration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import dashboard_router, health_router, listings_router

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(
    title="Business Listings Dashboard API",
    description="Backend foundation for the Honeybee Digital business listings assignment.",
    version="0.1.0",
    docs_url="/docs",
)

frontend_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(listings_router)
app.include_router(dashboard_router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Business Listings Dashboard API",
        "docs": "/docs",
    }
