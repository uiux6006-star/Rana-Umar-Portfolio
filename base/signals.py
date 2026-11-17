from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def apply_remember_me(sender, request, user, **kwargs):
    """Admin login page: without "Remember me", end the session when the
    browser closes. With it, keep Django's normal (2-week) session."""
    if request is None or request.method != "POST":
        return
    if not request.path.startswith("/admin/login"):
        return
    if not request.POST.get("remember_me"):
        request.session.set_expiry(0)
