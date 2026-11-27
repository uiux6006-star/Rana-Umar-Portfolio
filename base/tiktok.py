"""
TikTok helpers for the "From my TikTok" section.

- video_id_from_url(): reads the numeric id from a TikTok video link.
- resolve(): follows TikTok short links (vt.tiktok.com / vm.tiktok.com).
- fetch_details(): video id (oEmbed) + title and thumbnail from TikTok's
  creator embed, which lists an account's recent public videos.
- creator_videos(): the latest public videos of an account.

Only TikTok's own hosts are ever contacted, with short timeouts and a size
limit, and every failure just returns None so the admin can still save.
"""

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

log = logging.getLogger(__name__)

VIDEO_RE = re.compile(r"/video/(\d{8,25})")
OEMBED = "https://www.tiktok.com/oembed?url="
TIKTOK_HOSTS = ("tiktok.com",)
IMAGE_HOSTS = ("tiktokcdn.com", "tiktokcdn-us.com", "tiktokcdn-eu.com", "ibyteimg.com", "tiktok.com")
MAX_IMAGE_BYTES = 3 * 1024 * 1024
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; rud-portfolio)"}


def _host_ok(url, allowed):
    parts = urllib.parse.urlparse(url)
    host = (parts.hostname or "").lower()
    return parts.scheme == "https" and any(host == h or host.endswith("." + h) for h in allowed)


def is_tiktok_url(url):
    return _host_ok(url, TIKTOK_HOSTS)


def video_id_from_url(url):
    match = VIDEO_RE.search(url or "")
    return match.group(1) if match else ""


def resolve(url):
    """Follow a short link to the full video URL. Returns the input if it fails."""
    if not is_tiktok_url(url):
        return url
    try:
        request = urllib.request.Request(url, headers=HEADERS, method="GET")
        with urllib.request.urlopen(request, timeout=8) as response:
            final = response.geturl()
        return final if is_tiktok_url(final) else url
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        log.warning("Could not resolve TikTok link %s: %s", url, exc)
        return url


USERNAME_RE = re.compile(r"tiktok\.com/@([\w.]+)")
CREATOR_EMBED = "https://www.tiktok.com/embed/@{}"
STATE_RE = re.compile(r'<script[^>]*id="__FRONTITY_CONNECT_STATE__"[^>]*>(.*?)</script>', re.S)


def username_from_url(url):
    match = USERNAME_RE.search(url or "")
    return match.group(1) if match else ""


def clean_title(desc):
    """Readable title from a TikTok caption: no hashtags, no extra spaces."""
    text = re.sub(r"#\S+", " ", desc or "")
    text = re.sub(r"\s+", " ", text).strip(" \"'“”‘’-—|")
    if len(text) > 100:
        text = text[:100].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return text if len(text.split()) >= 3 else ""  # captions that were only hashtags


def creator_videos(username):
    """Recent public videos from TikTok's creator embed: [{id, title, cover}], newest first."""
    if not re.fullmatch(r"[\w.]{2,40}", username or ""):
        return []
    try:
        request = urllib.request.Request(CREATOR_EMBED.format(username), headers={
            **HEADERS, "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        })
        with urllib.request.urlopen(request, timeout=10) as response:
            html = response.read(3_000_000).decode("utf-8", "replace")
        state = json.loads(STATE_RE.search(html).group(1))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError, AttributeError) as exc:
        log.warning("TikTok creator embed failed for %s: %s", username, exc)
        return []

    found = []

    def walk(node):
        if isinstance(node, dict):
            if isinstance(node.get("videoList"), list):
                for v in node["videoList"]:
                    if isinstance(v, dict) and str(v.get("id", "")).isdigit() and not v.get("privateItem"):
                        found.append({
                            "id": str(v["id"]),
                            "title": clean_title(v.get("desc", "")),
                            "cover": v.get("originCoverUrl") or v.get("coverUrl") or "",
                        })
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(state)
    unique = {v["id"]: v for v in found}
    return sorted(unique.values(), key=lambda v: int(v["id"]), reverse=True)  # TikTok ids grow over time


def fetch_details(url, username=""):
    """{"title", "thumbnail_url", "video_id"} for a video link, or None if TikTok can't be reached."""
    if not is_tiktok_url(url):
        return None

    video_id = video_id_from_url(url)
    if not video_id:
        try:
            request = urllib.request.Request(OEMBED + urllib.parse.quote(url, safe=""), headers=HEADERS)
            with urllib.request.urlopen(request, timeout=8) as response:
                data = json.loads(response.read(200_000).decode("utf-8"))
            video_id = str(data.get("embed_product_id") or "")
            if not video_id.isdigit():
                match = re.search(r"/player/v1/(\d+)", data.get("html", ""))
                video_id = match.group(1) if match else ""
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
            log.warning("TikTok oEmbed failed for %s: %s", url, exc)

    videos = creator_videos(username_from_url(url) or username)
    if not videos and not video_id:
        return None
    match = next((v for v in videos if v["id"] == video_id), None)
    return {
        "video_id": video_id,
        "title": match["title"] if match else "",
        "thumbnail_url": match["cover"] if match else "",
    }


def download_image(url):
    """Image bytes from TikTok's CDN, or None."""
    if not url or not _host_ok(url, IMAGE_HOSTS):
        return None
    try:
        request = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(request, timeout=10) as response:
            if not response.headers.get("Content-Type", "").startswith("image/"):
                return None
            data = response.read(MAX_IMAGE_BYTES + 1)
        return data if 0 < len(data) <= MAX_IMAGE_BYTES else None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        log.warning("TikTok thumbnail download failed: %s", exc)
        return None
