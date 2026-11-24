"""
Developer hub endpoints: GitHub activity and the interactive terminal's data.

GitHub
    Public data from the GitHub REST API, fetched on the server and cached for
    an hour, so visitors never hit GitHub's rate limit and no credentials reach
    the browser. Set GITHUB_TOKEN in .env to raise the limit (optional).
    If GitHub can't be reached, the endpoint says so ({"ok": false}) and the
    page shows a fallback. It never makes data up.

Terminal
    Everything the terminal's commands print, built from the database and
    base/profile.py, loaded only when someone opens the terminal.
"""

import json
import logging
import os
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone

from django.core.cache import cache
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from . import profile
from .models import Project

log = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
CACHE_KEY = f"github:{profile.GITHUB_USERNAME}"
CACHE_OK = 60 * 60          # 1 hour
CACHE_FAILED = 60 * 10      # try again after 10 minutes
ACTIVITY_WEEKS = 12


def _get(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "rud-portfolio",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(GITHUB_API + path, headers=headers)
    with urllib.request.urlopen(request, timeout=6) as response:
        return json.loads(response.read().decode("utf-8"))


def _activity(events, today):
    """Public events per day for the last ACTIVITY_WEEKS weeks (oldest first)."""
    days = ACTIVITY_WEEKS * 7
    start = today - timedelta(days=days - 1)
    counts = Counter()
    for event in events:
        try:
            day = datetime.strptime(event["created_at"][:10], "%Y-%m-%d").date()
        except (KeyError, TypeError, ValueError):
            continue
        if start <= day <= today:
            weight = len(event.get("payload", {}).get("commits", [])) if event.get("type") == "PushEvent" else 1
            counts[day] += max(1, weight)
    return [
        {"date": (start + timedelta(days=i)).isoformat(), "count": counts[start + timedelta(days=i)]}
        for i in range(days)
    ]


def fetch_github():
    """Build the GitHub summary, or None if GitHub can't be reached."""
    user = profile.GITHUB_USERNAME
    try:
        info = _get(f"/users/{user}")
        repos = _get(f"/users/{user}/repos?per_page=100&sort=pushed")
        events = _get(f"/users/{user}/events/public?per_page=100")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        log.warning("GitHub fetch failed: %s", exc)
        return None

    own = [r for r in repos if not r.get("fork")]
    own.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)

    languages = Counter(r["language"] for r in own if r.get("language"))
    total = sum(languages.values()) or 1

    now = datetime.now(timezone.utc)
    activity = _activity(events if isinstance(events, list) else [], now.date())

    return {
        "ok": True,
        "fetched_at": now.isoformat(timespec="seconds"),
        "profile": {
            "login": info.get("login", user),
            "name": info.get("name") or "",
            "avatar": info.get("avatar_url", ""),
            "bio": info.get("bio") or "",
            "url": info.get("html_url", profile.GITHUB_URL),
            "public_repos": info.get("public_repos", len(own)),
            "followers": info.get("followers", 0),
            "following": info.get("following", 0),
        },
        "repos": [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "url": r["html_url"],
                "homepage": r.get("homepage") or "",
                "language": r.get("language") or "",
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "pushed_at": r.get("pushed_at") or "",
            }
            for r in own[:6]
        ],
        "languages": [
            {"name": name, "repos": n, "percent": round(n * 100 / total)}
            for name, n in languages.most_common(6)
        ],
        "activity": activity,
        "activity_total": sum(d["count"] for d in activity),
    }


def github_summary():
    data = cache.get(CACHE_KEY)
    if data is None:
        data = fetch_github() or {"ok": False}
        cache.set(CACHE_KEY, data, CACHE_OK if data.get("ok") else CACHE_FAILED)
    return data


@require_GET
@cache_control(max_age=600, public=True)
def github_data(request):
    data = dict(github_summary())
    data["username"] = profile.GITHUB_USERNAME
    data["profile_url"] = profile.GITHUB_URL
    return JsonResponse(data)


@require_GET
@cache_control(max_age=300, public=True)
def terminal_data(request):
    projects = list(Project.objects.order_by("-created_at"))
    skills = profile.skill_by_id()

    return JsonResponse({
        "name": "Rana Umar",
        "brand": "RUD — Rana Umar Developer",
        "role": profile.ROLE,
        "future": profile.FUTURE_ROLE,
        "location": profile.LOCATION,
        "summary": profile.SUMMARY,
        "skills": [
            {
                "group": g["label"],
                "items": [{"name": s["name"], "level": s["level"]} for s in profile.SKILLS if s["group"] == g["id"]],
            }
            for g in profile.SKILL_GROUPS
        ],
        "projects": [
            {
                "title": p.title,
                "url": p.get_absolute_url(),
                "kind": p.get_kind_display() if p.kind else p.get_category_display(),
                "tech": p.tech_list[:5],
                "live": p.live_demo or "",
            }
            for p in projects if p.slug
        ],
        "experience": profile.EXPERIENCE,
        "education": profile.EDUCATION,
        "journey": [
            {"title": j["title"], "skills": [skills[s]["name"] for s in j["skills"] if s in skills]}
            for j in profile.JOURNEY
        ],
        "services": [{"name": s["name"], "text": s["text"]} for s in profile.SERVICES],
        "contact": {
            "email": profile.EMAIL,
            "whatsapp": f"https://wa.me/{profile.WHATSAPP_NUMBER}",
            "github": profile.GITHUB_URL,
            "linkedin": profile.LINKEDIN_URL,
            "page": reverse("contact"),
        },
        "cv": static(profile.CV_PATH),
        "urls": {
            "projects": reverse("projects"),
            "about": reverse("about"),
            "services": reverse("services"),
            "planner": reverse("estimate"),
            "blog": reverse("blog"),
        },
    })
