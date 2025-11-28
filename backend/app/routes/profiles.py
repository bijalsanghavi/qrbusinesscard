from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict
import secrets

from ..db import get_db
from ..models import Profile as ProfileModel
from ..schemas import ProfileIn, ProfileOut
from .vcf import PROFILES as VCF_PROFILES

router = APIRouter()

def _gen_slug(db: Session) -> str:
    for _ in range(5):
        slug = secrets.token_urlsafe(6).replace("_", "").replace("-", "")[:8]
        exists = db.query(ProfileModel).filter_by(slug=slug).first()
        if not exists:
            return slug
    return secrets.token_urlsafe(12).replace("_", "").replace("-", "")[:12]

@router.post("/profile", response_model=ProfileOut)
def create_or_update_profile(profile: ProfileIn, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get('user_id')
    if not uid:
        raise HTTPException(status_code=401, detail="Login required")
    slug = _gen_slug(db)
    m = ProfileModel(
        slug=slug,
        user_id=uid,
        full_name=profile.fullName,
        first_name=profile.firstName,
        last_name=profile.lastName,
        org=profile.org,
        title=profile.title,
        url=str(profile.url) if profile.url else None,
        note=profile.note,
        photo_url=str(profile.photoUrl) if profile.photoUrl else None,
        phones=[p.model_dump() for p in profile.phones],
        emails=[e.model_dump() for e in profile.emails],
        address=profile.address.model_dump(mode='json') if profile.address else {},
        social=profile.social.model_dump(mode='json') if profile.social else {},
    )
    db.add(m)
    db.commit()
    db.refresh(m)

    VCF_PROFILES[m.slug] = {
        "fullName": m.full_name,
        "firstName": m.first_name,
        "lastName": m.last_name,
        "org": m.org,
        "title": m.title,
        "phones": m.phones,
        "emails": m.emails,
        "url": m.url,
        "social": m.social,
        "address": m.address,
        "note": m.note,
        "photoUrl": m.photo_url,
    }

    return ProfileOut(
        id=m.id,
        slug=m.slug,
        fullName=m.full_name,
        firstName=m.first_name,
        lastName=m.last_name,
        org=m.org,
        title=m.title,
        phones=m.phones,
        emails=m.emails,
        url=m.url,
        social=m.social,
        address=m.address,
        note=m.note,
        photoUrl=m.photo_url,
    )

@router.get("/profile/{id}", response_model=ProfileOut)
def get_profile(id: str, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get('user_id')
    m = db.get(ProfileModel, id)
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    if not uid or m.user_id != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    return ProfileOut(
        id=m.id,
        slug=m.slug,
        fullName=m.full_name,
        firstName=m.first_name,
        lastName=m.last_name,
        org=m.org,
        title=m.title,
        phones=m.phones,
        emails=m.emails,
        url=m.url,
        social=m.social,
        address=m.address,
        note=m.note,
        photoUrl=m.photo_url,
    )
