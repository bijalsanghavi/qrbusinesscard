# Backend (FastAPI)

## Run locally
- Create env: `cp .env.example .env`
- With Docker: `docker compose up --build`
- Without Docker: `pip install -r requirements.txt && uvicorn app.main:app --reload`

## Database (Local)
- Requires Docker Desktop running; Postgres container is started via `docker compose`.
- Tables are created automatically on startup via SQLAlchemy `create_all` (development only).
- For schema changes during early dev, prefer resetting the local DB:
  - `docker compose down -v` (drops the volume) then `docker compose up --build`
  - Or run manual `ALTER TABLE` statements if you want to preserve data.
  - Add proper migrations later when the schema stabilizes.

## Endpoints (stubs)
- `GET /u/{slug}.vcf` – serve a vCard; demo slug: `demo123`
- `POST /api/profile` – create a profile; returns `{ id, slug, ... }`
- `GET /api/profile/{id}` – fetch a profile
- `POST /api/upload-photo` – stub presigned upload
- `POST /api/stripe/checkout` – stub checkout
- `POST /api/stripe/webhook` – stub webhook

Replace the in-memory store with Postgres models and wire Google OAuth, Stripe, and S3/R2 per the PRD.

## Monetization gating
- vCard downloads (`GET /u/{slug}.vcf`) require an active subscription or a valid trial on the owning user.
- Trial is set on first login based on `TRIAL_DAYS` (default 7).

## Dev helpers
- `POST /dev/login` (development only): creates/logs in a dev user (email `dev@example.com`).
- `POST /dev/seed-profile` (development only): creates a sample profile with slug `devcard` for the current dev user.

## ENV Paths
- Set `ENV=development` for local dev: auto-creates tables, enables `/dev/*` routes, serves `/media`.
- Set `ENV=prod` for production: no dev routes; tables are not auto-created; keep `/media` if using local hosting.

## Image Uploads (Local Mode)
- The backend supports local image hosting without Cloudflare/S3.
- Upload flow: `POST /api/upload-photo` returns a direct upload endpoint; the frontend sends the image bytes to `/api/upload-photo-direct`.
- Files are stored under `UPLOAD_DIR` (default `media/`) and served at `GET /media/...`.
- Limits: images only; default max size 2MB (override via `MAX_UPLOAD_BYTES`).

To enable external storage later (Cloudflare R2/AWS S3), set `S3_*` envs and the upload API will switch to presigned PUT mode automatically.
