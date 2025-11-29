from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import os
from datetime import datetime, timedelta, timezone

from ..auth import oauth
from ..db import get_db
from ..models_user import User
from ..config import IS_DEV, FRONTEND_ORIGIN

router = APIRouter()


def _public_host(request: Request) -> str:
    host = os.getenv("PUBLIC_HOST")
    if host:
        return host.rstrip("/")
    # dev fallback
    scheme = request.url.scheme
    # Backend runs on 3001 locally
    return f"{scheme}://{request.client.host}:3001"


@router.get("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        # Be explicit; do not hide config issues
        raise HTTPException(status_code=500, detail="Missing GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET in environment. Set them in backend/.env. Redirect URI must be http://localhost:3001/auth/callback for local.")

    # Re-register client each time to ensure fresh config
    try:
        # Remove existing to avoid duplicate-registration issues
        oauth._clients.pop('google', None)
    except Exception:
        pass
    oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    redirect_uri = _public_host(request) + "/auth/callback"
    # Log computed values to server console for quick diagnosis in dev
    if IS_DEV:
        print(f"[auth] Using GOOGLE_CLIENT_ID={client_id}")
        print(f"[auth] Computed redirect_uri={redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/config")
def auth_config(request: Request):
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = _public_host(request) + "/auth/callback"
    return {
        "env": {
            "ENV": os.getenv("ENV", "development"),
            "FRONTEND_ORIGIN": os.getenv("FRONTEND_ORIGIN"),
            "PUBLIC_HOST": os.getenv("PUBLIC_HOST"),
        },
        "google": {
            "client_id_set": bool(client_id),
            "client_secret_set": bool(client_secret),
            "redirect_uri": redirect_uri,
        },
    }


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = token.get('userinfo') or {}
        email = userinfo.get('email')
        if not email:
            raise HTTPException(status_code=400, detail="No email from Google")
        name = userinfo.get('name')
        picture = userinfo.get('picture')

        # upsert user
        user = db.query(User).filter_by(email=email).first()
        if not user:
            # initialize trial period
            trial_days = int(os.getenv('TRIAL_DAYS', '7'))
            trial_ends = datetime.now(timezone.utc) + timedelta(days=trial_days)
            user = User(email=email, name=name, picture=picture, trial_ends_at=trial_ends)
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            changed = False
            if user.name != name:
                user.name = name
                changed = True
            if user.picture != picture:
                user.picture = picture
                changed = True
            # backfill trial end if missing
            if user.trial_ends_at is None:
                trial_days = int(os.getenv('TRIAL_DAYS', '7'))
                user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=trial_days)
                changed = True
            if changed:
                db.add(user)
                db.commit()

        # set session
        request.session['user_id'] = user.id
        request.session['email'] = user.email
        # redirect back to frontend
        # Use config module instead of os.getenv to get correct value
        return RedirectResponse(url=FRONTEND_ORIGIN)
    except Exception as e:
        # Log detailed error for debugging
        import traceback
        print(f"[auth/callback] ERROR: {type(e).__name__}: {str(e)}")
        print(f"[auth/callback] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"{type(e).__name__}: {str(e)}")


@router.get("/me")
def me(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get('user_id')
    if not uid:
        return JSONResponse(status_code=200, content={"authenticated": False})
    user = db.get(User, uid)
    if not user:
        return JSONResponse(status_code=200, content={"authenticated": False})
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        }
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}
