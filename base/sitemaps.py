from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Post, Project


class StaticSitemap(Sitemap):
    changefreq = "monthly"

    def items(self):
        return ["home", "about", "projects", "services", "blog", "estimate", "contact"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "home" else 0.8


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.exclude(slug__isnull=True).exclude(slug="").order_by("-created_at")

    def lastmod(self, obj):
        return obj.created_at


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticSitemap,
    "projects": ProjectSitemap,
    "blog": PostSitemap,
}
