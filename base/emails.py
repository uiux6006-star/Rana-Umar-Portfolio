"""Email notifications. A failed email never breaks the page: the message is
already saved in the database, so errors are only logged."""

import logging

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def _send(subject, body, to, reply_to=None):
    if not to:
        return
    try:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to,
            reply_to=[reply_to] if reply_to else None,
        ).send()
    except Exception:
        logger.exception("Could not send email: %s", subject)


def notify_new_contact(message):
    """Tell the site owner about a new enquiry, and thank the client."""

    owner_body = (
        f"New enquiry from your portfolio website\n"
        f"{'=' * 40}\n\n"
        f"Name:     {message.name}\n"
        f"Email:    {message.email}\n"
        f"Project:  {message.get_project_type_display() or '-'}\n"
        f"Budget:   {message.get_budget_display() or '-'}\n"
        f"Subject:  {message.subject}\n\n"
        f"{message.message}\n\n"
        f"Reply to this email to answer {message.name} directly."
    )
    _send(
        f"New enquiry: {message.subject}",
        owner_body,
        settings.NOTIFY_EMAILS,
        reply_to=message.email,
    )

    client_body = (
        f"Hi {message.name},\n\n"
        f"Thanks for getting in touch! I've received your message about "
        f"\"{message.subject}\" and will reply within 24 hours.\n\n"
        f"If it's urgent, you can also reach me on WhatsApp: {settings.OWNER_WHATSAPP}\n\n"
        f"Best regards,\n"
        f"{settings.OWNER_NAME}\n"
        f"Full Stack Developer"
    )
    _send(
        "Thanks for your message - I'll reply soon",
        client_body,
        [message.email],
        reply_to=settings.NOTIFY_EMAILS[0] if settings.NOTIFY_EMAILS else None,
    )


def notify_new_review(testimonial):
    body = (
        f"{testimonial.name} left a {testimonial.rating}-star review:\n\n"
        f"{testimonial.message}\n\n"
        f"It is hidden until you publish it in the admin panel (Testimonials)."
    )
    _send(f"New review from {testimonial.name}", body, settings.NOTIFY_EMAILS)
