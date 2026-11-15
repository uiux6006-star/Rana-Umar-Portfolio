"""Numbers for the admin dashboard home page."""

from datetime import timedelta

from django import template
from django.db.models import Avg, Count
from django.utils import timezone

from base.models import ContactMessage, Post, Project, Testimonial

register = template.Library()


def _month_start(dt, months_back=0):
    year, month = dt.year, dt.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return dt.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)


def _breakdown(field, choices):
    counts = dict(
        ContactMessage.objects.exclude(**{field: ""})
        .values_list(field)
        .annotate(n=Count("id"))
    )
    top = max(counts.values(), default=0)
    return [
        {
            "label": label,
            "count": counts.get(key, 0),
            "pct": round(counts.get(key, 0) * 100 / top) if top else 0,
        }
        for key, label in choices
    ]


def _change(now_value, before_value):
    if not before_value:
        return None
    return round((now_value - before_value) * 100 / before_value)


@register.simple_tag
def dashboard_data():
    now = timezone.localtime()
    this_month = _month_start(now)
    last_month = _month_start(now, 1)

    leads = ContactMessage.objects.all()
    total = leads.count()

    leads_this_month = leads.filter(created_at__gte=this_month).count()
    leads_last_month = leads.filter(created_at__gte=last_month, created_at__lt=this_month).count()

    status_counts = dict(leads.values_list("status").annotate(n=Count("id")))
    won = status_counts.get(ContactMessage.STATUS_WON, 0)
    lost = status_counts.get(ContactMessage.STATUS_LOST, 0)
    decided = won + lost

    # ----- Leads per month (last 6 months, oldest first) -----
    start = _month_start(now, 5)
    monthly = {}
    for created in leads.filter(created_at__gte=start).values_list("created_at", flat=True):
        local = timezone.localtime(created)
        monthly[(local.year, local.month)] = monthly.get((local.year, local.month), 0) + 1

    months = []
    for back in range(5, -1, -1):
        m = _month_start(now, back)
        months.append({
            "label": m.strftime("%b"),
            "full_label": m.strftime("%B %Y"),
            "count": monthly.get((m.year, m.month), 0),
            "current": back == 0,
        })
    peak = max((m["count"] for m in months), default=0)
    for m in months:
        m["pct"] = round(m["count"] * 100 / peak) if peak else 0

    pipeline = [
        {
            "key": key,
            "label": label,
            "count": status_counts.get(key, 0),
            "url_filter": f"?status__exact={key}",
        }
        for key, label in ContactMessage.STATUS_CHOICES
    ]

    reviews = Testimonial.objects.all()
    published_reviews = reviews.filter(is_published=True)

    return {
        "leads_total": total,
        "leads_new": status_counts.get(ContactMessage.STATUS_NEW, 0),
        "leads_this_month": leads_this_month,
        "leads_change": _change(leads_this_month, leads_last_month),
        "leads_week": leads.filter(created_at__gte=now - timedelta(days=7)).count(),
        "won": won,
        "win_rate": round(won * 100 / decided) if decided else None,
        "pipeline": pipeline,
        "months": months,
        "months_total": sum(m["count"] for m in months),
        "budgets": _breakdown("budget", ContactMessage.BUDGET_CHOICES),
        "project_types": _breakdown("project_type", ContactMessage.PROJECT_TYPE_CHOICES),
        "recent_leads": leads.order_by("-created_at")[:6],
        "projects_total": Project.objects.count(),
        "projects_featured": Project.objects.filter(featured=True).count(),
        "posts_published": Post.objects.filter(is_published=True).count(),
        "posts_draft": Post.objects.filter(is_published=False).count(),
        "reviews_pending": reviews.filter(is_published=False).count(),
        "reviews_published": published_reviews.count(),
        "rating_avg": published_reviews.aggregate(avg=Avg("rating"))["avg"],
        "greeting": (
            "Good morning" if now.hour < 12
            else "Good afternoon" if now.hour < 17
            else "Good evening"
        ),
        "today": now,
    }
