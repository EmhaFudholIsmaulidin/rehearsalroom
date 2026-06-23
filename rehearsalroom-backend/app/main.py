import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.bootstrap import init_db, seed_if_empty
from app.routers import (
    auth, bands, members, invitations,
    songs, sessions, session_songs,
    progress, feedback, dashboard,
)

app = FastAPI(
    title="RehearsalRoom API",
    description="Backend REST API untuk manajemen latihan band indie/rintisan.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup():
    # Buat tabel otomatis (SQLite) + isi data dummy bila kosong
    init_db()
    try:
        if seed_if_empty():
            print("Data dummy 'The Catalyst' berhasil dibuat.")
    except Exception as e:
        print(f"Auto-seed dilewati: {e}")


# CORS (untuk mode dev terpisah; tidak diperlukan saat served statis)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(bands.router, prefix=API_PREFIX)
app.include_router(members.router, prefix=API_PREFIX)
app.include_router(invitations.router, prefix=API_PREFIX)
app.include_router(songs.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(session_songs.router, prefix=API_PREFIX)
app.include_router(progress.router, prefix=API_PREFIX)
app.include_router(feedback.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "ok"}


# Sajikan frontend React hasil build (folder app/static) sehingga seluruh
# aplikasi jalan di http://localhost:8000 tanpa perlu Node.js.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "app": "RehearsalRoom API",
            "docs": "/docs",
            "note": "Frontend belum di-build.",
        }
