from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
import os

from ..db import get_db
from ..models_user import User
from ..models import Profile
from datetime import datetime, timedelta, timezone

router = APIRouter()


from ..config import IS_DEV

def _ensure_dev():
    if not IS_DEV:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/login")
def dev_login(request: Request, db: Session = Depends(get_db)):
    _ensure_dev()
    email = "dev@example.com"
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(email=email, name="Dev User")
        db.add(user)
        db.commit()
        db.refresh(user)
    # ensure dev user has a valid long trial
    if user.trial_ends_at is None or user.trial_ends_at < datetime.now(timezone.utc):
        user.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=3650)
        db.add(user)
        db.commit()
    request.session['user_id'] = user.id
    request.session['email'] = user.email
    return {"ok": True, "user": {"id": user.id, "email": user.email}}


@router.post("/seed-profile")
def seed_profile(request: Request, db: Session = Depends(get_db)):
    _ensure_dev()
    uid = request.session.get('user_id')
    if not uid:
        raise HTTPException(status_code=401, detail="Login required (use /dev/login)")
    p = Profile(
        user_id=uid,
        slug="devcard",
        full_name="Dev User",
        first_name="Dev",
        last_name="User",
        org="Dev Co",
        title="Engineer",
        url="http://localhost:3000",
        phones=[{"type":"cell","number":"+10000000000"}],
        emails=[{"type":"work","address":"dev@example.com"}],
        address={"street":"1 Dev Way","city":"Local","region":"","postcode":"00000","country":"US"},
        social={"linkedin":"https://linkedin.com","instagram":"https://instagram.com","twitter":"https://twitter.com","facebook":"https://facebook.com"},
        note="Local seed profile",
        photo_url=None,
    )
    # Replace if exists
    existing = db.query(Profile).filter_by(slug=p.slug).first()
    if existing:
        db.delete(existing)
        db.commit()
    db.add(p)
    db.commit()
    db.refresh(p)
    return {"ok": True, "slug": p.slug}
