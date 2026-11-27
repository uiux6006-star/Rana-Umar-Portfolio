"""
Decides which requests count as a page view and describes them.

Counted:     successful GET requests for public HTML pages.
Not counted: the admin, static/media files, JSON endpoints, robots/sitemap,
             link prefetches, bots and crawlers, and logged-in staff
             (so your own visits don't inflate the numbers).
"""

import hashlib
import re
from urllib.parse import parse_qs, urlparse

from django.conf import settings
from django.utils import timezone

SKIP_PREFIXES = (
    "/admin", "/static", "/media", "/chat/", "/github/", "/terminal/",
    "/robots.txt", "/sitemap.xml", "/favicon", "/reset/",
)

BOT_RE = re.compile(
    r"bot|crawl|spider|slurp|bingpreview|facebookexternalhit|embedly|quora link preview|"
    r"whatsapp|telegram|skypeuripreview|discord|slack|headless|lighthouse|pingdom|uptime|"
    r"python-requests|python-urllib|curl|wget|httpclient|go-http|java/|axios|node-fetch|monitor|preview",
    re.IGNORECASE,
)

# Referrer host -> friendly source name
SOURCES = [
    ("google.", "Google"),
    ("bing.", "Bing"),
    ("duckduckgo.", "DuckDuckGo"),
    ("yahoo.", "Yahoo"),
    ("linkedin.", "LinkedIn"),
    ("lnkd.in", "LinkedIn"),
    ("whatsapp.", "WhatsApp"),
    ("wa.me", "WhatsApp"),
    ("github.", "GitHub"),
    ("facebook.", "Facebook"),
    ("fb.", "Facebook"),
    ("instagram.", "Instagram"),
    ("t.co", "X (Twitter)"),
    ("twitter.", "X (Twitter)"),
    ("x.com", "X (Twitter)"),
    ("youtube.", "YouTube"),
    ("fiverr.", "Fiverr"),
    ("upwork.", "Upwork"),
    ("netlify.app", "Netlify demos"),
    ("chatgpt.", "ChatGPT"),
]

DIRECT = "Direct"


def should_track(request, response):
    if request.method != "GET" or response.status_code != 200:
        return False
    if not response.get("Content-Type", "").startswith("text/html"):
        return False
    path = request.path
    if any(path.startswith(p) for p in SKIP_PREFIXES):
        return False
    # Link prefetching / prerendering isn't a real view
    purpose = (request.headers.get("Sec-Purpose", "") + request.headers.get("Purpose", "")).lower()
    if "prefetch" in purpose or "prerender" in purpose:
        return False
    ua = request.headers.get("User-Agent", "")
    if not ua or BOT_RE.search(ua):
        return False
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and user.is_staff:
        return False
    return True


def client_ip(request):
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.headers.get("X-Real-IP") or request.META.get("REMOTE_ADDR", "")


def visitor_id(request, day=None):
    """Anonymous id that changes every day. The IP itself is never stored."""
    day = day or timezone.localdate()
    raw = f"{settings.SECRET_KEY}|{day.isoformat()}|{client_ip(request)}|{request.headers.get('User-Agent', '')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def device_of(user_agent):
    ua = user_agent or ""
    if re.search(r"iPad|Tablet|PlayBook|Silk|Kindle", ua, re.I) or ("Android" in ua and "Mobile" not in ua):
        return "tablet"
    if re.search(r"Mobi|iPhone|iPod|Android|Opera Mini|IEMobile", ua, re.I):
        return "mobile"
    return "desktop"


def source_of(request):
    """Where the visit came from. Empty string = a click inside this site."""
    utm = parse_qs(urlparse(request.get_full_path()).query).get("utm_source")
    if utm and utm[0].strip():
        return utm[0].strip()[:60].title()

    referer = request.headers.get("Referer", "")
    if not referer:
        return DIRECT
    host = (urlparse(referer).hostname or "").lower()
    if not host:
        return DIRECT
    if host == request.get_host().split(":")[0].lower():
        return ""  # moving between pages of this site
    for needle, name in SOURCES:
        if needle in host:
            return name
    return host.removeprefix("www.")[:60]
