from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import ContactMessage, Project



# ================= HOME =================

def home(request):

    featured_projects = Project.objects.filter(
        featured=True
    ).order_by("-created_at")[:3]


    context = {
        "featured_projects": featured_projects
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

    if request.method == "POST":


        ContactMessage.objects.create(

            name=request.POST.get("name"),

            email=request.POST.get("email"),

            subject=request.POST.get("subject"),

            message=request.POST.get("message")

        )


        messages.success(
            request,
            "Your message has been sent successfully."
        )


        return redirect("contact")



    return render(
        request,
        "contact.html"
    )