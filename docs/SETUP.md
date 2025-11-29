# QR Business Card - Complete Setup Guide

Quick reference for getting your QR Business Card application running locally and in production.

---

## 🏠 Local Development Setup

### Prerequisites
- Docker Desktop installed and running
- Node.js 18+ installed
- Git installed

### Quick Start

```bash
# 1. Clone backend repo
git clone https://github.com/bijalsanghavi/qrbusinesscard.git
cd qrbusinesscard

# 2. Run full-stack development environment
./scripts/dev-fullstack.sh
```

**That's it!** The script will:
- ✅ Start PostgreSQL in Docker
- ✅ Start backend on `http://localhost:3001`
- ✅ Clone frontend repo (if not exists)
- ✅ Install frontend dependencies
- ✅ Start frontend on `http://localhost:5173`
- ✅ Open browser automatically

### Manual Setup (if you prefer)

**Terminal 1 - Backend:**
```bash
cd qrbusinesscard/backend
./scripts/run.sh
```

**Terminal 2 - Frontend:**
```bash
cd qrbusinesscard-frontend
npm install
echo "VITE_API_URL=http://localhost:3001" > .env.local
npm run dev
```

### Local Testing
```bash
# Health check
curl http://localhost:3001/healthz
# Should return: {"ok": true}

# Dev login (no OAuth needed locally)
curl -X POST http://localhost:3001/dev/login -c cookies.txt

# Create test profile
curl -X POST http://localhost:3001/dev/seed-profile -b cookies.txt
# Should return: {"slug": "devcard"}

# Get vCard
curl http://localhost:3001/u/devcard.vcf
```

---

## 🚀 Production Deployment

### Architecture
```
Frontend: Netlify  → https://qrbusinesscard.netlify.app
Backend:  Railway  → https://qrbusinesscard-production-qrcode.up.railway.app
```

### 1️⃣ Backend Deployment (Railway)

**Status:** ✅ Already deployed!

Your backend is live at:
```
https://qrbusinesscard-production-qrcode.up.railway.app
```

**Environment variables set:**
- `DATABASE_URL` - PostgreSQL connection (auto-set by Railway)
- `GOOGLE_CLIENT_ID` - OAuth credentials
- `GOOGLE_CLIENT_SECRET` - OAuth credentials
- `PUBLIC_HOST` - Your Railway URL
- `FRONTEND_ORIGIN` - **UPDATE THIS** after Netlify deploy

**To redeploy:**
```bash
# Auto-deploy via GitHub
git push origin main

# Or manual deploy
cd backend
railway up
```

---

### 2️⃣ Frontend Deployment (Netlify)

**Follow:** [`docs/NETLIFY_SETUP.md`](./NETLIFY_SETUP.md)

**Quick version:**

1. **Go to Netlify Dashboard**: https://app.netlify.com
2. **Import from GitHub**: Select `qrbusinesscard-frontend` repo
3. **Build settings**:
   ```
   Build command: npm run build
   Publish directory: dist
   ```
4. **Add environment variable**:
   ```
   VITE_API_URL = https://qrbusinesscard-production-qrcode.up.railway.app
   ```
5. **Deploy!**

6. **Update Railway environment variable**:
   ```bash
   # After Netlify deploy, update this in Railway dashboard:
   FRONTEND_ORIGIN=https://[your-site].netlify.app
   ```

7. **Redeploy backend** (so CORS picks up new domain):
   ```bash
   railway redeploy
   ```

---

## 🔧 Configuration Reference

### Backend Environment Variables

**Local (`.env`):**
```bash
ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5555/qrbusiness
UPLOAD_DIR=media
PUBLIC_HOST=http://localhost:3001
FRONTEND_ORIGIN=http://localhost:5173
SESSION_SECRET=dev-secret-change-in-prod
ENABLE_CREATE_ALL=true
ENABLE_DEV_ROUTES=true
ENABLE_LOCAL_MEDIA=true
```

**Production (Railway):**
```bash
ENV=production
DATABASE_URL=[auto-set by Railway]
PUBLIC_HOST=https://qrbusinesscard-production-qrcode.up.railway.app
FRONTEND_ORIGIN=https://[your-site].netlify.app
SESSION_SECRET=[generate random string]
GOOGLE_CLIENT_ID=[from Google Console]
GOOGLE_CLIENT_SECRET=[from Google Console]
ENABLE_LOCAL_MEDIA=true
```

