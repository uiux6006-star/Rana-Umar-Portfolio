from django.db import models


class PageView(models.Model):
    """One page view on the public site.

    Privacy: no IP address and no cookie is stored. `visitor` is a one-way
    hash of (secret, date, IP, browser) that changes every day, so it can
    count unique visitors per day but can't identify or follow anyone.
    """

    DEVICE_CHOICES = [
        ("desktop", "Desktop"),
        ("mobile", "Mobile"),
        ("tablet", "Tablet"),
    ]

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    day = models.DateField(db_index=True)
    path = models.CharField(max_length=255)
    visitor = models.CharField(max_length=16, db_index=True)
    source = models.CharField(
        max_length=60, blank=True,
        help_text="Where the visit came from, e.g. Google, LinkedIn. Empty for clicks inside the site.",
    )
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES, default="desktop")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Page view"
        verbose_name_plural = "Page views"

    def __str__(self):
        return f"{self.path} · {self.created_at:%Y-%m-%d %H:%M}"
