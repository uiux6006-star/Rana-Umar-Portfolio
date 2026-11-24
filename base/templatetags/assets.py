"""
{% vstatic 'css/home.css' %}  ->  /static/css/home.css?v=1732441234

Adds the file's last-modified time to CSS/JS links, so after a deploy every
visitor gets the new file instead of an old copy from their browser cache.
"""

import os
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


def _version(path):
    found = finders.find(path)
    if not found and settings.STATIC_ROOT:
        candidate = os.path.join(settings.STATIC_ROOT, path)
        found = candidate if os.path.exists(candidate) else None
    if not found:
        return ""
    try:
        return str(int(os.path.getmtime(found)))
    except OSError:
        return ""


_cached_version = lru_cache(maxsize=256)(_version)


@register.simple_tag
def vstatic(path):
    # In development files change all the time, so check every request
    version = _version(path) if settings.DEBUG else _cached_version(path)
    url = static(path)
    return f"{url}?v={version}" if version else url
