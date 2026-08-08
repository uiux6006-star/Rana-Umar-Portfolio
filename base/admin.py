from django.contrib import admin
from .models import ContactMessage, Project


# ================= CONTACT ADMIN =================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "subject",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
    )

    list_filter = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )


# ================= PROJECT ADMIN =================


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "featured",
        "created_at",
    )


    list_editable = (
        "featured",
    )


    list_filter = (
        "category",
        "featured",
    )


    search_fields = (
        "title",
        "technologies",
    )


    prepopulated_fields = {
        "slug": ("title",)
    }


    readonly_fields = (
        "created_at",
    )


    ordering = (
        "-created_at",
    )
