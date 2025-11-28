from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from ..storage import build_photo_key, create_presigned_put, build_public_url, save_local_bytes
import os

router = APIRouter()


class UploadReq(BaseModel):
    filename: str
    contentType: str


@router.post("/upload-photo")
def upload_photo(req: UploadReq, request: Request):
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(status_code=401, detail="Login required")
    if not req.contentType.lower().startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed")
    key = build_photo_key(uid, req.filename, req.contentType)
    # If S3/R2 is configured, return a presigned PUT; else use local direct upload
    if os.getenv("S3_ENDPOINT_URL") and os.getenv("S3_BUCKET") and os.getenv("S3_ACCESS_KEY_ID"):
        try:
            cache_control = os.getenv("UPLOAD_CACHE_CONTROL", "public, max-age=31536000, immutable")
            url = create_presigned_put(key, req.contentType, cache_control=cache_control)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        return {
            "uploadUrl": url,
            "method": "PUT",
            "headers": {"Content-Type": req.contentType, "Cache-Control": cache_control},
            "publicUrl": build_public_url(key),
            "key": key,
        }
    else:
        # local mode: client should POST raw bytes to direct endpoint
        return {
            "uploadUrl": f"/api/upload-photo-direct?key={key}",
            "method": "POST",
            "headers": {"Content-Type": req.contentType},
            "publicUrl": build_public_url(key),
            "key": key,
            "direct": True,
        }


@router.post("/upload-photo-direct")
async def upload_photo_direct(request: Request, key: str):
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(status_code=401, detail="Login required")
    # Read raw body and save to local storage
    max_bytes = int(os.getenv("MAX_UPLOAD_BYTES", "2000000"))
    data = await request.body()
    if not data:
        raise HTTPException(status_code=400, detail="No data")
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    try:
        save_local_bytes(key, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True, "publicUrl": build_public_url(key), "key": key}
