from .models import SiteTheme
from .themes import ORIGINAL, THEMES, build_css, google_font_query

PREVIEW_SESSION_KEY = "theme_preview"


def can_customize(user):
    return user.is_active and user.is_staff and user.has_perm("appearance.change_sitetheme")


def site_theme(request):
    """Adds the active theme (or a staff member's preview) to every template."""

    # Admin pages have their own theme; skip the query there.
    if request.path.startswith("/admin/"):
        return {}

    setting = SiteTheme.current()
    slug, accent = setting.theme, setting.custom_accent
    preview = None

    data = request.session.get(PREVIEW_SESSION_KEY) if hasattr(request, "session") else None
    if data and request.user.is_authenticated and can_customize(request.user):
        if data.get("theme") in THEMES:
            slug = data["theme"]
            accent = data.get("accent", "")
            preview = {
                "name": THEMES[slug]["name"],
                "accent": accent,
                "is_active": slug == setting.theme and accent == setting.custom_accent,
            }

    return {
        "site_theme": {
            "slug": slug,
            "name": THEMES.get(slug, THEMES[ORIGINAL])["name"],
            "bg": THEMES.get(slug, THEMES[ORIGINAL])["bg"],
            "css": build_css(slug, accent),
            "font_query": google_font_query(slug),
            "preview": preview,
        }
    }
