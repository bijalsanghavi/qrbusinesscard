# QR Business Card Monorepo

This repo contains a Python FastAPI backend for generating QR codes that open native Add Contact with a hosted vCard (`.vcf`). The frontend was intentionally removed — build UIs against the documented APIs.

## Structure
- `backend/` – FastAPI app (vCard endpoint, profile API, auth, uploads)
- `docker-compose.yml` – Local dev for backend + Postgres (frontend optional)

## Quick Start (Local)
1. Copy envs: `cp backend/.env.example backend/.env`.
2. Start backend + Postgres: `./scripts/stop.sh && ./run.sh`.
3. Backend health: `http://localhost:3001/healthz`.

Notes: Configure Google OAuth in `backend/.env` for `/auth/login` to work.

## Domain
- Hosted vCards will live under `https://qr.trika.ai/u/{slug}.vcf` in production.

## Next Steps
- Wire Stripe Checkout + webhooks, S3/R2 uploads.
- Add more tests under `backend/tests`.

## Image Hosting (Local Mode)
- By default, the backend serves uploaded images from `UPLOAD_DIR` (default `media/`) at `GET /media/...`.
- No Cloudflare/S3 required for MVP. Ensure the server has write access and persistent storage.
- Configure in `backend/.env`:
  - `UPLOAD_DIR=media`
  - `IMAGE_PUBLIC_BASE` (optional): set to your backend origin + `/media` for absolute URLs.
- Upload safety: images only; default max size 2MB (config `MAX_UPLOAD_BYTES`).

## TODOs
- Add Cloudflare R2 or AWS S3 for CDN-backed image hosting when needed.
- Add Stripe billing (7-day trial + subscription checks).
- Add Alembic migrations and production DB setup docs.
- Implement proper QR code preview and density guidance.
- Improve auth UI and protect additional routes.

## Simple CI/CD (single-server)

- Build and run on your server (SSH into it):
  - `git pull` your repo
  - `cp backend/.env.example backend/.env` and set `ENV=prod`, `DATABASE_URL`, etc.
  - `make prod-build && make prod-up`
  - Backend: `http://<server>:3001`

- Update deploy:
  - Pull latest code and run `make prod-build && make prod-up` again. Containers rebuild and restart with zero extra tooling.

- Optional GitHub Actions (later):
  - Add a basic workflow to SSH into the server and run the same `make` targets after pushing to `main`.
  - Or push images to a registry (GHCR/Docker Hub) and `docker compose pull && make prod-up` on the server.
