# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

QR Business Card is a backend-only FastAPI service that generates QR codes linking to hosted vCards (`.vcf` files). When scanned, these QR codes open the native "Add Contact" dialog on mobile devices. The frontend is maintained in a **separate repository** and built with Google Gemini AI Studio.

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

**Repository Structure:**
- **Backend**: `github.com/bijalsanghavi/qrbusinesscard` (this repo)
- **Frontend**: `github.com/bijalsanghavi/QRCodeFrontEnd` (separate repo, built with Gemini)

---

## Current Deployment Status (As of 2025-11-29)

### Production
- **Backend**: Railway - https://qrbusinesscard-production-qrcode.up.railway.app
  - ✅ Manual deployment works (`railway up`)
  - ❌ GitHub Actions auto-deploy needs valid Railway token
  - Environment: `production-qrcode`
  - Service ID: `efd4178b-20e2-4387-a062-09079d8fa5a0`
  - Project ID: `5053b920-4513-465d-aa9f-a92723317975`

- **Frontend**: Not yet deployed
  - Planned: Netlify (see `docs/NETLIFY_SETUP.md`)
  - Current: Development on Google AI Studio (https://aistudio.google.com)

### Local Development
- ✅ Backend: `http://localhost:3001`
- ✅ Frontend: `http://localhost:3000` (Vite dev server)
- ✅ Full-stack script: `./scripts/dev-fullstack.sh`

---

## Commands

### Full-Stack Local Development (RECOMMENDED)
```bash
# Start both backend and frontend with one command
./scripts/dev-fullstack.sh

# This script will:
# 1. Start PostgreSQL (Docker)
# 2. Start backend on port 3001
# 3. Clone/setup frontend repo (if needed)
# 4. Start frontend on port 3000
# 5. Open browser automatically

# Logs are available at:
# - Backend: /tmp/qr-backend.log
# - Frontend: /tmp/qr-frontend.log
```

### Backend Only
```bash
# Start backend + Postgres via docker-compose
./scripts/stop.sh && ./run.sh

# Or use Makefile
make dev-up

# Backend health check
curl http://localhost:3001/healthz

# Dev login (bypasses OAuth for local testing)
curl -X POST http://localhost:3001/dev/login -c /tmp/cookies.txt

# Seed dev user and profile (creates slug=devcard)
make dev-seed
```

### Testing
```bash
# Run end-to-end test (uses SQLite + local media)
cd backend && pytest -q tests/test_e2e.py

# Run full local integration test (requires backend running)
./scripts/test_local.sh

# CI tests (GitHub Actions)
# Automatically run on push to main via .github/workflows/ci.yml
```

### Production Deployment

**Railway (Backend):**
```bash
# Manual deploy (WORKS)
railway up --detach

# View logs
railway logs

# Check status
railway status
```

**GitHub Actions (NEEDS FIX):**
```bash
# GitHub Actions auto-deploy is configured but needs valid RAILWAY_TOKEN
# Workflow: .github/workflows/railway-deploy.yml
# Required secrets:
#   - RAILWAY_TOKEN (currently invalid - needs to be updated)
#   - RAILWAY_SERVICE_ID (set correctly)

# To fix: Get valid token from https://railway.app/account/tokens
# Then update: gh secret set RAILWAY_TOKEN
```

---

## Architecture

### Two-Repository Setup

**Backend (this repo):**
- Python/FastAPI application
- Deployed to Railway
- Provides REST API for frontend

**Frontend (separate repo):**
- React/Vite application
- Built with Google Gemini AI Studio
- Will deploy to Netlify
- Consumes backend API

**API Documentation for Frontend:**
- **For Gemini**: `docs/API_FOR_GEMINI.md` - JavaScript examples
- **Complete**: `docs/API_REFERENCE.md` - Full API specs

### Request Flow
1. **vCard Serving**: `GET /u/{slug}.vcf` → `routes/vcf.py` → `services/vcard.py` → returns vCard text
2. **Profile CRUD**: `/api/profile` routes → `routes/profiles.py` → SQLAlchemy `Profile` model
3. **Auth**: `/auth/login` → Google OAuth via Authlib → session cookie → `/auth/me` to check status
4. **Uploads**: `/api/upload-photo` → returns absolute URL → `/api/upload-photo-direct` or S3 presigned URL

### Database Models
- **Profile** (`models.py`): Core business card data
  - Fields: slug, full_name, phones (JSON), emails (JSON), social (JSON), address (JSON), photo_url
  - Unique constraint on slug
  - Foreign key: user_id (nullable)
- **User** (`models_user.py`): OAuth user (google_id, trial_ends_at, sub_active, sub_ends_at)

### Image Storage Strategy
**Two modes** configured at runtime:

**Local mode** (default for dev):
- Upload to `UPLOAD_DIR` (default `media/`)
- Served at `GET /media/{key}`
- Returns absolute URLs like `http://localhost:3001/media/profiles/...`
- Logic: `storage.py:save_local_bytes()`, `storage.py:build_public_url()`

**S3/R2 mode** (for production):
- When `S3_BUCKET` is set, returns presigned PUT URL
- Client uploads directly to S3/R2
- Public URL from `IMAGE_PUBLIC_BASE` env var
- Logic: `storage.py:create_presigned_put()`

### CORS Configuration
Located in `backend/app/main.py`:
```python
# Production frontend (Netlify - not yet deployed)
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")  # Set in Railway env vars

# Local development
allowed_origins.extend([
    "http://localhost:3000",  # Local frontend (Vite)
    "http://localhost:3001",  # Backend
    "http://localhost:5173",  # Vite alternative port
])

# Google AI Studio (for Gemini-built frontend testing)
allowed_origins.append("https://aistudio.google.com")
```

**IMPORTANT**: Update `FRONTEND_ORIGIN` in Railway after deploying frontend to Netlify.

---

## Recent Fixes & Improvements (2025-11-29)

### 1. Pydantic URL Validation Fix
**Issue**: Frontend sending empty strings for optional URL fields caused validation errors.
**Fix**: Added `field_validator` to convert empty strings to `None` before Pydantic validation.
**Files**: `backend/app/schemas.py`
```python
@field_validator('url', 'photoUrl', 'linkedin', 'instagram', 'twitter', 'facebook', mode='before')
@classmethod
def empty_str_to_none(cls, v):
    if v == '' or v is None:
        return None
    return v
```

### 2. Photo URL Returns Absolute URLs
**Issue**: Photo upload returned relative URLs (`/media/...`) but validation requires absolute URLs.
**Fix**: Updated `build_public_url()` to include `PUBLIC_HOST` for local mode.
**Files**: `backend/app/storage.py`
```python
def build_public_url(key: str) -> str:
    base = os.getenv("IMAGE_PUBLIC_BASE")
    if base:
        return f"{base.rstrip('/')}/{key}"
    # Return absolute URL for local mode
    public_host = os.getenv("PUBLIC_HOST", "http://localhost:3001")
    return f"{public_host.rstrip('/')}/media/{key}"
```

### 3. FRONTEND_ORIGIN Configuration
**Issue**: OAuth redirects were going to wrong port (3002 instead of 3000).
**Fix**:
- Updated `backend/.env` to set `FRONTEND_ORIGIN=http://localhost:3000`
- Added override in `config.py` and `auth.py` to use config module
**Files**: `backend/app/config.py`, `backend/app/routes/auth.py`

### 4. Railway Deployment Configuration
**Issue**: Railway couldn't find Dockerfile because it was analyzing repo root instead of `backend/` directory.
**Fix**: Created `railway.toml` at repo root with build context.
**Files**: `railway.toml`
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile"
buildContext = "backend"
```

### 5. Full-Stack Development Script
**Created**: `scripts/dev-fullstack.sh` - One command to start backend + frontend
**Features**:
- Auto-starts PostgreSQL via Docker
- Starts backend on port 3001
- Clones frontend repo if needed
- Installs frontend dependencies
- Starts frontend on port 3000 (or 5173)
- Opens browser automatically
- Handles cleanup on exit

### 6. Frontend HTML Entry Point Fix
**Issue**: Frontend showed blank page.
**Fix**: Added missing script tag to `index.html`
**Frontend Repo**: `github.com/bijalsanghavi/QRCodeFrontEnd`
```html
<script type="module" src="/index.tsx"></script>
```

---

## Environment Variables

### Development (.env)
Located: `backend/.env` (not committed to git)

```bash
# Environment
ENV=development
PORT=3001

# Frontend (local dev)
FRONTEND_ORIGIN=http://localhost:3000

# Database (Docker PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5555/qrcard

# OAuth (Google) - Get from https://console.cloud.google.com
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-google-client-secret
OAUTH_SECRET_KEY=generate-with-openssl-rand-base64-32

# Storage (local mode)
PUBLIC_HOST=http://localhost:3001
UPLOAD_DIR=media
MAX_UPLOAD_BYTES=10000000  # 10MB
ENABLE_LOCAL_MEDIA=true

# Feature flags
ENABLE_CREATE_ALL=true  # Auto-create tables on startup
ENABLE_DEV_ROUTES=true  # Enable /dev/login and /dev/seed-profile

# Stripe (stubbed)
STRIPE_PRICE_ID=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
TRIAL_DAYS=7
```

### Production (Railway)
Set via Railway dashboard or CLI:

```bash
# Environment
ENV=production

# Frontend (UPDATE THIS after Netlify deploy!)
FRONTEND_ORIGIN=https://qrbusinesscard.trika.ai  # Or Netlify URL

# Database (auto-set by Railway)
DATABASE_URL=[Railway provides this]

# Public URLs
PUBLIC_HOST=https://qrbusinesscard-production-qrcode.up.railway.app

# OAuth (same as dev)
GOOGLE_CLIENT_ID=[same]
GOOGLE_CLIENT_SECRET=[same]
OAUTH_SECRET_KEY=[generate new random string for prod]

# Storage
UPLOAD_DIR=media
MAX_UPLOAD_BYTES=10000000
ENABLE_LOCAL_MEDIA=true  # Or configure S3/R2

# S3/R2 (optional, for persistent storage)
S3_ENDPOINT_URL=
S3_BUCKET=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
IMAGE_PUBLIC_BASE=

# Feature flags
ENABLE_CREATE_ALL=false  # Don't auto-create in prod
ENABLE_DEV_ROUTES=false  # Disable dev routes in prod
```

**Critical Production Updates Needed:**
1. **FRONTEND_ORIGIN**: Must be updated to Netlify URL after frontend deployment
2. **OAUTH_SECRET_KEY**: Should use a production-specific random value
3. **S3/R2 Config**: Recommended for persistent image storage (Railway filesystem is ephemeral)

---

## Outstanding Issues

### 1. GitHub Actions Railway Deployment ❌
**Status**: Manual deployment works, GitHub Actions fails with "Unauthorized"
**Cause**: Invalid or incorrectly formatted RAILWAY_TOKEN
**Next Steps**:
1. Go to https://railway.app/account/tokens
2. Create new token (click "Create New Token")
3. **Immediately copy the token value shown** (only shown once!)
4. Update GitHub secret: `gh secret set RAILWAY_TOKEN`
5. Test: Manually trigger workflow or push to `backend/` directory

**Workflow**: `.github/workflows/railway-deploy.yml`
**Secrets**: `RAILWAY_TOKEN` (needs update), `RAILWAY_SERVICE_ID` (correct)

### 2. Frontend Netlify Deployment ⏳
**Status**: Not started
**Guide**: `docs/NETLIFY_SETUP.md`
**Next Steps**:
1. Deploy frontend to Netlify
2. Update `FRONTEND_ORIGIN` in Railway
3. Redeploy backend to pick up new CORS config
4. Test OAuth flow end-to-end

### 3. Google OAuth Redirect URI
**Status**: Configured for Railway production, needs localhost for local dev
**Current URIs** (in Google Cloud Console):
- `https://qrbusinesscard-production-qrcode.up.railway.app/auth/callback` ✅
- `http://localhost:3001/auth/callback` ❌ (needs to be added)

**To Add**:
1. Go to https://console.cloud.google.com/apis/credentials
2. Edit OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:3001/auth/callback`
   - `http://127.0.0.1:3001/auth/callback`

**Workaround for Local Dev**:
Use `/dev/login` endpoint which bypasses OAuth.

---

## Development Workflow

### Local Development Iterations
```bash
# 1. Start full stack
./scripts/dev-fullstack.sh

# 2. Dev login (bypasses OAuth)
# In browser console at http://localhost:3000:
fetch('http://localhost:3001/dev/login', {method: 'POST', credentials: 'include'})
  .then(r => r.json()).then(d => console.log('Logged in:', d))

# 3. Make changes to backend
# Backend auto-reloads (uvicorn --reload)

# 4. Make changes to frontend
# Frontend auto-reloads (Vite HMR)

# 5. Test, commit, push
git add . && git commit -m "..." && git push

# 6. Deploy to Railway manually (until GitHub Actions is fixed)
railway up --detach
```

### Adding a New Profile Field
1. Add column to `backend/app/models.py:Profile`
2. Update `backend/app/schemas.py:ProfileIn` and `ProfileOut`
3. Update `backend/app/services/vcard.py:build_vcard()` if needed
4. Restart backend to create new column
5. Update frontend to include new field (in frontend repo)

### OAuth Setup (Local Development)
**Option 1: Use Dev Login** (Recommended for local dev)
```bash
curl -X POST http://localhost:3001/dev/login -c /tmp/cookies.txt
# OR from browser console:
fetch('http://localhost:3001/dev/login', {method: 'POST', credentials: 'include'})
```

**Option 2: Add localhost to Google OAuth**
1. Google Cloud Console: https://console.cloud.google.com/apis/credentials
2. Edit your OAuth 2.0 Client ID
3. Add redirect URI: `http://localhost:3001/auth/callback`

### Testing Strategy
- **E2E**: `backend/tests/test_e2e.py` (uses TestClient + SQLite)
- **Integration**: `scripts/test_local.sh` (tests against running backend)
- **CI**: GitHub Actions runs tests on every push (`.github/workflows/ci.yml`)

---

## Common Gotchas

### CORS Issues
- **Frontend must send `credentials: 'include'`** in all fetch requests
- Backend `FRONTEND_ORIGIN` must exactly match frontend URL
- Google AI Studio origin (`https://aistudio.google.com`) is already allowed
- Local ports 3000, 3001, 5173 are allowed

### Photo Upload Issues
- **File size limit**: 10MB (set via `MAX_UPLOAD_BYTES`)
- **Photo URLs must be absolute**: `http://localhost:3001/media/...` not `/media/...`
- **Authentication required**: User must be logged in (session cookie)

### OAuth Redirect Issues
- **FRONTEND_ORIGIN** in backend must match where user is redirected after login
- Local dev: `http://localhost:3000`
- Production: Set to Netlify URL after deployment
- **Redirect URI in Google Console** must match `${PUBLIC_HOST}/auth/callback`

### Empty URL Field Validation
- Frontend can send empty strings for optional URLs
- Backend converts empty strings to `None` via Pydantic validators
- Fields affected: `url`, `photoUrl`, `linkedin`, `instagram`, `twitter`, `facebook`

### Railway Deployment
- **Build context**: Uses `backend/` as root (configured in `railway.toml`)
- **Environment variables**: Set via Railway dashboard or `railway variables`
- **Logs**: `railway logs` or view in Railway dashboard
- **Manual deploy**: `railway up --detach` (works reliably)
- **GitHub Actions**: Currently broken (token issue), use manual deploy

---

## Documentation

### For Users
- **`README.md`**: Project overview and quick start
- **`docs/SETUP.md`**: Complete local + production setup guide
- **`docs/RAILWAY_SETUP.md`**: Railway deployment guide
- **`docs/NETLIFY_SETUP.md`**: Netlify deployment guide (for frontend)

### For Frontend Developers (Gemini)
- **`docs/API_FOR_GEMINI.md`**: JavaScript/fetch examples
- **`docs/API_REFERENCE.md`**: Complete API specification

### For Future Claude Instances
- **`CLAUDE.md`**: This file - comprehensive development guide
- **`docs/DEPLOY.md`**: General deployment notes

---

## Quick Reference

### URLs
- **Local Frontend**: http://localhost:3000
- **Local Backend**: http://localhost:3001
- **Local API Docs**: http://localhost:3001/docs
- **Prod Backend**: https://qrbusinesscard-production-qrcode.up.railway.app
- **Prod Frontend**: (not yet deployed)

### Repositories
- **Backend**: https://github.com/bijalsanghavi/qrbusinesscard
- **Frontend**: https://github.com/bijalsanghavi/QRCodeFrontEnd

### Railway
- **Project ID**: `5053b920-4513-465d-aa9f-a92723317975`
- **Service ID**: `efd4178b-20e2-4387-a062-09079d8fa5a0`
- **Environment**: `production-qrcode`
- **Dashboard**: https://railway.com/project/5053b920-4513-465d-aa9f-a92723317975

### Common Commands
```bash
# Full-stack dev
./scripts/dev-fullstack.sh

# Backend only
./run.sh

# Deploy to Railway
railway up --detach

# Dev login
curl -X POST http://localhost:3001/dev/login -c /tmp/cookies.txt

# Tests
cd backend && pytest -q tests

# GitHub Actions
gh run list --workflow "Deploy to Railway"
gh secret list
```

---

## Next Steps for Deployment

1. **Fix GitHub Actions Railway Token**
   - Create new token at https://railway.app/account/tokens
   - Update: `gh secret set RAILWAY_TOKEN`

2. **Deploy Frontend to Netlify**
   - Follow `docs/NETLIFY_SETUP.md`
   - Update `FRONTEND_ORIGIN` in Railway after deployment

3. **Add localhost to Google OAuth** (for local dev)
   - Add `http://localhost:3001/auth/callback` to authorized redirect URIs

4. **Configure S3/R2 for Production Images** (optional but recommended)
   - Railway filesystem is ephemeral
   - Set S3 env vars in Railway dashboard

5. **Test Full Production Flow**
   - OAuth login
   - Photo upload
   - Business card creation
   - QR code scanning on mobile device
