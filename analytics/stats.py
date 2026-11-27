"""Numbers for the Visitors section of the admin dashboard."""

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from .models import PageView

PAGE_NAMES = {
    "/": "Home",
    "/about/": "About",
    "/projects/": "Projects",
    "/services/": "Services",
    "/blog/": "Blog",
    "/contact/": "Contact",
    "/estimate/": "Project Planner",
    "/review/": "Leave a review",
}


def _bars(rows, limit=6):
    rows = list(rows)[:limit]
    top = max((r["count"] for r in rows), default=0) or 1
    for r in rows:
        r["pct"] = round(r["count"] * 100 / top)
    return rows


def _page_label(path, project_titles, post_titles):
    if path in PAGE_NAMES:
        return PAGE_NAMES[path]
    parts = [p for p in path.split("/") if p]
    if len(parts) == 2 and parts[0] == "project":
        return project_titles.get(parts[1], parts[1])
    if len(parts) == 2 and parts[0] == "blog":
        return "Blog: " + post_titles.get(parts[1], parts[1])
    return path


def _unique_visits(qs):
    """Daily unique visitors, added up (the anonymous id changes every day)."""
    return qs.values("day", "visitor").distinct().count()


def visitor_summary(days=30):
    today = timezone.localdate()
    start = today - timedelta(days=days - 1)
    prev_start = start - timedelta(days=days)

    window = PageView.objects.filter(day__gte=start)
    previous = PageView.objects.filter(day__gte=prev_start, day__lt=start)

    views = window.count()
    prev_views = previous.count()
    change = round((views - prev_views) * 100 / prev_views) if prev_views else None

    # Daily chart
    per_day = {r["day"]: r for r in window.values("day").annotate(count=Count("id"), visitors=Count("visitor", distinct=True))}
    daily = []
    for i in range(days):
        d = start + timedelta(days=i)
        row = per_day.get(d, {})
        daily.append({
            "date": d,
            "count": row.get("count", 0),
            "visitors": row.get("visitors", 0),
            "label": d.strftime("%d") if (days - 1 - i) % 5 == 0 else "",
            "today": d == today,
        })
    top_day = max((d["count"] for d in daily), default=0) or 1
    for d in daily:
        d["pct"] = round(d["count"] * 100 / top_day)

    # Names for pages
    from base.models import Post, Project
    project_titles = dict(Project.objects.values_list("slug", "title"))
    post_titles = dict(Post.objects.values_list("slug", "title"))

    pages = [
        {"label": _page_label(r["path"], project_titles, post_titles), "path": r["path"], "count": r["count"]}
        for r in window.values("path").annotate(count=Count("id")).order_by("-count")[:8]
    ]

    projects = [
        {"label": _page_label(r["path"], project_titles, post_titles), "path": r["path"], "count": r["count"]}
        for r in window.filter(path__startswith="/project/").values("path").annotate(count=Count("id")).order_by("-count")[:6]
    ]

    sources = [
        {"label": r["source"], "count": r["count"]}
        for r in window.exclude(source="").values("source").annotate(count=Count("id")).order_by("-count")[:6]
    ]

    device_labels = dict(PageView.DEVICE_CHOICES)
    devices = [
        {"label": device_labels.get(r["device"], r["device"]), "count": r["count"]}
        for r in window.values("device").annotate(count=Count("visitor", distinct=True)).order_by("-count")
    ]

    week = PageView.objects.filter(day__gte=today - timedelta(days=6))
    today_qs = PageView.objects.filter(day=today)

    first = PageView.objects.order_by("created_at").values_list("created_at", flat=True).first()

    return {
        "days": days,
        "has_data": views > 0 or PageView.objects.exists(),
        "tracking_since": first,
        "views_today": today_qs.count(),
        "visitors_today": today_qs.values("visitor").distinct().count(),
        "views_week": week.count(),
        "visits_week": _unique_visits(week),
        "views": views,
        "visits": _unique_visits(window),
        "change": change,
        "change_abs": abs(change) if change is not None else None,
        "daily": daily,
        "pages": _bars(pages, 8),
        "projects": _bars(projects),
        "sources": _bars(sources),
        "devices": _bars(devices, 3),
    }
