from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from .themes import ORIGINAL, THEME_CHOICES, THEMES

hex_color = RegexValidator(
    regex=r"^#[0-9a-fA-F]{6}$",
    message="Use a 6-digit hex colour, e.g. #69d7ff.",
)


class SiteTheme(models.Model):
    """The single, site-wide theme setting (always row pk=1)."""

    theme = models.CharField(max_length=30, choices=THEME_CHOICES, default=ORIGINAL)

    previous_theme = models.CharField(max_length=30, choices=THEME_CHOICES, blank=True)

    custom_accent = models.CharField(
        max_length=7,
        blank=True,
        validators=[hex_color],
        help_text="Optional. Replaces the theme's primary colour everywhere.",
    )

    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        verbose_name = "Theme Customizer"
        verbose_name_plural = "Theme Customizer"

    def __str__(self):
        return f"Active theme: {self.get_theme_display()}"

    def save(self, *args, **kwargs):
        self.pk = 1
        if self.custom_accent:
            self.custom_accent = self.custom_accent.lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # The setting row is permanent; "deleting" resets to the original.
        self.theme, self.custom_accent = ORIGINAL, ""
        self.save()

    @classmethod
    def current(cls):
        """Read-only lookup used on every public request (no write)."""
        return cls.objects.filter(pk=1).first() or cls(theme=ORIGINAL)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def apply(self, slug, user=None):
        if slug not in THEMES:
            raise ValueError(f"Unknown theme: {slug}")
        if slug != self.theme:
            self.previous_theme = self.theme
            self.theme = slug
        self.updated_by = user
        self.save()
