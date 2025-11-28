# QR Business Card – MVP: Scan to Add Contact

## Introduction/Overview

Build a web-based creator that generates a QR code which, when scanned, opens the native Add Contact flow on iOS and Android with prefilled details. The MVP emphasizes reliability, speed, and simplicity for individuals/freelancers, while enabling hosted vCard links to support monetization.

## Goals

1. Ensure >99% of scans trigger an add-contact prompt on iOS/Android.
2. Deliver <300ms TTFB for hosted `.vcf` downloads (p95).
3. Keep QR codes easily scannable at standard readability distances (print and screen).
4. Allow users to create, preview, and export QR codes and `.vcf` files quickly.
5. Support hosted vCard links (short slugs) as the default mode to enable monetization.

## User Stories

1. As an individual professional, I want to generate a QR that opens my contact so people can save my info in one tap.
2. As a user, I want to include my social links (LinkedIn/Instagram/Twitter/Facebook) and a profile photo so my contact is recognizable.
3. As a user, I want a hosted link so I can update details later without reprinting my QR.
4. As a user, I want to sign in with Google to manage my hosted profile(s) securely.
5. As a recipient, I want the scan to immediately present an Add Contact screen with accurate fields.

## Functional Requirements

1. QR Generation
   1.1 The system must generate a QR that encodes a short HTTPS URL to a hosted `.vcf` file (default mode).
   1.2 The system must also support generating an embedded MECARD QR as an optional offline fallback.
   1.3 The QR generator must allow PNG and SVG exports and set appropriate error correction (default ECC level M or Q) and quiet zone.
   1.4 The UI must show a live QR preview and a density/legibility indicator.

2. vCard (.vcf) Output (vCard 3.0)
   2.1 The backend must serve a `.vcf` with content type `text/vcard; charset=utf-8` and filename `contact.vcf`.
   2.2 Required fields supported: full name, company, title, phone(s), email(s), website, address, note.
   2.3 Social fields supported as URLs: LinkedIn, Instagram, Twitter (X), Facebook.
   2.4 Photo must be supported as a URL reference in the vCard (`PHOTO;VALUE=URI:`). Base64 embedding is out of scope for MVP to keep payloads small and downloads fast.
   2.5 Mapping (examples):
       - `FN:` Full Name
       - `N:` last;first;;;
       - `ORG:` Company
       - `TITLE:` Title
       - `TEL;TYPE=cell|work|home:` Number (E.164 recommended)
       - `EMAIL;TYPE=work|home:` Address
       - `URL:` Personal/Company website (repeatable for social links)
       - `ADR;TYPE=work:` `;;street;city;region;postcode;country`
       - `NOTE:` Freeform note
       - `PHOTO;VALUE=URI:` HTTPS image URL (optional)
   2.6 The system must add Apple-specific `X-SOCIALPROFILE` lines for well-known networks (LinkedIn/Instagram/Twitter/Facebook) in addition to standard `URL` entries to improve iOS Contacts rendering; non-Apple platforms safely ignore these.
   2.7 Notes:
       - `X-SOCIALPROFILE` is an Apple extension that makes social links appear as tappable profiles in iOS Contacts. Android/other clients fall back to `URL` fields.
       - Keep social links as both `URL` and `X-SOCIALPROFILE` for best cross-platform behavior.

3. Creator App (Web)
   3.1 The creator must be a responsive web app (desktop + mobile web) with a form for all supported fields.
   3.2 The app must provide validation (email format, E.164 phone normalization hint, URL format) and show guidance if the QR becomes too dense.
   3.3 The app must allow downloading the `.vcf` directly (client-generated) even without hosting.
   3.4 The app must allow switching QR mode: Hosted URL (default) vs MECARD.
   3.5 The app must display a summary preview of the contact information alongside the QR.

4. Hosting & Accounts
   4.1 Users can create a hosted profile that generates a short slug (e.g., `/u/abc123.vcf`).
   4.2 Google Sign-In must be available to create/manage hosted profiles.
   4.3 Anonymous (no-login) use is allowed for local `.vcf` download and QR export, but hosting requires login.
   4.4 Hosted profiles must be private/unlisted (no indexing), retrievable only by direct URL.
   4.5 Users must be able to update hosted profile fields; updates reflect in the served `.vcf` within seconds.
   4.6 Users must be able to delete a hosted profile and revoke access to the slug.
   4.7 Monetization (MVP): Hosting requires a subscription at X$/month with a 7-day free trial; price is configurable (no paywall for local downloads/QR exports). If the trial ends without payment, hosted links become inactive until the subscription is started.

5. Scan Experience
   5.1 Scanning a hosted QR must initiate a direct `.vcf` download without an intermediate landing page.
   5.2 iOS/Android should open the native Add Contact sheet (subject to OS behavior) upon download/open.
   5.3 The system must set headers to maximize native handling: correct MIME type, content disposition with filename, and caching headers.

