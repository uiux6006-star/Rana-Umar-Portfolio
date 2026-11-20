from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_GET

from .emails import notify_new_contact, notify_new_review
from .forms import ContactForm, TestimonialForm
from .models import ContactMessage, Post, Project, Testimonial



# ================= HOME =================

def home(request):

    featured_projects = Project.objects.filter(
        featured=True
    ).order_by("-created_at")[:3]


    context = {
        "featured_projects": featured_projects,
        "project_count": Project.objects.count(),
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
        "latest_posts": Post.objects.filter(is_published=True)[:3],
        # "from Rs ..." on the service cards, kept in sync with the estimator
        "start_prices": {t["id"]: t["base"] for t in ESTIMATOR_PRICES["types"]},
    }


    return render(
        request,
        "index.html",
        context
    )



# ================= ABOUT =================

def about(request):

    return render(
        request,
        "about.html",
        {
            "project_count": Project.objects.count(),
        }
    )



# ================= PROJECTS =================

def projects(request):

    projects = list(Project.objects.all().order_by("-created_at"))

    # Filter tabs with a live count, only for categories that have projects
    categories = [
        {"value": value, "label": label, "count": sum(p.category == value for p in projects)}
        for value, label in Project.CATEGORY_CHOICES
    ]
    categories = [c for c in categories if c["count"]]


    return render(
        request,
        "projects.html",
        {
            "projects": projects,
            "categories": categories,
            "live_count": sum(bool(p.live_demo) for p in projects),
            "tech_count": len({t.lower() for p in projects for t in p.tech_list}),
        }
    )



# ================= PROJECT DETAIL =================

def project_detail(request, slug):

    project = get_object_or_404(
        Project.objects.prefetch_related("gallery"),
        slug=slug
    )


    related_projects = Project.objects.filter(
        category=project.category
    ).exclude(
        id=project.id
    )[:3]


    return render(
        request,
        "project_detail.html",
        {
            "project": project,
            "related_projects": related_projects
        }
    )



# ================= SERVICES =================

# What each package includes on the Services page. Prices, pages and days
# come from ESTIMATOR_PRICES so every page shows the same numbers.
SERVICE_DETAILS = {
    "landing": {
        "pitch": "One focused page that turns visitors into enquiries, fast.",
        "includes": ["Single high-converting page", "Contact form & WhatsApp button", "Mobile-first design", "Fast loading"],
    },
    "business": {
        "pitch": "A professional website that builds trust and brings in enquiries.",
        "includes": ["Home, About, Services, Contact & more", "Responsive on every device", "Contact form with email alerts", "Google Maps & social links"],
        "popular": True,
    },
    "ecommerce": {
        "pitch": "Sell online with a store your customers enjoy using.",
        "includes": ["Product catalogue & categories", "Cart, checkout & order emails", "Admin panel to manage stock", "JazzCash, Easypaisa & card (add-on)"],
    },
    "webapp": {
        "pitch": "Management systems built around how your business really works.",
        "includes": ["Built with Python & Django", "Secure logins & user roles", "Dashboards & reports", "Admin panel for your team"],
    },
}

ADDON_ICONS = {
    "admin": "fa-sliders", "blog": "fa-pen-nib", "payment": "fa-credit-card",
    "booking": "fa-calendar-check", "seo": "fa-magnifying-glass-chart",
    "multilang": "fa-language", "whatsapp": "fa-whatsapp", "hosting": "fa-globe",
}


def services(request):

    packages = [
        {**t, **SERVICE_DETAILS.get(t["id"], {})}
        for t in ESTIMATOR_PRICES["types"]
    ]

    addons = [
        {**f, "icon": ADDON_ICONS.get(f["id"], "fa-plus"), "brand": f["id"] == "whatsapp"}
        for f in ESTIMATOR_PRICES["features"]
    ]

    return render(
        request,
        "services.html",
        {
            "packages": packages,
            "addons": addons,
            "hero_package": next((p for p in packages if p.get("popular")), packages[0]),
        }
    )



# ================= CONTACT =================

def contact(request):

    if request.method == "POST":
        form = ContactForm(request.POST)
    else:
        # The price estimator links here with the client's choices filled in.
        form = ContactForm(initial=_contact_prefill(request.GET))

    if request.method == "POST" and form.is_valid():

        # Bots get the same success message, but nothing is saved.
        if not form.is_spam():
            message = form.save()
            notify_new_contact(message)

        messages.success(
            request,
            "Thanks! Your message has been sent. I'll get back to you as soon as possible."
        )

        return redirect("contact")

    return render(
        request,
        "contact.html",
        {
            "form": form
        }
    )


