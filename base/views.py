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

    projects = Project.objects.all().order_by("-created_at")


    return render(
        request,
        "projects.html",
        {
            "projects": projects
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

def services(request):

    return render(
        request,
        "services.html"
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

    return render(
        request,
        "estimate.html",
        {
            "prices": ESTIMATOR_PRICES,
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

    posts = Post.objects.filter(is_published=True)

    tag = request.GET.get("tag", "").strip()
    if tag:
        posts = posts.filter(tags__icontains=tag)

    page = Paginator(posts, 9).get_page(request.GET.get("page"))

    return render(
        request,
        "blog.html",
        {
            "page": page,
            "tag": tag,
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
