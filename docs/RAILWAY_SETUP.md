# Railway Deployment Setup

This guide provides step-by-step instructions for deploying the QR Business Card backend to Railway.

## Prerequisites

- Railway account ([railway.app](https://railway.app))
- GitHub repository connected to Railway
- Google OAuth credentials (from Google Cloud Console)

## Initial Setup (One-Time)

### 1. Create Railway Project

1. Go to [railway.app/new](https://railway.app/new)
2. Select "Deploy from GitHub repo"
3. Choose this repository
4. Railway will detect the backend Dockerfile automatically

### 2. Add PostgreSQL Database

1. In your Railway project, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically create a Postgres instance and set `DATABASE_URL` variable

### 3. Configure Environment Variables

In Railway project settings → Variables, add these required variables:

**Required:**
```bash
ENV=prod
PUBLIC_HOST=https://your-app.up.railway.app  # Get this from Railway after first deploy
FRONTEND_ORIGIN=https://your-frontend-domain.com
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_SECRET_KEY=your_random_secret_key_here  # Generate with: openssl rand -hex 32
```

**Optional (for S3/R2 image storage):**
```bash
S3_BUCKET=your-bucket-name
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=https://your-endpoint.com  # For Cloudflare R2
IMAGE_PUBLIC_BASE=https://your-cdn-domain.com
```

### 4. Initialize Database

After the first deployment, run this command once in Railway Shell (or using Railway CLI):

```bash
python -m app.cli create-db
```

**Using Railway Dashboard:**
1. Go to your service → "Deployments" → Select latest deployment
2. Click "View Logs" → "Shell"
3. Run: `python -m app.cli create-db`

**Using Railway CLI:**
```bash
railway login
railway link  # Select your project
cd backend && railway run python -m app.cli create-db
```

### 5. Update PUBLIC_HOST

After your first deploy, Railway assigns a domain like `your-app.up.railway.app`:

1. Copy the domain from Railway dashboard
2. Update `PUBLIC_HOST` variable to `https://your-app.up.railway.app`
3. Trigger a redeploy (or push a new commit)

### 6. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Navigate to "APIs & Services" → "Credentials"
3. Edit your OAuth 2.0 Client ID
4. Add to "Authorized redirect URIs": `https://your-app.up.railway.app/auth/callback`
5. Save

Verify your OAuth config:
```bash
curl https://your-app.up.railway.app/auth/config
```

## GitHub Actions Auto-Deploy (Recommended)

This repo includes a GitHub Actions workflow that automatically deploys on push to `main`.

### Setup GitHub Secrets

1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:

```
RAILWAY_TOKEN         # Get from Railway → Account Settings → Tokens
RAILWAY_SERVICE_ID    # Get from Railway → Service → Settings → Service ID
```

### How it Works

1. On every push to `main`, GitHub Actions:
   - Runs backend tests
   - If tests pass, deploys to Railway automatically

2. To manually trigger deployment:
   - Go to Actions tab → "Deploy to Railway" → "Run workflow"

## Manual Deployment (Alternative)

If you prefer manual deployment via Railway CLI:

### Install Railway CLI
```bash
npm install -g @railway/cli
```

### Deploy
```bash
railway login
railway link  # Select your project and service
cd backend
railway up
```

## Railway Configuration

The `backend/railway.json` file configures:
- Dockerfile-based builds
- Restart policy (ON_FAILURE with 10 retries)

Railway automatically:
- Builds from `backend/Dockerfile`
- Exposes the service on Railway's domain
- Manages SSL certificates
- Provides zero-downtime deployments

## Troubleshooting

### Database Not Connected
- Verify `DATABASE_URL` is set in Railway variables
- Check Postgres service is running
- Run `python -m app.cli create-db` to initialize tables

### OAuth Not Working
- Verify `PUBLIC_HOST` matches your Railway domain exactly (with https://)
- Check Google Console redirect URI matches `{PUBLIC_HOST}/auth/callback`
- Test: `curl https://your-app.up.railway.app/auth/config`

### Image Uploads Failing
**Local Storage (Default):**
- Railway filesystem is ephemeral; uploads won't persist across deployments
- Use Railway Volumes (beta) or migrate to S3/R2

**S3/R2 Storage:**
- Set all `S3_*` environment variables
- Verify bucket permissions allow PUT operations
- Check `IMAGE_PUBLIC_BASE` is publicly accessible

### Build Failures
- Check Railway build logs for Python dependency errors
- Verify `backend/requirements.txt` is up to date
- Ensure Dockerfile is in `backend/` directory

### Service Won't Start
- Check Railway service logs
- Verify `PORT` environment variable (Railway sets this automatically)
- Ensure database is initialized: `railway run python -m app.cli create-db`

## Production Checklist

Before going live:

- [ ] Database initialized (`create-db` ran successfully)
- [ ] `PUBLIC_HOST` matches your Railway domain
- [ ] Google OAuth redirect URI configured correctly
- [ ] S3/R2 configured for persistent image storage (recommended)
- [ ] `OAUTH_SECRET_KEY` is a strong random value
- [ ] CORS `FRONTEND_ORIGIN` matches your actual frontend domain
- [ ] Health endpoint responding: `https://your-app.up.railway.app/healthz`
- [ ] GitHub Actions secrets configured for auto-deploy

## Monitoring

- **Health Check:** `GET /healthz` should return `{"ok": true}`
- **Railway Dashboard:** Monitor service metrics, logs, and deployment status
- **Database:** Check Postgres plugin metrics in Railway dashboard

## Cost Optimization

- Railway free tier includes $5/month credit
- Typical usage: ~$5-10/month (backend + Postgres)
- Add Railway Volumes (+$0.25/GB/month) or use S3/R2 for images
- Monitor usage in Railway dashboard → Project → Usage
