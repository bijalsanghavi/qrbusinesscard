# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QR Business Card is a backend-only FastAPI service that generates QR codes linking to hosted vCards (`.vcf` files). When scanned, these QR codes open the native "Add Contact" dialog on mobile devices. The frontend was intentionally removed; external UIs should be built against the documented APIs.

**Core Functionality:**
- vCard generation at `/u/{slug}.vcf`
- Profile management (CRUD) at `/api/profile/*`
- Google OAuth authentication at `/auth/*`
- Image uploads (local or S3/R2) at `/api/upload-photo`
- Subscription gating via trial_ends_at and sub_active fields

**Tech Stack:**
- FastAPI + Uvicorn
- SQLAlchemy with PostgreSQL (psycopg3)
- Authlib for Google OAuth
- Boto3 for S3/R2 uploads
- Stripe for billing (stubbed)

## Commands

### Local Development
```bash
# Start backend + Postgres via docker-compose
./scripts/stop.sh && ./run.sh

# Or use Makefile
make dev-up

# Backend health check
curl http://localhost:3001/healthz

# Reset DB and start fresh
make dev-reset-db

# Seed dev user and profile (creates slug=devcard)
make dev-seed
```

### Testing
```bash
# Run end-to-end test (uses SQLite + local media)
cd backend && pytest -q tests/test_e2e.py

# Run full local integration test (requires backend running)
./scripts/test_local.sh

# The test flow: health → dev login → upload photo → create profile → fetch vCard
```

### Production Deployment
```bash
# Build and run via docker-compose.prod.yml
make prod-build && make prod-up

# First-time DB initialization (run once)
python -m app.cli create-db

# View logs
make prod-logs
```

### Database Management
```bash
# Initialize database tables (production first-boot)
python -m app.cli create-db

# Note: Uses SQLAlchemy's create_all; no Alembic migrations yet
```

## Architecture

### Request Flow
1. **vCard Serving**: `GET /u/{slug}.vcf` → `routes/vcf.py` → `services/vcard.py` → returns vCard text
2. **Profile CRUD**: `/api/profile` routes → `routes/profiles.py` → SQLAlchemy `Profile` model
3. **Auth**: `/auth/login` → Google OAuth via Authlib → session cookie → `/auth/me` to check status
4. **Uploads**: `/api/upload-photo` → either presigned S3 URL or local `/media` route

### Database Models
- **Profile** (`models.py`): Core business card data (slug, full_name, phones, emails, social, address, photo_url)
  - JSON columns: phones, emails, address, social
  - Unique constraint on slug
  - Foreign key: user_id (nullable)
- **User** (`models_user.py`): OAuth user (google_id, trial_ends_at, sub_active, sub_ends_at)

### Image Storage Strategy
The backend supports **two modes** configured at runtime:
- **Local mode** (default): Upload to `UPLOAD_DIR` (default `media/`), served at `GET /media/{key}`
  - Logic in `storage.py:save_local_bytes()`, mounted in `main.py` via `StaticFiles`
- **S3/R2 mode**: When `S3_BUCKET` is set, returns presigned PUT URL for client-side upload
  - Logic in `storage.py:create_presigned_put()`
  - Public URL uses `IMAGE_PUBLIC_BASE` env var

**Key function:** `routes/files.py:init_upload()` decides which mode based on `os.getenv("S3_BUCKET")`

### Environment Configuration
- **`ENV`**: `development` enables dev routes (`/dev/login`, `/dev/seed-profile`) and auto table creation
- **`ENABLE_CREATE_ALL`**: Auto-creates tables on startup (development only; use `python -m app.cli create-db` in prod)
- **`ENABLE_LOCAL_MEDIA`**: Mounts `/media` static file serving (both dev and prod by default)

### vCard Generation
- **Service**: `services/vcard.py:build_vcard()` constructs vCard 3.0 format
- **Social links**: Adds both `URL:` and `X-SOCIALPROFILE:` entries for Apple Contacts compatibility
- **Photo**: Uses `PHOTO;VALUE=URI:` with absolute URL
- **Escaping**: vCard-specific escaping for `;`, `,`, `\`, `\n` via `_escape()`

### Subscription/Monetization
- vCard endpoint (`routes/vcf.py:get_vcard()`) checks `_user_has_access()`
- Returns HTTP 402 if user has no active subscription and trial expired
- **Trial**: 7 days default (`TRIAL_DAYS` env var), set on first Google login
- **Subscription**: Managed via Stripe (stubbed in `routes/billing.py`)

## Development Workflow

### Adding a New Profile Field
1. Add column to `models.py:Profile` (e.g., `nickname = Column(String(128))`)
2. Update `schemas.py:ProfileCreate` and `ProfileOut` Pydantic models
3. Modify `services/vcard.py:build_vcard()` to include field in vCard output
4. Run DB migration (currently manual; use `python -m app.cli create-db` to recreate in dev)

### OAuth Setup
1. Create Google OAuth app at [console.cloud.google.com](https://console.cloud.google.com)
2. Set authorized redirect URI: `http://localhost:3001/auth/callback` (dev) or `https://{PUBLIC_HOST}/auth/callback` (prod)
3. Copy `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `backend/.env`
4. Verify config: `curl http://localhost:3001/auth/config` should show correct `redirect_uri`

### Testing Strategy
- **Unit**: None currently; add to `backend/tests/`
- **E2E**: `tests/test_e2e.py` uses `TestClient` with SQLite
- **Integration**: `scripts/test_local.sh` tests full stack with curl

## Railway Deployment Notes
**See [docs/RAILWAY_SETUP.md](docs/RAILWAY_SETUP.md) for complete deployment guide.**

Key points:
- GitHub Actions auto-deploys on push to `main` (`.github/workflows/railway-deploy.yml`)
- Required GitHub secrets: `RAILWAY_TOKEN`, `RAILWAY_SERVICE_ID`
- **First deploy**: Run `railway run python -m app.cli create-db` to initialize DB
- **Configuration**: `backend/railway.json` specifies Dockerfile build
- **Storage**: Railway filesystem is ephemeral; configure S3/R2 for persistent images

## Common Gotchas
- **CORS**: Frontend origin must match `FRONTEND_ORIGIN` env var exactly (including http vs https)
- **Photo URLs**: vCard PHOTO field requires absolute URL; relative paths won't work in native contacts apps
- **Session cookies**: OAuth uses `SessionMiddleware` with `same_site="lax"`; ensure frontend sends credentials
- **Port mismatch**: `docker-compose.yml` maps port 8000, but `run.sh` uses port 3001 (non-Docker)
- **Database URL**: Docker uses `@db:5432`, local uses `@localhost:5555`
