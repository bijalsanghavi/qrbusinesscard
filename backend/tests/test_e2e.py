import os
import shutil
from pathlib import Path

os.environ.setdefault("ENV", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_e2e.db")
os.environ.setdefault("UPLOAD_DIR", "test_media")
os.environ.setdefault("PUBLIC_HOST", "http://localhost:3001")

from fastapi.testclient import TestClient
from app.main import app


def setup_module(module):
    # Clean test artifacts
    db = Path("test_e2e.db")
    if db.exists():
        db.unlink()
    media = Path("test_media")
    if media.exists():
        shutil.rmtree(media)

    # Create database tables
    from app.db import Base, engine
    Base.metadata.create_all(bind=engine)


def test_end_to_end_flow():
    client = TestClient(app)

    # Health
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json().get("ok") is True

    # Dev login
    r = client.post("/dev/login")
    assert r.status_code == 200

    # Verify session
    r = client.get("/auth/me")
    assert r.status_code == 200
    assert r.json().get("authenticated") is True

    # Init upload
    r = client.post("/api/upload-photo", json={"filename": "t.jpg", "contentType": "image/jpeg"})
    assert r.status_code == 200
    init = r.json()
    upload_url = init.get("uploadUrl", "")
    method = init.get("method", "PUT")
    headers = init.get("headers", {})
    public_url = init.get("publicUrl")
    assert public_url

    # Upload bytes
    data = b"test-bytes"
    if upload_url.startswith("/"):
        r = client.post(upload_url, content=data, headers={"Content-Type": headers.get("Content-Type", "application/octet-stream")})
        assert r.status_code == 200
    else:
        # Presigned mode (not expected locally, but support it)
        import requests
        rr = requests.request(method, upload_url, data=data, headers=headers)
        assert rr.status_code in (200, 204)

    # Create profile
    # Ensure absolute photoUrl for vCard
    absolute_photo = public_url if public_url.startswith("http") else f"http://localhost:3001{public_url}"
    profile = {
        "fullName": "Test User",
        "firstName": "Test",
        "lastName": "User",
        "phones": [{"type": "cell", "number": "+15551234567"}],
        "emails": [{"type": "work", "address": "test@example.com"}],
        "url": "https://example.com",
        "social": {"linkedin": "https://linkedin.com/in/test"},
        "address": {"street": "1 Test", "city": "City", "country": "US"},
        "photoUrl": absolute_photo,
    }
    r = client.post("/api/profile", json=profile)
    assert r.status_code == 200
    slug = r.json().get("slug")
    assert slug

    # Fetch vCard
    r = client.get(f"/u/{slug}.vcf")
    assert r.status_code == 200
    body = r.text
    assert "BEGIN:VCARD" in body
    assert "PHOTO;VALUE=URI" in body

