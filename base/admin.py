from django.contrib import admin
from .models import ContactMessage, Project, Testimonial


# ================= CONTACT ADMIN =================

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "email",
        "project_type",
        "budget",
        "subject",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
    )

    list_filter = (
        "project_type",
        "budget",
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


# ================= TESTIMONIAL ADMIN =================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "role",
        "rating",
        "is_published",
        "created_at",
    )

    list_editable = (
        "is_published",
    )
