from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .context_processors import PREVIEW_SESSION_KEY, can_customize
from .models import SiteTheme, hex_color
from .themes import ORIGINAL, THEMES, build_tokens, swatches


@admin.register(SiteTheme)
class SiteThemeAdmin(admin.ModelAdmin):
    """'Appearance > Theme Customizer'. The changelist is replaced by a
    custom page; every write goes through a POST view below."""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # ---------- URLs ----------

    def get_urls(self):
        wrap = self.admin_site.admin_view
        custom = [
            path("", wrap(self.customizer_view), name="theme_customizer"),
            path("apply/", wrap(require_POST(self.apply_view)), name="theme_apply"),
            path("accent/", wrap(require_POST(self.accent_view)), name="theme_accent"),
            path("reset/", wrap(require_POST(self.reset_view)), name="theme_reset"),
            path("preview/", wrap(require_POST(self.preview_view)), name="theme_preview"),
            path("preview/exit/", wrap(require_POST(self.preview_exit_view)), name="theme_preview_exit"),
        ]
        return custom + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        return redirect("admin:theme_customizer")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        return redirect("admin:theme_customizer")

    # ---------- helpers ----------

    def _check(self, request):
        if not can_customize(request.user):
            raise PermissionDenied

    def _back(self, request):
        target = request.POST.get("next", "")
        if target and url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
            return HttpResponseRedirect(target)
        return redirect("admin:theme_customizer")

    # ---------- views ----------

    def customizer_view(self, request):
        if not (request.user.is_staff and request.user.has_perm("appearance.view_sitetheme")) \
                and not can_customize(request.user):
            raise PermissionDenied

        setting = SiteTheme.load()
        themes = []
        for slug, theme in THEMES.items():
            tokens = build_tokens(slug)
            themes.append({
                "slug": slug,
                "name": theme["name"],
                "tagline": theme["tagline"],
                "tags": theme["tags"],
                "swatches": swatches(slug),
                "primary": theme["primary"],
                "bg": theme["bg"],
                "surface": theme["surface"],
                "text": theme["text"],
                "muted": theme["muted"],
                "accent": theme["accent"],
                "on_accent": tokens["dark"]["--on-accent"],
                "radius": tokens["shared"]["--radius-btn"],
                "font": tokens["shared"]["--font-heading"],
                "is_active": slug == setting.theme,
            })

        preview_tokens = {slug: build_tokens(slug) for slug in THEMES}

        context = {
            **self.admin_site.each_context(request),
            "title": "Theme Customizer",
            "opts": self.model._meta,
            "setting": setting,
            "active": THEMES[setting.theme],
            "previous": THEMES.get(setting.previous_theme) if setting.previous_theme else None,
            "themes": themes,
            "preview_tokens": preview_tokens,
            "can_edit": can_customize(request.user),
            "previewing": request.session.get(PREVIEW_SESSION_KEY),
        }
        return TemplateResponse(request, "admin/appearance/customizer.html", context)

    def apply_view(self, request):
        self._check(request)
        slug = request.POST.get("theme", "")
        if slug not in THEMES:
            messages.error(request, "That theme doesn't exist. Nothing was changed.")
            return self._back(request)

        accent = request.POST.get("accent", "").strip()
        if accent:
            try:
                hex_color(accent)
            except ValidationError:
                messages.error(request, "That accent colour isn't valid. Nothing was changed.")
                return self._back(request)

        setting = SiteTheme.load()
        setting.apply(slug, request.user)
        if accent:
            setting.custom_accent = accent
        elif "keep_accent" not in request.POST:
            setting.custom_accent = ""
        setting.save()

        request.session.pop(PREVIEW_SESSION_KEY, None)
        messages.success(request, f"“{THEMES[slug]['name']}” is now live on your website.")
        return self._back(request)

    def accent_view(self, request):
        self._check(request)
        setting = SiteTheme.load()

        if request.POST.get("clear"):
            setting.custom_accent = ""
            setting.updated_by = request.user
            setting.save()
            messages.success(request, "Custom accent removed. The theme's own colours are back.")
            return self._back(request)

        color = request.POST.get("accent", "").strip()
        try:
            hex_color(color)
        except ValidationError:
            messages.error(request, "Please pick a valid colour (6-digit hex like #69d7ff).")
            return self._back(request)

        setting.custom_accent = color
        setting.updated_by = request.user
        setting.save()
        messages.success(request, f"Custom accent {color.lower()} applied to “{setting.get_theme_display()}”.")
        return self._back(request)

    def reset_view(self, request):
        self._check(request)
        setting = SiteTheme.load()
        setting.apply(ORIGINAL, request.user)
        setting.custom_accent = ""
        setting.save()
        request.session.pop(PREVIEW_SESSION_KEY, None)
        messages.success(request, "Your website is back on the Original theme.")
        return self._back(request)

    def preview_view(self, request):
        """Show a theme on the real website for this admin only."""
        self._check(request)
        slug = request.POST.get("theme", "")
        accent = request.POST.get("accent", "").strip()
        if slug not in THEMES:
            messages.error(request, "That theme doesn't exist.")
            return redirect("admin:theme_customizer")
        try:
            if accent:
                hex_color(accent)
        except ValidationError:
            accent = ""

        request.session[PREVIEW_SESSION_KEY] = {"theme": slug, "accent": accent.lower()}
        return redirect(reverse("home"))

    def preview_exit_view(self, request):
        request.session.pop(PREVIEW_SESSION_KEY, None)
        return self._back(request)
