#!/usr/bin/env bash
set -euo pipefail

BASE=${BASE:-http://localhost:3001}
FRONT=${FRONT:-http://localhost:3002}
COOKIES="$(mktemp /tmp/qrcard-cookies.XXXXXX)"
cleanup(){ rm -f "$COOKIES" 2>/dev/null || true; }
trap cleanup EXIT

echo "[test] Using BASE=$BASE FRONT=$FRONT"

echo "[test] 1) Health check"
curl -sf "$BASE/healthz" | grep -q '"ok": true' && echo "   OK"

echo "[test] 2) Auth config"
CFG=$(curl -sf "$BASE/auth/config")
echo "   $CFG" | grep -q '"redirect_uri": "http://localhost:3001/auth/callback"' || {
  echo "   WARN: redirect_uri not as expected: $(echo "$CFG" | tr -d '\n')";
}

echo "[test] 3) Dev login (session cookie)"
curl -sf -X POST -c "$COOKIES" -b "$COOKIES" "$BASE/dev/login" >/dev/null && echo "   OK"
ME=$(curl -sf -c "$COOKIES" -b "$COOKIES" "$BASE/auth/me" || true)
echo "   /auth/me => $ME"
echo "$ME" | grep -Eq '"authenticated"\s*:\s*true' || { echo "   ERROR: Not authenticated after dev login"; exit 1; }

echo "[test] 4) Init photo upload"
INIT=$(curl -sf -c "$COOKIES" -b "$COOKIES" -H 'Content-Type: application/json' \
  -d '{"filename":"test.jpg","contentType":"image/jpeg"}' \
  "$BASE/api/upload-photo")
echo "   INIT=$INIT"
UPLOAD_URL=$(python3 - <<PY
import json,sys
d=json.loads(sys.stdin.read());
print(d.get('uploadUrl',''))
PY
<<<"$INIT")
METHOD=$(python3 - <<PY
import json,sys
d=json.loads(sys.stdin.read());
print(d.get('method','PUT'))
PY
<<<"$INIT")
PUB_URL=$(python3 - <<PY
import json,sys
d=json.loads(sys.stdin.read());
print(d.get('publicUrl',''))
PY
<<<"$INIT")
KEY=$(python3 - <<PY
import json,sys
d=json.loads(sys.stdin.read());
print(d.get('key',''))
PY
<<<"$INIT")
echo "   method=$METHOD url=$UPLOAD_URL"

echo "[test] 5) Upload photo bytes"
if [[ "$UPLOAD_URL" == /* ]]; then
  # local direct upload
  curl -sf -X POST -c "$COOKIES" -b "$COOKIES" \
    --data-binary @/bin/bash \
    -H 'Content-Type: image/jpeg' \
    "$BASE$UPLOAD_URL" >/dev/null
else
  curl -sf -X "$METHOD" --data-binary @/bin/bash \
    -H 'Content-Type: image/jpeg' \
    "$UPLOAD_URL" >/dev/null
fi
echo "   OK"

echo "[test] 6) Verify public image"
curl -sf "$BASE$PUB_URL" >/dev/null && echo "   OK"

echo "[test] 7) Create profile"
PROFILE=$(cat <<JSON
{
  "fullName": "Test User",
  "firstName": "Test",
  "lastName": "User",
  "phones": [{"type":"cell","number":"+15551234567"}],
  "emails": [{"type":"work","address":"test@example.com"}],
  "url": "https://example.com",
  "social": {"linkedin":"https://linkedin.com/in/test"},
  "address": {"street":"1 Test", "city":"City", "country":"US"},
  "photoUrl": "$BASE$PUB_URL"
}
JSON
)
RES=$(curl -sf -c "$COOKIES" -b "$COOKIES" -H 'Content-Type: application/json' \
  -d "$PROFILE" "$BASE/api/profile")
SLUG=$(python3 - <<PY
import json,sys
print(json.loads(sys.stdin.read()).get('slug',''))
PY
<<<"$RES")
echo "   slug=$SLUG"

echo "[test] 8) Fetch vCard"
VCF=$(curl -sf "$BASE/u/$SLUG.vcf")
echo "$VCF" | grep -q 'BEGIN:VCARD' && echo "   vCard OK" || { echo "   vCard missing header"; exit 1; }
echo "$VCF" | grep -q 'PHOTO;VALUE=URI' && echo "   PHOTO OK" || { echo "   PHOTO missing"; exit 1; }

echo "[test] All checks passed."
