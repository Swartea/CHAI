"""CHAI API Server - FastAPI backend for CHAI Web UI."""

import sys
import asyncio
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.models import (
    NovelCreateRequest,
    WorldBuildRequest,
    ChapterWriteRequest,
    DeconstructRequest,
)
from server.routes import novel, world, chapter, deconstruct

app = FastAPI(
    title="CHAI API",
    description="CHAI - AI 小说自动化写作系统 API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(novel.router, prefix="/api/novel", tags=["novel"])
app.include_router(world.router, prefix="/api/world", tags=["world"])
app.include_router(chapter.router, prefix="/api/chapter", tags=["chapter"])
app.include_router(deconstruct.router, prefix="/api/deconstruct", tags=["deconstruct"])


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "CHAI API"}


@app.get("/api/status")
async def status():
    """Get CHAI system status."""
    # Check if novel data exists
    novels_dir = Path(__file__).parent.parent / "novels"
    projects = []
    if novels_dir.exists():
        projects = [d.name for d in novels_dir.iterdir() if d.is_dir()]

    return {
        "projects": projects,
        "chai_version": "0.1.0",
    }


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server."""
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