### Frontend Environment Variables

**Local (`.env.local`):**
```bash
VITE_API_URL=http://localhost:3001
```

**Production (Netlify):**
```bash
VITE_API_URL=https://qrbusinesscard-production-qrcode.up.railway.app
```

---

## 📋 Deployment Checklist

### Initial Production Setup
- [x] Backend deployed to Railway
- [x] PostgreSQL database connected
- [x] Google OAuth credentials configured
- [ ] Frontend deployed to Netlify
- [ ] `VITE_API_URL` set in Netlify
- [ ] `FRONTEND_ORIGIN` updated in Railway
- [ ] Test OAuth login flow
- [ ] Create test business card
- [ ] Scan QR code on phone

### Local Development Setup
- [ ] Docker Desktop running
- [ ] Run `./scripts/dev-fullstack.sh`
- [ ] Backend running on port 3001
- [ ] Frontend running on port 5173
- [ ] Test creating a business card locally

---

## 🔍 Troubleshooting

### Local Development

**❌ "Docker is not running"**
```bash
# Start Docker Desktop application
open -a Docker  # macOS
```

**❌ "Port 3001 already in use"**
```bash
# Find and kill process
lsof -ti:3001 | xargs kill -9
```

**❌ "Port 5555 already in use" (Postgres)**
```bash
docker compose down
docker compose up -d
```

**❌ Frontend can't reach backend**
```bash
# Check backend is running
curl http://localhost:3001/healthz

# Check .env.local in frontend
cat qrbusinesscard-frontend/.env.local
# Should show: VITE_API_URL=http://localhost:3001
```

### Production

**❌ "Failed to fetch" from frontend**
- Check: Is `VITE_API_URL` set in Netlify?
- Check: Is your Netlify domain in Railway's `FRONTEND_ORIGIN`?
- Check: Backend health: `curl https://[railway-url]/healthz`

**❌ "OAuth redirects to wrong URL"**
- Update `FRONTEND_ORIGIN` in Railway
- Redeploy backend: `railway redeploy`

**❌ "CORS error"**
- Verify `FRONTEND_ORIGIN` matches your Netlify domain exactly
- Check `allowed_origins` in `backend/app/main.py`

---

## 📚 Documentation

- **API Reference**: [`docs/API_REFERENCE.md`](./API_REFERENCE.md) - Complete API documentation
- **API for Gemini**: [`docs/API_FOR_GEMINI.md`](./API_FOR_GEMINI.md) - Frontend integration guide
- **Railway Setup**: [`docs/RAILWAY_SETUP.md`](./RAILWAY_SETUP.md) - Backend deployment guide
- **Netlify Setup**: [`docs/NETLIFY_SETUP.md`](./NETLIFY_SETUP.md) - Frontend deployment guide
- **Deployment**: [`docs/DEPLOY.md`](./DEPLOY.md) - General deployment notes

---

## 🆘 Getting Help

### Check Logs

**Local:**
```bash
# Backend logs
tail -f /tmp/qr-backend.log

# Frontend logs
tail -f /tmp/qr-frontend.log
```

**Production:**
```bash
# Backend (Railway)
railway logs

# Frontend (Netlify)
# View in dashboard: Deploys → [Latest] → Deploy log
```

### Common Commands

```bash
# Restart local development
./scripts/dev-fullstack.sh

# Deploy to Railway
git push origin main

# Check Railway status
railway status

# Check Netlify status
netlify status
```

---

## 🎯 Next Steps

1. ✅ **Complete Netlify deployment** using [`docs/NETLIFY_SETUP.md`](./NETLIFY_SETUP.md)
2. ✅ **Test production** by creating a business card
3. ✅ **Scan QR code** on your phone to verify it works
4. 🎨 **Customize frontend** with Gemini
5. 🚀 **Share your business cards!**

---

## 📞 Support

- **Railway Issues**: https://railway.app/help
- **Netlify Issues**: https://answers.netlify.com
- **Backend Repo**: https://github.com/bijalsanghavi/qrbusinesscard
