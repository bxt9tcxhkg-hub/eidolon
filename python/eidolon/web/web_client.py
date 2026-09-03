from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


CLIENT_DIR = Path(__file__).resolve().parent


def mount_client(app: FastAPI) -> None:
    if CLIENT_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(CLIENT_DIR)), name="static")

        @app.get("/")
        def root() -> FileResponse:
            return FileResponse(str(CLIENT_DIR / "index.html"))
