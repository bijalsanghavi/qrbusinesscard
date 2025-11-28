from typing import Dict, List

def _escape(text: str) -> str:
    if text is None:
        return ""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )

def build_vcard(profile: Dict) -> str:
    first = profile.get("firstName", "") or ""
    last = profile.get("lastName", "") or ""
    fn = profile.get("fullName") or f"{first} {last}".strip()
    org = profile.get("org", "")
    title = profile.get("title", "")
    phones: List[Dict] = profile.get("phones", []) or []
    emails: List[Dict] = profile.get("emails", []) or []
    url = profile.get("url")
    social = profile.get("social", {}) or {}
    address = profile.get("address", {}) or {}
    note = profile.get("note", "")
    photo_url = profile.get("photoUrl")

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{_escape(fn)}",
        f"N:{_escape(last)};{_escape(first)};;;",
    ]

    if org:
        lines.append(f"ORG:{_escape(org)}")
    if title:
        lines.append(f"TITLE:{_escape(title)}")

    for ph in phones:
        t = (ph.get("type") or "cell").lower()
        num = ph.get("number", "")
        if num:
            lines.append(f"TEL;TYPE={t}:{_escape(num)}")
    for em in emails:
        t = (em.get("type") or "work").lower()
        addr = em.get("address", "")
        if addr:
            lines.append(f"EMAIL;TYPE={t}:{_escape(addr)}")

    if url:
        lines.append(f"URL:{_escape(url)}")

    # Social links as URL + Apple X-SOCIALPROFILE
    def add_social(kind: str, link: str):
        if not link:
            return
        lines.append(f"URL:{_escape(link)}")
        # Apple extension
        # Example: X-SOCIALPROFILE;type=linkedin:x-apple:https://www.linkedin.com/in/username
        lines.append(f"X-SOCIALPROFILE;type={kind}:{_escape(link)}")

    add_social("linkedin", social.get("linkedin"))
    add_social("instagram", social.get("instagram"))
    add_social("twitter", social.get("twitter"))
    add_social("facebook", social.get("facebook"))

    if address:
        street = address.get("street", "")
        city = address.get("city", "")
        region = address.get("region", "")
        postcode = address.get("postcode", "")
        country = address.get("country", "")
        lines.append(
            f"ADR;TYPE=work:;;{_escape(street)};{_escape(city)};{_escape(region)};{_escape(postcode)};{_escape(country)}"
        )

    if note:
        lines.append(f"NOTE:{_escape(note)}")

    if photo_url:
        lines.append(f"PHOTO;VALUE=URI:{_escape(photo_url)}")

    lines.append("END:VCARD")
    return "\r\n".join(lines) + "\r\n"

