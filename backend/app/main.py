from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os

from .routes.vcf import router as vcf_router
from .routes.profiles import router as profiles_router
from .routes.billing import router as billing_router
from .routes.files import router as files_router
from .routes.auth import router as auth_router
from .db import Base, engine
from fastapi.staticfiles import StaticFiles
from .config import (
    ENABLE_CREATE_ALL,
    ENABLE_DEV_ROUTES,
    ENABLE_LOCAL_MEDIA,
    FRONTEND_ORIGIN,
    SESSION_SECRET,
    IS_PROD,
)

app = FastAPI(title="QR Business Card API", version="0.1.0")

# Allow multiple frontend origins for development and production
allowed_origins = [FRONTEND_ORIGIN]

# Add localhost variants for development
if "localhost" in FRONTEND_ORIGIN:
    allowed_origins.append(FRONTEND_ORIGIN.replace("localhost", "127.0.0.1"))
else:
    # Production - also allow localhost for testing
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cookie sessions for auth
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=False)

@app.get("/healthz")
def healthz():
    return {"ok": True}

# Table creation on startup
@app.on_event("startup")
def on_startup():
    if ENABLE_CREATE_ALL:
        Base.metadata.create_all(bind=engine)
    # One-time table creation for production if tables don't exist
    elif IS_PROD:
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            if not inspector.get_table_names():
                Base.metadata.create_all(bind=engine)
        except Exception:
            pass  # Tables might already exist

app.include_router(vcf_router)
app.include_router(profiles_router, prefix="/api")
app.include_router(files_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(auth_router, prefix="/auth")
if ENABLE_DEV_ROUTES:
    from .routes.dev import router as dev_router
    app.include_router(dev_router, prefix="/dev")

# Serve local media at /media (for local hosting option)
if ENABLE_LOCAL_MEDIA:
    media_dir = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "media"))
    # Ensure directory exists before mounting (StaticFiles checks at import time)
    os.makedirs(media_dir, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_dir), name="media")
