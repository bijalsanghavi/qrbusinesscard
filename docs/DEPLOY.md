# Deploy Guide

This backend deploys cleanly to Railway or AWS. Choose the path that matches your comfort and speed.

## Recommended: Railway (fastest)

What you get
- Simple PaaS, builds from your repo (Dockerfile).
- Managed Postgres add-on.
- Free tier suitable for MVPs.

Caveat: Local file uploads
- Railway file system is ephemeral unless you enable Volumes. For reliability, use object storage (AWS S3) by setting `S3_*` env vars — the backend will switch to presigned uploads automatically.

Steps
1) Create a Railway project; connect your GitHub repo.
2) Add a Postgres plugin; copy its connection string to `DATABASE_URL` env.
3) Add Environment Variables in Railway:
   - `ENV=prod`
   - `DATABASE_URL=postgresql+psycopg://...` (from plugin)
   - `PUBLIC_HOST=https://<your-railway-domain>`
   - `FRONTEND_ORIGIN=https://<your-ui-domain>`
   - `OAUTH_SECRET_KEY=<random>`
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
   - Optional S3:
     - `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`
     - `IMAGE_PUBLIC_BASE=https://<your-public-image-host>`
4) First-time DB init (one-off):
   - Railway → Shell → `python -m app.cli create-db`
5) Deploy via GitHub integration (push to main) or Railway CLI/action.

GitHub Actions (optional)
- Add repo secrets:
  - `RAILWAY_TOKEN` (Railway account token)
  - `RAILWAY_PROJECT_ID`, `RAILWAY_SERVICE_ID`, `RAILWAY_ENV_ID` (from Railway UI)
- Trigger the workflow manually under Actions → “Deploy to Railway”.

## AWS (more control)

What you get
- Full control, better scaling; more setup.

Suggested stack
- ECS Fargate (service) + ECR (images)
- RDS Postgres
- S3 for images (set envs as above)
- Optional CloudFront in front of S3

High-level steps
1) Build & push image to ECR from GitHub Actions.
2) Create ECS service using that image; set env vars (`ENV=prod`, `DATABASE_URL`, OAuth secrets, S3…)
3) RDS Postgres for `DATABASE_URL`; open security group to ECS.
4) Run `python -m app.cli create-db` once (exec into task or init container).
5) Point your domain to an ALB in front of ECS (HTTPS).

## CI/CD

### Tests on push
Add a GitHub Actions workflow to run backend tests:

```
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r backend/requirements.txt
      - run: pytest -q backend/tests
```

### Railway deploy (optional)
Use Railway’s GitHub app (UI) or action `railwayapp/railway-action` with a project token; configure in repo secrets.

## Runtime env variables
- `ENV=prod` (production) or `development` (local)
- `DATABASE_URL` (Postgres)
- `PUBLIC_HOST` (e.g., `https://api.yourdomain.com`)
- `FRONTEND_ORIGIN` (CORS; e.g., `https://app.yourdomain.com`)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `OAUTH_SECRET_KEY`
- `UPLOAD_DIR` (used when not on S3; local-only)
- S3 (optional): `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `IMAGE_PUBLIC_BASE`

## Runbooks
- First boot (prod): run DB init `python -m app.cli create-db`
- Changing domains: update `PUBLIC_HOST` and `FRONTEND_ORIGIN`
- OAuth errors: check `/auth/config` for computed `redirect_uri` and match in Google Console
- Image issues: prefer S3 in production; local uploads require persistent volumes
