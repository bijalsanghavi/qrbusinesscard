# QR Business Card API Reference

**Base URL (Production):** `https://qrbusinesscard-production-qrcode.up.railway.app`
**Base URL (Local):** `http://localhost:3001`

---

## Health Check

### GET /healthz
Check if the API is running.

**Response:**
```json
{
  "ok": true
}
```

---

## Authentication (Google OAuth)

### GET /auth/login
Initiate Google OAuth login flow.

**Response:** Redirects to Google login page

---

### GET /auth/callback
OAuth callback endpoint (handled automatically by Google).

**Query Params:**
- `code`: OAuth authorization code (from Google)

**Response:** Redirects to `FRONTEND_ORIGIN` with session cookie set

---

### GET /auth/config
Get authentication configuration (for debugging).

**Response:**
```json
{
  "env": {
    "ENV": "prod",
    "FRONTEND_ORIGIN": "https://qrbusinesscard.trika.ai",
    "PUBLIC_HOST": "https://qrbusinesscard-production-qrcode.up.railway.app"
  },
  "google": {
    "client_id_set": true,
    "client_secret_set": true,
    "redirect_uri": "https://qrbusinesscard-production-qrcode.up.railway.app/auth/callback"
  }
}
```

---

### GET /auth/me
Get current authenticated user.

**Authentication:** Session cookie required

**Response (authenticated):**
```json
{
  "authenticated": true,
  "user": {
    "id": "abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "picture": "https://..."
  }
}
```

**Response (not authenticated):**
```json
{
  "authenticated": false
}
```

---

### POST /auth/logout
Logout current user.

**Authentication:** Session cookie required

**Response:**
```json
{
  "ok": true
}
```

---

## Profile Management

### POST /api/profile
Create a new profile (business card).

**Authentication:** Session cookie required

**Request Body:**
```json
{
  "fullName": "John Doe",
  "firstName": "John",
  "lastName": "Doe",
  "org": "Acme Inc",
  "title": "CEO",
  "phones": [
    {
      "type": "cell",
      "number": "+15551234567"
    }
  ],
  "emails": [
    {
      "type": "work",
      "address": "john@acme.com"
    }
  ],
  "url": "https://acme.com",
  "social": {
    "linkedin": "https://linkedin.com/in/johndoe",
    "instagram": "https://instagram.com/johndoe",
    "twitter": "https://twitter.com/johndoe",
    "facebook": "https://facebook.com/johndoe"
  },
  "address": {
    "street": "123 Main St",
    "city": "San Francisco",
    "region": "CA",
    "postcode": "94102",
    "country": "US"
  },
  "note": "Scan to save my contact!",
  "photoUrl": "https://qrbusinesscard-production-qrcode.up.railway.app/media/profiles/abc/photo.jpg"
}
```

**Response:**
```json
{
  "id": "profile123",
  "slug": "abc123xyz",
  "fullName": "John Doe",
  ... // same fields as request
}
```

---

### GET /api/profile/{id}
Get a specific profile by ID.

**Authentication:** Session cookie required (must be owner)

**Response:**
```json
{
  "id": "profile123",
  "slug": "abc123xyz",
  "fullName": "John Doe",
  ... // all profile fields
}
```

---

## File Upload

### POST /api/upload-photo
Initialize photo upload.

**Authentication:** Session cookie required

**Request Body:**
```json
{
  "filename": "photo.jpg",
  "contentType": "image/jpeg"
}
```

**Response (Local mode):**
```json
{
  "uploadUrl": "/api/upload-photo-direct?key=profiles/user123/xyz.jpg",
  "method": "POST",
  "headers": {
    "Content-Type": "image/jpeg"
  },
  "publicUrl": "/media/profiles/user123/xyz.jpg",
  "key": "profiles/user123/xyz.jpg",
  "direct": true
}
```

**Response (S3 mode):**
```json
{
  "uploadUrl": "https://s3.amazonaws.com/...",
  "method": "PUT",
  "headers": {
    "Content-Type": "image/jpeg",
    "Cache-Control": "public, max-age=31536000, immutable"
  },
  "publicUrl": "https://cdn.example.com/profiles/user123/xyz.jpg",
  "key": "profiles/user123/xyz.jpg"
}
```

**Usage:**
1. Call `/api/upload-photo` to get upload URL
2. Upload file to the returned `uploadUrl` using the specified `method`
3. Use the `publicUrl` in your profile's `photoUrl` field

---

### POST /api/upload-photo-direct
Direct upload endpoint (local mode only).

**Authentication:** Session cookie required

**Query Params:**
- `key`: The key returned from `/api/upload-photo`

**Request Body:** Raw image bytes (binary)

**Headers:**
- `Content-Type`: image/jpeg, image/png, etc.

**Response:**
```json
{
  "ok": true,
  "publicUrl": "/media/profiles/user123/xyz.jpg",
  "key": "profiles/user123/xyz.jpg"
}
```

---

## vCard Generation

### GET /u/{slug}.vcf
Get vCard file for a profile.

**Public endpoint** (no authentication required)

**Response:** vCard file (text/vcard)
```
BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
ORG:Acme Inc
TITLE:CEO
TEL;TYPE=cell:+15551234567
EMAIL;TYPE=work:john@acme.com
URL:https://acme.com
PHOTO;VALUE=URI:https://...
END:VCARD
```

**Example:**
- `GET /u/demo123.vcf` - Demo card (built-in)
- `GET /u/abc123xyz.vcf` - Your created card

---

## Billing (Stripe - Stub)

### POST /api/stripe/checkout
Create Stripe checkout session (stub).

**Authentication:** Session cookie required

**Response:**
```json
{
  "checkoutUrl": "https://checkout.stripe.com/pay/demo"
}
```

---

### POST /api/stripe/webhook
Stripe webhook handler (stub).

**Response:**
```json
{
  "received": true
}
```

---

## Development Endpoints (Local Only)

Only available when `ENV=development`

### POST /dev/login
Auto-login as dev user (no OAuth needed).

**Response:**
```json
{
  "ok": true
}
```

---

### POST /dev/seed-profile
Create test profile with slug "devcard".

**Authentication:** Dev session required (call `/dev/login` first)

**Response:**
```json
{
  "slug": "devcard"
}
```

---

## Error Responses

All endpoints may return these error formats:

**401 Unauthorized:**
```json
{
  "detail": "Login required"
}
```

**403 Forbidden:**
```json
{
  "detail": "Forbidden"
}
```

**404 Not Found:**
```json
{
  "detail": "Profile not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Only image uploads are allowed"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error message"
}
```

---

## Authentication Flow

1. Frontend redirects user to `/auth/login`
2. User completes Google OAuth
3. Backend redirects back to frontend with session cookie
4. Frontend calls `/auth/me` to get user info
5. All subsequent API calls include the session cookie automatically

## CORS Configuration

The API allows requests from:
- `https://qrbusinesscard.trika.ai` (production frontend)
- `http://localhost:3000` (local development)

Credentials (cookies) are included in cross-origin requests.