def _contact_prefill(params):
    initial = {}

    if params.get("type") in dict(ContactMessage.PROJECT_TYPE_CHOICES):
        initial["project_type"] = params["type"]

    if params.get("budget") in dict(ContactMessage.BUDGET_CHOICES):
        initial["budget"] = params["budget"]

    if params.get("subject"):
        initial["subject"] = params["subject"][:200]

    if params.get("message"):
        initial["message"] = params["message"][:2000]

    return initial



# ================= PRICE ESTIMATOR =================
# Prices in PKR. Edit these numbers to match your own rates.

ESTIMATOR_PRICES = {
    "types": [
        {"id": "landing", "label": "Landing Page / Portfolio", "icon": "fa-rocket", "base": 15000, "pages": 1, "days": 5},
        {"id": "business", "label": "Business / Brand Website", "icon": "fa-briefcase", "base": 30000, "pages": 5, "days": 10},
        {"id": "ecommerce", "label": "Online Store (E-commerce)", "icon": "fa-cart-shopping", "base": 70000, "pages": 8, "days": 21},
        {"id": "webapp", "label": "Custom Web App / System", "icon": "fa-gears", "base": 90000, "pages": 6, "days": 30},
    ],
    "extra_page": 3000,
    "features": [
        {"id": "admin", "label": "Admin panel (edit content yourself)", "price": 15000, "days": 4},
        {"id": "blog", "label": "Blog / News section", "price": 10000, "days": 3},
        {"id": "payment", "label": "Online payments (JazzCash, Easypaisa, card)", "price": 15000, "days": 4},
        {"id": "booking", "label": "Appointment / booking system", "price": 12000, "days": 4},
        {"id": "seo", "label": "SEO setup (Google ranking basics)", "price": 8000, "days": 2},
        {"id": "multilang", "label": "English + Urdu (two languages)", "price": 12000, "days": 4},
        {"id": "whatsapp", "label": "WhatsApp chat & order button", "price": 3000, "days": 1},
        {"id": "hosting", "label": "Domain + hosting setup", "price": 5000, "days": 1},
    ],
    "designs": [
        {"id": "clean", "label": "Clean & simple", "multiplier": 1.0},
        {"id": "custom", "label": "Premium custom design", "multiplier": 1.3},
    ],
    "rush_multiplier": 1.25,
}


def estimate(request):

    # ?type=ecommerce pre-selects that package (used by the Services page)
    type_ids = [t["id"] for t in ESTIMATOR_PRICES["types"]]
    selected = request.GET.get("type")
    if selected not in type_ids:
        selected = type_ids[1]

    return render(
        request,
        "estimate.html",
        {
            "prices": ESTIMATOR_PRICES,
            "selected_type": selected,
        }
    )



# ================= REVIEWS =================

def leave_review(request):

    form = TestimonialForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        if not form.is_spam():
            review = form.save(commit=False)
            review.is_published = False  # you approve it in the admin first
            review.save()
            notify_new_review(review)

        messages.success(
            request,
            "Thank you for your review! It will appear on the website after a quick check."
        )

        return redirect("leave_review")

    return render(
        request,
        "review.html",
        {
            "form": form
        }
    )



# ================= BLOG =================

def blog(request):

    published = Post.objects.filter(is_published=True)

    # Topic chips: every tag used on a published post, most used first
    counts = {}
    for tags in published.values_list("tags", flat=True):
        for name in {t.strip() for t in tags.split(",") if t.strip()}:
            key = name.lower()
            label, n = counts.get(key, (name, 0))
            # Prefer the properly capitalised spelling ("SEO" over "seo")
            if label.islower() and not name.islower():
                label = name
            counts[key] = (label, n + 1)
    all_tags = sorted(counts.values(), key=lambda item: (-item[1], item[0].lower()))

    posts = published
    tag = request.GET.get("tag", "").strip()
    if tag:
        posts = posts.filter(tags__icontains=tag)

    page = Paginator(posts, 9).get_page(request.GET.get("page"))

    # The newest post gets the big card on the first, unfiltered page
    items = list(page.object_list)
    featured = items[0] if page.number == 1 and not tag and items else None
    rest = items[1:] if featured else items

    return render(
        request,
        "blog.html",
        {
            "page": page,
            "tag": tag,
            "featured": featured,
            "posts": rest,
            "all_tags": [{"name": name, "count": n} for name, n in all_tags],
            "post_count": published.count(),
        }
    )


def post_detail(request, slug):

    post = get_object_or_404(Post, slug=slug, is_published=True)

    more_posts = Post.objects.filter(is_published=True).exclude(pk=post.pk)[:3]

    return render(
        request,
        "post_detail.html",
        {
            "post": post,
            "more_posts": more_posts,
        }
    )



# ================= ROBOTS.TXT =================

@require_GET
def robots_txt(request):

    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]

    return HttpResponse("\n".join(lines), content_type="text/plain")
