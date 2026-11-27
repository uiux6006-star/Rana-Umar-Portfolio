import logging

from django.utils import timezone

from .tracking import device_of, should_track, source_of, visitor_id

log = logging.getLogger(__name__)


class PageViewMiddleware:
    """Records public page views. Never lets analytics break a page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            if should_track(request, response):
                from .models import PageView

                today = timezone.localdate()
                PageView.objects.create(
                    day=today,
                    path=request.path[:255],
                    visitor=visitor_id(request, today),
                    source=source_of(request),
                    device=device_of(request.headers.get("User-Agent", "")),
                )
        except Exception:  # analytics must never take the site down
            log.exception("Could not record page view")
        return response
