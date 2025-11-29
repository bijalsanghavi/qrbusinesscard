# QR Business Card - API Endpoints for Frontend

**Production API:** `https://qrbusinesscard-production-qrcode.up.railway.app`
**Local API:** `http://localhost:3001`

---

## Quick Reference

```javascript
const API_URL = 'https://qrbusinesscard-production-qrcode.up.railway.app';

// All requests must include credentials for session cookies
const fetchOptions = {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json'
  }
};
```

---

## Authentication Endpoints

```javascript
// 1. Login - Redirect user to this URL
window.location.href = `${API_URL}/auth/login`;

// 2. Get current user
const response = await fetch(`${API_URL}/auth/me`, {
  credentials: 'include'
});
const data = await response.json();
// Returns: { authenticated: true, user: { id, email, name, picture } }

// 3. Logout
await fetch(`${API_URL}/auth/logout`, {
  method: 'POST',
  credentials: 'include'
});
```

---

## Profile Management

```javascript
// Create Profile
const profile = {
  fullName: "John Doe",
  firstName: "John",
  lastName: "Doe",
  org: "Acme Inc",
  title: "CEO",
  phones: [{ type: "cell", number: "+15551234567" }],
  emails: [{ type: "work", address: "john@acme.com" }],
  url: "https://acme.com",
  social: {
    linkedin: "https://linkedin.com/in/johndoe",
    instagram: null,
    twitter: null,
    facebook: null
  },
  address: {
    street: "123 Main St",
    city: "San Francisco",
    region: "CA",
    postcode: "94102",
    country: "US"
  },
  note: "Scan to save!",
  photoUrl: "https://..." // From upload-photo endpoint
};

const response = await fetch(`${API_URL}/api/profile`, {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(profile)
});

const created = await response.json();
// Returns: { id, slug, ...profile fields }
```

---

## Photo Upload Flow

```javascript
// Step 1: Initialize upload
const initResponse = await fetch(`${API_URL}/api/upload-photo`, {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filename: file.name,
    contentType: file.type
  })
});

const { uploadUrl, method, headers, publicUrl } = await initResponse.json();

// Step 2: Upload the actual file
if (uploadUrl.startsWith('/')) {
  // Local mode - direct upload
  const uploadResponse = await fetch(`${API_URL}${uploadUrl}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': file.type },
    body: file
  });
} else {
  // S3 mode - presigned URL
  await fetch(uploadUrl, {
    method: method,
    headers: headers,
    body: file
  });
}

// Step 3: Use publicUrl in your profile
// photoUrl: publicUrl
```

---

## Get vCard

```javascript
// Public endpoint - no auth needed
const vcardUrl = `${API_URL}/u/${slug}.vcf`;

// Example:
// https://qrbusinesscard-production-qrcode.up.railway.app/u/abc123.vcf

// Use this URL in QR code generator
```

---

## Complete Example: Create Business Card

```javascript
async function createBusinessCard(formData, photoFile) {
  const API_URL = 'https://qrbusinesscard-production-qrcode.up.railway.app';

  // 1. Upload photo
  const uploadInit = await fetch(`${API_URL}/api/upload-photo`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      filename: photoFile.name,
      contentType: photoFile.type
    })
  });

  const { uploadUrl, publicUrl } = await uploadInit.json();

  // 2. Upload file
  await fetch(
    uploadUrl.startsWith('/') ? `${API_URL}${uploadUrl}` : uploadUrl,
    {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': photoFile.type },
      body: photoFile
    }
  );

  // 3. Create profile
  const profile = {
    fullName: formData.fullName,
    firstName: formData.firstName,
    lastName: formData.lastName,
    phones: [{ type: "cell", number: formData.phone }],
    emails: [{ type: "work", address: formData.email }],
    photoUrl: `${API_URL}${publicUrl}` // Make absolute URL
  };

  const profileResponse = await fetch(`${API_URL}/api/profile`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile)
  });

  const { slug } = await profileResponse.json();

  // 4. Generate QR code for this URL
  const vcardUrl = `${API_URL}/u/${slug}.vcf`;

  return { vcardUrl, slug };
}
```

---

## Error Handling

```javascript
try {
  const response = await fetch(`${API_URL}/api/profile`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile)
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Redirect to login
      window.location.href = `${API_URL}/auth/login`;
      return;
    }
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  const data = await response.json();
  // Success
} catch (error) {
  console.error('API Error:', error);
}
```

---

## Environment Variables for Frontend

```bash
# .env.local (development)
VITE_API_URL=http://localhost:3001

# .env.production
VITE_API_URL=https://qrbusinesscard-production-qrcode.up.railway.app
```

```javascript
// Use in code
const API_URL = import.meta.env.VITE_API_URL;
```

---

## Important Notes

1. **Always include `credentials: 'include'`** in fetch requests for session cookies
2. **Photo URLs must be absolute** when creating profiles (include full domain)
3. **Auth flow:** User clicks login → redirects to `/auth/login` → Google OAuth → redirects back to your app
4. **Check auth status** on app load with `/auth/me`
5. **vCard URLs are public** - no auth needed to download them
