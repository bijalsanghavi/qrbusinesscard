import os

ENV = os.getenv("ENV", "development").lower()

IS_DEV = ENV == "development"
IS_PROD = ENV in ("prod", "production")

# Feature flags derived from ENV
ENABLE_DEV_ROUTES = IS_DEV
ENABLE_CREATE_ALL = os.getenv("ENABLE_CREATE_ALL", "false").lower() in ("true", "1", "yes") or IS_DEV
ENABLE_LOCAL_MEDIA = True   # allow serving /media in both, can be overridden later

# CORS origins
# TEMPORARY: Hardcoded to fix .env loading issue
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN") or "http://localhost:3000"
if FRONTEND_ORIGIN == "http://localhost:3002":  # Override incorrect cached value
    FRONTEND_ORIGIN = "http://localhost:3000"

# Session secret
SESSION_SECRET = os.getenv("OAUTH_SECRET_KEY", "dev-secret-change-me")

