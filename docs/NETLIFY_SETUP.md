# Netlify Deployment Guide - Frontend

Complete guide to deploy the QR Business Card frontend to Netlify.

---

## Prerequisites

1. **Netlify Account**: Sign up at [netlify.com](https://www.netlify.com)
2. **GitHub Account**: Frontend repo must be on GitHub
3. **Backend Running**: Railway backend already deployed at `https://qrbusinesscard-production-qrcode.up.railway.app`

---

## Step 1: Prepare Frontend Repository

### **Required Files**

Your frontend repo should have:

```
qrbusinesscard-frontend/
├── package.json
├── vite.config.js (or webpack/next config)
├── .env.production
├── .env.local (gitignored)
└── src/
```

### **Environment Variables**

**`.env.production`** (commit this):
```bash
VITE_API_URL=https://qrbusinesscard-production-qrcode.up.railway.app
```

**`.env.local`** (DO NOT commit):
```bash
VITE_API_URL=http://localhost:3001
```

### **Update `.gitignore`**
```
.env.local
.env*.local
```

### **Update `package.json`**
```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

---

## Step 2: Deploy to Netlify

### **Option A: Netlify Dashboard (Recommended)**

1. **Go to Netlify Dashboard**: https://app.netlify.com
2. **Click "Add new site" → "Import an existing project"**
3. **Choose GitHub** and authorize Netlify
4. **Select your frontend repository**: `qrbusinesscard-frontend`
5. **Configure build settings**:
   ```
   Base directory: (leave empty if repo root is the app)
   Build command: npm run build
   Publish directory: dist
   ```
6. **Click "Deploy site"**

### **Option B: Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize (from frontend repo root)
cd qrbusinesscard-frontend
netlify init

# Follow prompts:
# - Create & configure a new site
# - Build command: npm run build
# - Publish directory: dist

# Deploy
netlify deploy --prod
```

---

## Step 3: Configure Environment Variables

### **In Netlify Dashboard**

1. Go to **Site settings → Environment variables**
2. Click **Add a variable**
3. Add:
   ```
   Key: VITE_API_URL
   Value: https://qrbusinesscard-production-qrcode.up.railway.app
   ```
4. **Important**: Set scope to "All scopes" or "Production"
5. Click **Save**

### **Verify Environment Variables Work**

Add this to your frontend code temporarily:
```javascript
console.log('API URL:', import.meta.env.VITE_API_URL);
```

Deploy and check browser console - should show Railway URL, not localhost.

---

## Step 4: Update Backend CORS

Your backend already has CORS configured, but verify your Netlify domain is allowed.

**Your Netlify URL will be**: `https://[site-name].netlify.app` or `https://qrbusinesscard.trika.ai`

The backend (`app/main.py`) should include:
```python
allowed_origins = [
    "https://qrbusinesscard.trika.ai",      # Custom domain
    "https://[your-site].netlify.app",      # Netlify default domain
    "https://aistudio.google.com",          # Google AI Studio
    "http://localhost:5173",                # Local dev
]
```

**If your Netlify domain is different**, you'll need to:
1. Add it to `allowed_origins` in `backend/app/main.py`
2. Commit and push to trigger Railway redeploy
3. Wait 2-3 minutes for Railway to update

---

## Step 5: Set Custom Domain (Optional)

### **Use Your Own Domain**

1. **In Netlify**: Site settings → Domain management → Add custom domain
2. **Enter**: `qrbusinesscard.trika.ai`
3. **Update DNS** (in your domain registrar):
   ```
   Type: CNAME
   Name: qrbusinesscard
   Value: [your-site].netlify.app
   ```
4. **Wait for DNS propagation** (5 minutes - 24 hours)
5. **Netlify auto-provisions HTTPS** (via Let's Encrypt)

### **Update Backend CORS**

If you set a custom domain, update backend CORS:
```python
allowed_origins = [
    "https://qrbusinesscard.trika.ai",  # Your custom domain
    # ... rest
]
```

---

## Step 6: Test Production Deployment

### **Test Checklist**

```bash
# 1. Frontend loads
curl -I https://qrbusinesscard.trika.ai
# Should return: 200 OK

# 2. Backend health check
curl https://qrbusinesscard-production-qrcode.up.railway.app/healthz
# Should return: {"ok": true}

# 3. Test in browser
open https://qrbusinesscard.trika.ai
# Check browser console for errors
# Try logging in with Google OAuth
# Create a test profile
# Verify QR code works
```

### **Common Issues**

**❌ "Failed to fetch" errors**
- Check: Is VITE_API_URL set in Netlify env vars?
- Check: Is your Netlify domain in backend CORS?
- Check: Browser console for actual error

**❌ Google OAuth redirects to localhost**
- Check: `FRONTEND_ORIGIN` in Railway env vars
- Should be: `https://qrbusinesscard.trika.ai`
- Update and redeploy Railway

**❌ 404 on routes**
- Add `netlify.toml` to frontend repo:
  ```toml
  [[redirects]]
    from = "/*"
    to = "/index.html"
    status = 200
  ```

**❌ Images not loading**
- Check: Is `S3_BUCKET` set in Railway? (if using S3)
- Or: Is `ENABLE_LOCAL_MEDIA=true` in Railway? (if using local)

---

## Step 7: Enable Auto-Deploy

### **GitHub Integration (Default)**

Netlify automatically deploys when you push to your main branch:

```bash
# Make frontend changes
cd qrbusinesscard-frontend
# ... edit files ...
git add .
git commit -m "Update UI"
git push origin main

# Netlify auto-deploys in 1-2 minutes
```

### **Deploy Previews**

Netlify creates preview URLs for pull requests:
1. Create a PR in frontend repo
2. Netlify comments with preview URL
3. Test changes before merging
4. Merge PR → auto-deploy to production

---

## Production Deployment Workflow

```
┌─────────────────────────────────────────────────────┐
│                   PRODUCTION SETUP                   │
└─────────────────────────────────────────────────────┘

Frontend (Netlify)                Backend (Railway)
══════════════════                ═════════════════

1. Push to GitHub                 1. Push to GitHub
   ↓                                 ↓
2. Netlify auto-build             2. GitHub Actions
   ↓                                 ↓
3. Deploy to CDN                  3. Railway deploy
   ↓                                 ↓
4. https://qrbusinesscard         4. https://qrbusinesscard-
   .trika.ai                         production-qrcode.up.railway.app
   ↓                                 ↓
   └─────── API calls ──────────────┘
```

---

## Monitoring and Debugging

### **Netlify Deploy Logs**

1. Go to **Deploys** tab in Netlify dashboard
2. Click latest deploy
3. View build logs for errors

### **Check Frontend Errors**

```javascript
// Add to your frontend app
window.addEventListener('error', (e) => {
  console.error('Frontend error:', e);
});

// Check API calls
fetch(`${import.meta.env.VITE_API_URL}/healthz`)
  .then(r => r.json())
  .then(d => console.log('Backend health:', d))
  .catch(e => console.error('Backend unreachable:', e));
```

### **Netlify Functions (Optional)**

If you need serverless functions:
```
netlify/functions/
  └── hello.js  → https://[site].netlify.app/.netlify/functions/hello
```

But for this project, all backend logic is on Railway.

---

## Cost and Limits

| Feature | Free Tier | Paid |
|---------|-----------|------|
| **Bandwidth** | 100GB/month | $20/month for 1TB |
| **Build minutes** | 300/month | Unlimited |
| **Sites** | Unlimited | Unlimited |
| **Team members** | 1 | Multiple |
| **Deploy previews** | ✅ | ✅ |
| **Custom domains** | ✅ | ✅ |
| **HTTPS** | ✅ Auto | ✅ Auto |

**For this project**: Free tier is more than enough.

---

## Quick Reference

### **Netlify URLs**
- Dashboard: https://app.netlify.com
- Your site: https://[site-name].netlify.app
- Custom domain: https://qrbusinesscard.trika.ai

### **Important Environment Variables**
```bash
VITE_API_URL=https://qrbusinesscard-production-qrcode.up.railway.app
```

### **Deploy Commands**
```bash
# Manual deploy
netlify deploy --prod

# Open dashboard
netlify open

# View logs
netlify logs
```

### **Backend API Base URL**
```
https://qrbusinesscard-production-qrcode.up.railway.app
```

---

## Next Steps

1. ✅ Deploy frontend to Netlify
2. ✅ Set environment variables
3. ✅ Update backend CORS (if needed)
4. ✅ Test OAuth flow
5. ✅ Create a business card
6. ✅ Scan QR code on phone

---

## Support

- **Netlify Docs**: https://docs.netlify.com
- **Netlify Community**: https://answers.netlify.com
- **Backend API Docs**: `docs/API_FOR_GEMINI.md` in this repo