6. Privacy & Security
   6.1 Do not log PII in server logs; redact fields where possible.
   6.2 Use random, non-guessable slugs (6–8+ chars) and `robots`/`noindex` protections.
   6.3 Input sanitization must be applied to all fields; enforce size caps to prevent oversized QR.
   6.4 Rate limit hosted `.vcf` retrieval per IP to mitigate abuse.

## Non-Goals (Out of Scope)

1. Full visual business card designer (templates, fonts, themes).
2. Team/multi-user org management and advanced RBAC.
3. Analytics dashboard (beyond minimal download count for internal reliability).
4. CRM/ATS integrations and webhooks.
5. Custom domains and branded profile pages.
6. Inline/base64 photo embedding in `.vcf`.

## Design Considerations

- Branding (MVP): Keep the creator UI clean and neutral; include a lightweight brand header/logo only. No card layout designer in MVP. The hosted flow uses direct `.vcf` download—no landing page UI to brand in V1. If a minimal marketing site is present, apply a simple brand header and footer; QR exports remain unbranded.
- Readability: Show a legibility meter that reacts to content length and chosen QR mode (URL vs MECARD). Provide guidance to shorten text or switch modes if density is high.
- Export: Offer PNG for general use and SVG for print; include quiet zone guidance and recommended printed size (e.g., ≥2–3 cm square at 300 dpi).
- Accessibility: Ensure sufficient contrast for QR preview; keyboard navigable form; labels and hints for all inputs.

## Technical Considerations

- Stack: Frontend in Next.js/React; backend in Python FastAPI serving APIs and the `.vcf` endpoint.
- Data: Postgres (SQLAlchemy + Alembic) for profiles/subscriptions; small KV/Redis (optional) for slug → profile lookup cache. Profile: `{ id, userId, slug, fields, createdAt, updatedAt }`.
- QR: Client-side QR preview using `qrcode`/`qrcode.react`; ECC level M/Q; default to URL QR for smaller modules and better reliability.
- vCard: Generate vCard 3.0 on the backend. Include Apple `X-SOCIALPROFILE` in addition to `URL` for socials. Escape commas/semicolons/newlines per spec.
- Headers: `Content-Type: text/vcard; charset=utf-8`, `Content-Disposition: attachment; filename="contact.vcf"`. Add `Cache-Control` and `ETag` for performance; CDN-cacheable.
- Mobile nuances: Test iOS Safari and Android Chrome direct download behavior; ensure tap-to-open flows present the add-contact sheet reliably.
- Security: Google OAuth via Authlib; HttpOnly session cookies; CSRF protection; minimal PII stored; encryption at rest. Enforce CORS to frontend origin.
- OS/Browser Support: iOS 13+ and Android 8+; latest two versions of Safari, Chrome, Edge, and Firefox.
- Domain: Use temporary subdomain `qr.trika.ai` for hosted links (e.g., `https://qr.trika.ai/u/{slug}.vcf`). Frontend can be at `app.qr.trika.ai` if desired.
- Payments: Stripe Checkout + Billing Portal via stripe-python; 7‑day free trial; price via environment variable.
- Photo Hosting: Use S3-compatible storage (e.g., Cloudflare R2/S3). Backend provides presigned URLs; serve optimized public images at `https://qr.trika.ai/i/{id}.jpg` referenced by `PHOTO;VALUE=URI`. Fallback: allow user-provided public image URL.
- Deployment: Frontend on Vercel (CNAME under `qr.trika.ai`), backend on Fly.io/Render/Heroku-like PaaS behind Cloudflare CDN for global <300ms TTFB.

### API Endpoints (Backend)
- GET `/u/{slug}.vcf`: Return vCard; set caching headers; CDN cacheable.
- POST `/api/profile` (auth + active subscription): Create or update profile fields.
- GET `/api/profile/{id}` (auth): Retrieve own profile.
- POST `/api/upload-photo` (auth): Return S3/R2 presigned URL; store resulting public image URL on success.
- POST `/api/stripe/checkout` (auth): Create Stripe Checkout session with 7‑day trial.
- POST `/api/stripe/webhook`: Handle subscription lifecycle events; activate/deactivate hosting.

## Success Metrics

- Reliability: >99% of scans result in an add-contact prompt (across a defined device/OS test matrix).
- Performance: Hosted `.vcf` TTFB <300ms (p95); file size <30KB typical (without embedded photo).
- QR Quality: Default QR readable at standard distances on recent phones; print at ≥2–3 cm remains scannable.
- Creation Flow: >95% of users complete QR generation in <60 seconds.

## Open Questions

1. Data retention policy for hosted profiles: keep until user deletes (proposed default), or add auto-expiration options?
