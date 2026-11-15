"""
Website assistant ("RUD Assistant"): a free, rule-based FAQ chatbot.

- `knowledge` gives the browser everything the bot may say, built from the
  site's own data (projects, estimator prices, FAQs), so answers never drift
  from what the website shows.
- `lead` saves a visitor's details as a normal Lead / Enquiry and sends the
  usual email notifications.
"""

import json
import time

from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET, require_POST

from .emails import notify_new_contact
from .forms import ContactForm
from .models import ContactMessage, Project
from .views import ESTIMATOR_PRICES

WHATSAPP_NUMBER = "923238144826"
CONTACT_EMAIL = "uiux6006@gmail.com"

SERVICES = [
    {"name": "Business websites", "text": "Fast, modern sites that make your brand look professional and bring in enquiries."},
    {"name": "Online stores", "text": "E-commerce with products, cart and checkout, plus JazzCash / Easypaisa / card payments."},
    {"name": "Custom web apps", "text": "Management systems, dashboards and portals built with Python and Django."},
    {"name": "Landing pages & portfolios", "text": "One-page sites built to turn visitors into leads."},
    {"name": "UI/UX design", "text": "Clean, modern interfaces designed around your customers."},
    {"name": "Redesign & fixes", "text": "Make an old or slow website modern, fast and mobile-friendly."},
]

PROCESS = [
    {"name": "Planning", "text": "We talk about your goals, pages and features. You get a clear quote."},
    {"name": "Design", "text": "I design the look and layout and share it with you for feedback."},
    {"name": "Development", "text": "I build it with regular progress updates so you see it come to life."},
    {"name": "Deployment", "text": "I put it live, test it on all devices, and stay available for support."},
]

FAQS = {
    "mobile": "Yes. Every site I build is fully responsive and tested on phones, tablets and desktops.",
    "admin": "Yes. For dynamic sites I include an easy admin panel, so you can change text, images and products yourself.",
    "support": "Yes. I help you get the site live and I'm available for questions, fixes and future updates.",
    "timeline": "A simple business website is much quicker than a custom web app. After our first discussion I'll give you a realistic timeline and keep you updated throughout.",
    "cost": "It depends on what you need: pages, features and design. Share your idea and I'll send you a clear quote with no hidden charges.",
}

MAX_LEADS_PER_HOUR = 3


@require_GET
@cache_control(max_age=300, public=True)
def knowledge(request):
    projects = [
        {
            "title": p.title,
            "url": p.get_absolute_url(),
            "category": p.get_category_display(),
            "tech": p.tech_list[:4],
            "live": p.live_demo or "",
        }
        for p in Project.objects.order_by("-featured", "-created_at")[:6]
        if p.slug
    ]

    prices = [
        {"id": t["id"], "label": t["label"], "from": t["base"], "days": t["days"]}
        for t in ESTIMATOR_PRICES["types"]
    ]

    return JsonResponse({
        "owner": settings.OWNER_NAME,
        "whatsapp": f"https://wa.me/{WHATSAPP_NUMBER}",
        "email": CONTACT_EMAIL,
        "location": "Faisalabad, Pakistan",
        "urls": {
            "estimate": reverse("estimate"),
            "projects": reverse("projects"),
            "services": reverse("services"),
            "contact": reverse("contact"),
            "about": reverse("about"),
            "cv": settings.STATIC_URL + "cv/Rana_Umar_CV.pdf",
        },
        "services": SERVICES,
        "process": PROCESS,
        "faqs": FAQS,
        "prices": prices,
        "features": [{"label": f["label"], "price": f["price"]} for f in ESTIMATOR_PRICES["features"]],
        "projects": projects,
        "project_count": Project.objects.count(),
        "tech": ["Python", "Django", "JavaScript", "HTML5", "CSS3", "Bootstrap", "Three.js", "SQL"],
    })


@require_POST
def lead(request):
    try:
        data = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"ok": False, "errors": {"__all__": ["Invalid request."]}}, status=400)

    # Light rate limit per visitor session.
    now = time.time()
    recent = [t for t in request.session.get("chat_leads", []) if now - t < 3600]
    if len(recent) >= MAX_LEADS_PER_HOUR:
        return JsonResponse({"ok": False, "errors": {"__all__": ["Thanks, I already have your details. I'll be in touch soon!"]}}, status=429)

    project_type = data.get("project_type", "")
    if project_type not in dict(ContactMessage.PROJECT_TYPE_CHOICES):
        project_type = ""

    message = str(data.get("message", "")).strip()[:2000]

    form = ContactForm({
        "name": str(data.get("name", "")).strip()[:100],
        "email": str(data.get("email", "")).strip()[:254],
        "project_type": project_type,
        "budget": "",
        "subject": "Chatbot enquiry" + (f": {dict(ContactMessage.PROJECT_TYPE_CHOICES)[project_type]}" if project_type else ""),
        "message": message or "(Left details through the website chat, no message.)",
        "website": data.get("website", ""),   # honeypot
    })

    if not form.is_valid():
        errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    if not form.is_spam():
        enquiry = form.save(commit=False)
        enquiry.notes = "Captured by the website chat assistant."
        enquiry.save()
        notify_new_contact(enquiry)

    recent.append(now)
    request.session["chat_leads"] = recent

    return JsonResponse({"ok": True})
