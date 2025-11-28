# Unified API Guide

Base URL (local): `http://localhost:3001`

All requests should include cookies (`credentials: include` in browsers). JSON bodies use `application/json`.

## Auth & Session

GET `/auth/me`
- 200 JSON: `{ authenticated: false }` or `{ authenticated: true, user: { id, email, name?, picture? } }`

GET `/auth/login`
- Full-page navigation to start Google OAuth; on success redirects back to frontend origin.

POST `/auth/logout`
- 200 JSON: `{ ok: true }`

GET `/auth/config` (dev aid)
- 200 JSON: `{ env: { ENV, FRONTEND_ORIGIN, PUBLIC_HOST }, google: { client_id_set, client_secret_set, redirect_uri } }`

## Dev Helpers (development only)

POST `/dev/login`
- Sets a development session cookie.

POST `/dev/seed-profile`
- Creates a sample profile with slug `devcard` for the current session user.

## Uploads

POST `/api/upload-photo` (auth required)
- Request: `{ "filename": string, "contentType": string }`
- Response:
  - Always: `{ publicUrl: string, key: string }`
  - Local/direct mode: `{ uploadUrl: "/api/upload-photo-direct?key=...", method: "POST", headers: { "Content-Type": string }, direct: true }`
  - Presigned mode (future S3/R2): `{ uploadUrl: string, method: "PUT", headers: { "Content-Type": string, "Cache-Control"?: string } }`
- Client behavior:
  - If `uploadUrl` is relative or `direct: true`: POST bytes to `BASE + uploadUrl` with headers.
  - Else: PUT bytes to absolute `uploadUrl` with headers.
  - On success, use `publicUrl` in the profile’s `photoUrl`.

POST `/api/upload-photo-direct` (auth required)
- Query: `?key=...` (returned from init).
- Body: raw file bytes.
- 200 JSON: `{ ok: true, publicUrl, key }`.

## Profiles

POST `/api/profile` (auth required)
- Request example:
```
{
  "fullName": "Jane Doe",
  "firstName": "Jane",
  "lastName": "Doe",
  "org": "Acme",
  "title": "Manager",
  "phones": [{ "type": "cell", "number": "+15551234567" }],
  "emails": [{ "type": "work", "address": "jane@acme.com" }],
  "url": "https://example.com",
  "social": { "linkedin": "https://linkedin.com/in/janedoe" },
  "address": { "street": "1 Main", "city": "SF", "country": "US" },
  "note": "Hi",
  "photoUrl": "https://host/media/..." or "/media/..." (prefix with BASE for absolute)
}
```
- Response: profile object including `id` and `slug`.

GET `/api/profile/{id}` (auth required, owner-only)
- Response: same shape as profile create.

## vCard

GET `/u/{slug}.vcf`
- Content-Type: `text/vcard; charset=utf-8`
- Triggers native “Add Contact” flows on mobile.

## Notes
- All endpoints are rate-limited at infrastructure level in production (not included in this repo).
- Avoid embedding large photos in vCard; use `PHOTO;VALUE=URI` with an HTTPS URL.

