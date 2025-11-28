from fastapi import APIRouter, Response, HTTPException, Depends
from sqlalchemy.orm import Session
from ..services.vcard import build_vcard
from ..db import get_db
from ..models import Profile as ProfileModel
from ..models_user import User
from datetime import datetime, timezone

router = APIRouter()

# In-memory stub store: slug -> profile dict
PROFILES = {
    "demo123": {
        "fullName": "Ada Lovelace",
        "firstName": "Ada",
        "lastName": "Lovelace",
        "org": "Analytical Engines",
        "title": "Engineer",
        "phones": [{"type": "cell", "number": "+15551234567"}],
        "emails": [{"type": "work", "address": "ada@example.com"}],
        "url": "https://example.com",
        "social": {
            "linkedin": "https://www.linkedin.com/in/adalovelace",
            "instagram": "https://www.instagram.com/ada",
            "twitter": "https://twitter.com/ada",
            "facebook": "https://www.facebook.com/ada"
        },
        "address": {
            "street": "1 Computing Way",
            "city": "London",
            "region": "",
            "postcode": "SW1A 1AA",
            "country": "UK"
        },
        "note": "Scan to save.",
        "photoUrl": "https://example.com/photo.jpg"
    }
}

@router.get("/u/{slug}.vcf")
def get_vcard(slug: str, db: Session = Depends(get_db)):
    profile = PROFILES.get(slug)
    if not profile:
        # Fallback to DB
        m = db.query(ProfileModel).filter_by(slug=slug).first()
        if not m or not m.active:
            raise HTTPException(status_code=404, detail="Profile not found")
        # Monetization gate: require active subscription or valid trial on owner
        if m.user_id:
            u = db.get(User, m.user_id)
            if not _user_has_access(u):
                raise HTTPException(status_code=402, detail="Subscription required or trial ended")
        profile = {
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
    vcf = build_vcard(profile)
    headers = {
        "Content-Type": "text/vcard; charset=utf-8",
        "Content-Disposition": "attachment; filename=contact.vcf",
        "Cache-Control": "public, max-age=300",
    }
    return Response(content=vcf, media_type="text/vcard", headers=headers)


def _user_has_access(user: User | None) -> bool:
    if not user:
        return False
    now = datetime.now(timezone.utc)
    # active subscription (optionally with end date)
    if user.sub_active and (user.sub_ends_at is None or user.sub_ends_at > now):
        return True
    # valid trial
    if user.trial_ends_at and user.trial_ends_at > now:
        return True
    return False
