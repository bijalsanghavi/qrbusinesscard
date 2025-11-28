import os
import time
import uuid
import mimetypes
from typing import Tuple
from pathlib import Path

import boto3


def get_s3_client():
    endpoint_url = os.getenv("S3_ENDPOINT_URL")
    access_key = os.getenv("S3_ACCESS_KEY_ID")
    secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
    )


def guess_ext(content_type: str) -> str:
    if not content_type:
        return ""
    ext = mimetypes.guess_extension(content_type) or ""
    # normalize jpeg
    if ext == ".jpe":
        ext = ".jpg"
    return ext


def build_photo_key(user_id: str, filename: str, content_type: str) -> str:
    base = f"profiles/{user_id}/{uuid.uuid4().hex}"
    ext = guess_ext(content_type)
    if not ext and "." in filename:
        ext = "." + filename.rsplit(".", 1)[-1]
    return base + (ext or "")


def build_public_url(key: str) -> str:
    base = os.getenv("IMAGE_PUBLIC_BASE")
    if base:
        return f"{base.rstrip('/')}/{key}"
    # Fallback to local media route
    return f"/media/{key}"


def create_presigned_put(key: str, content_type: str, expires_in: int = 900, cache_control: str | None = None) -> str:
    bucket = os.getenv("S3_BUCKET")
    client = get_s3_client()
    params = {
        "Bucket": bucket,
        "Key": key,
        "ContentType": content_type or "application/octet-stream",
    }
    if cache_control:
        params["CacheControl"] = cache_control
    url = client.generate_presigned_url(
        "put_object", Params=params, ExpiresIn=expires_in
    )
    return url


def save_local_bytes(key: str, data: bytes):
    upload_dir = os.getenv("UPLOAD_DIR", os.path.join(os.getcwd(), "media"))
    # prevent path traversal
    safe_key = key.replace("..", "").lstrip("/")
    path = Path(upload_dir) / safe_key
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return str(path)
