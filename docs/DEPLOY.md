# Deploy Guide

This backend deploys cleanly to Railway or AWS. Choose the path that matches your comfort and speed.

## Recommended: Railway (fastest)

**See [RAILWAY_SETUP.md](./RAILWAY_SETUP.md) for complete step-by-step instructions.**

Quick summary:
1. Create Railway project, add Postgres database
2. Set environment variables (ENV, DATABASE_URL, PUBLIC_HOST, GOOGLE_CLIENT_ID/SECRET, OAUTH_SECRET_KEY)
3. Deploy (auto via GitHub Actions or manual via Railway CLI)
4. Initialize database: `railway run python -m app.cli create-db`
5. Configure Google OAuth redirect URI
6. (Optional) Set up S3/R2 for persistent image storage

The repo includes GitHub Actions workflow for automatic deployment on push to `main`.

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

### Railway deploy (auto on push)
This repo includes `.github/workflows/railway-deploy.yml` which:
- Runs backend tests, then
- Deploys to Railway automatically on pushes to `main` (paths: backend/, docs/, scripts/, workflows).

Configure repo secrets in GitHub → Settings → Secrets and variables → Actions:
- `RAILWAY_TOKEN` – Railway account token
- `RAILWAY_PROJECT_ID` – Your project ID (e.g., `5053b920-4513-465d-aa9f-a92723317975`)
- `RAILWAY_SERVICE_ID` – The backend service ID (from Railway UI)
- `RAILWAY_ENV_ID` – The environment ID (e.g., production)

Once secrets are set, every push to `main` triggers tests and deploy.

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
