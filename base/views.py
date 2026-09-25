from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import ContactForm
from .models import Project, Testimonial



# ================= HOME =================

def home(request):

    featured_projects = Project.objects.filter(
        featured=True
    ).order_by("-created_at")[:3]


    context = {
        "featured_projects": featured_projects,
        "project_count": Project.objects.count(),
        "testimonials": Testimonial.objects.filter(is_published=True)[:6],
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
        "about.html"
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
        Project,
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

    form = ContactForm(request.POST or None)

    if request.method == "POST" and form.is_valid():

        # Bots get the same success message, but nothing is saved.
        if not form.is_spam():
            form.save()

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
