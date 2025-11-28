# QR Business Card Backend — Agent Guide

This repo hosts the backend for a QR-code digital business card app. The frontend is intentionally removed; consumers call the backend via the documented APIs.

## Goals
- Provide stable, minimal APIs to create business card profiles, upload a photo, and serve a vCard (`.vcf`) for QR scanning.
- Keep local dev fast and deterministic.
- Avoid hidden coupling to UI; treat the backend as a clean service boundary.

## Layout
- `backend/` FastAPI app and services
- `scripts/` Local run/stop/clean/test helpers
- `docs/` Guides (API)

## Local Development
- Prereqs: Docker Desktop, Node optional (frontend removed), Python 3.11+
- Start:
  - `./scripts/stop.sh && ./run.sh`
  - Optional self-test: `RUN_TEST=1 ./run.sh`
- Env (backend/.env):
  - `ENV=development`
  - `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5555/qrcard`
  - `PUBLIC_HOST=http://localhost:3001`
  - `FRONTEND_ORIGIN=http://localhost:3002` (for CORS; keep as-is)
  - Google OAuth: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_SECRET_KEY`

## Key Endpoints (see docs/API.md for full contract)
- Auth/session: `/auth/me`, `/auth/login`, `/auth/logout`, `/auth/config`
- Dev helpers (dev only): `/dev/login`, `/dev/seed-profile`
- Uploads: `/api/upload-photo`, `/api/upload-photo-direct`
- Profiles: `POST /api/profile`, `GET /api/profile/{id}`
- vCard: `GET /u/{slug}.vcf`

## Testing
- End-to-end smoke test: `scripts/test_local.sh`
  - Validates health, session, upload, profile create, and vCard fetch.
- Unit tests live under `backend/tests` (pytest). Add more as needed.

## Non-Goals
- No rendering/UI; this repo is solely the backend and tooling to run it.
- No analytics or Stripe integration (placeholders in code, but not wired).

