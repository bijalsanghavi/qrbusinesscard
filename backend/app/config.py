import os

ENV = os.getenv("ENV", "development").lower()

IS_DEV = ENV == "development"
IS_PROD = ENV in ("prod", "production")

# Feature flags derived from ENV
ENABLE_DEV_ROUTES = IS_DEV
ENABLE_CREATE_ALL = IS_DEV  # only create tables automatically in development
ENABLE_LOCAL_MEDIA = True   # allow serving /media in both, can be overridden later

# CORS origins
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

# Session secret
SESSION_SECRET = os.getenv("OAUTH_SECRET_KEY", "dev-secret-change-me")

