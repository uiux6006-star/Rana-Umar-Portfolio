from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.timesince import timesince

from .models import ContactMessage, Post, Project, ProjectImage, Testimonial


admin.site.site_header = "RANA UMAR"
admin.site.site_title = "Rana Umar · Studio"
admin.site.index_title = "Dashboard"


def badge(text, kind):
    return format_html('<span class="rd-status rd-status-{}">{}</span>', kind, text)


# ================= LEADS (CONTACT MESSAGES) =================

def _set_status(status, label):

    @admin.action(description=f"Mark selected as {label}")
    def action(modeladmin, request, queryset):
        updated = queryset.update(status=status)
        modeladmin.message_user(request, f"{updated} lead(s) marked as {label}.", messages.SUCCESS)

    action.__name__ = f"mark_{status}"
    return action


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):

    list_display = (
        "lead",
        "project_type",
        "budget",
        "status",
        "received",
    )

    list_display_links = ("lead",)

    list_editable = ("status",)

    list_filter = (
        "status",
        "project_type",
        "budget",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "subject",
        "message",
        "notes",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    readonly_fields = (
        "name",
        "email",
        "project_type",
        "budget",
        "subject",
        "message",
        "created_at",
        "reply_buttons",
    )

    fieldsets = (
        ("Client", {
            "fields": ("name", "email", "reply_buttons", "created_at"),
        }),
        ("Project request", {
            "fields": ("project_type", "budget", "subject", "message"),
        }),
        ("Your follow-up", {
            "fields": ("status", "notes"),
        }),
    )

    actions = [
        _set_status(ContactMessage.STATUS_REPLIED, "Replied"),
        _set_status(ContactMessage.STATUS_WON, "Won"),
        _set_status(ContactMessage.STATUS_LOST, "Lost"),
    ]

    def has_add_permission(self, request):
        # Leads only come from the website's contact form.
        return False

    @admin.display(description="Lead", ordering="name")
    def lead(self, obj):
        return format_html(
            '<span class="rd-client"><span class="rd-avatar">{}</span>'
            '<span><strong>{}</strong><small>{}</small></span></span>',
            obj.name[:1].upper(),
            obj.name,
            obj.subject,
        )

    @admin.display(description="Received", ordering="created_at")
    def received(self, obj):
        return format_html(
            '<span title="{}">{} ago</span>',
            obj.created_at.strftime("%d %b %Y, %H:%M"),
            timesince(obj.created_at).split(",")[0],
        )

    @admin.display(description="Reply")
    def reply_buttons(self, obj):
        if not obj.pk:
            return "-"
        mail = "mailto:{}?{}".format(
            obj.email,
            urlencode({"subject": f"Re: {obj.subject}", "body": f"Hi {obj.name},\n\n"}).replace("+", "%20"),
        )
        return format_html(
            '<a class="btn btn-primary btn-sm me-2" href="{}"><i class="fas fa-reply me-1"></i> Reply by email</a>'
            '<span class="rd-muted">{}</span>',
            mail,
            obj.email,
        )


# ================= PROJECTS =================

class ProjectImageInline(admin.TabularInline):

    model = ProjectImage
    extra = 1
    fields = ("preview", "image", "caption", "order")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" class="rd-thumb" alt="">', obj.image.url)
        return "-"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "thumbnail",
        "title",
        "category",
        "case_study",
        "featured",
        "created_at",
    )

    list_display_links = ("thumbnail", "title")

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
        "client",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = (
        "created_at",
        "cover_preview",
        "view_on_site_link",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        ("Project", {
            "fields": (
                "title", "slug", "category", "description",
                "cover_preview", "image",
                "technologies", "github_link", "live_demo", "featured",
            ),
        }),
        ("Case study", {
            "description": "Optional. Each part only shows on the project page when it's filled in.",
            "fields": ("client", "duration", "problem", "solution", "result"),
        }),
        ("Info", {
            "fields": ("view_on_site_link", "created_at"),
        }),
    )

    inlines = [ProjectImageInline]

    @admin.display(description="")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="rd-thumb" alt="">', obj.image.url)
        return ""

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" class="rd-cover" alt="">', obj.image.url)
        return "Upload an image below."

    @admin.display(description="Case study", boolean=True)
    def case_study(self, obj):
        return obj.has_case_study

    @admin.display(description="Public page")
    def view_on_site_link(self, obj):
        if obj.pk and obj.slug:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">Open on website <i class="fas fa-arrow-up-right-from-square"></i></a>',
                obj.get_absolute_url(),
            )
        return "-"


# ================= BLOG =================

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = ("title", "state", "is_published", "reading", "published_at")
    list_editable = ("is_published",)
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "excerpt", "body", "tags")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"

    fieldsets = (
        (None, {"fields": ("title", "slug", "excerpt", "body")}),
        ("Publishing", {"fields": ("cover_image", "tags", "is_published", "published_at")}),
    )

    @admin.display(description="State", ordering="is_published")
    def state(self, obj):
        return badge("Live", "won") if obj.is_published else badge("Draft", "replied")

    @admin.display(description="Read time")
    def reading(self, obj):
        return f"{obj.reading_time} min"


# ================= TESTIMONIALS =================

@admin.action(description="Publish selected reviews")
def publish_reviews(modeladmin, request, queryset):
    updated = queryset.update(is_published=True)
    modeladmin.message_user(request, f"{updated} review(s) published.", messages.SUCCESS)


@admin.action(description="Hide selected reviews")
def hide_reviews(modeladmin, request, queryset):
    updated = queryset.update(is_published=False)
    modeladmin.message_user(request, f"{updated} review(s) hidden.", messages.SUCCESS)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "role",
        "stars",
        "short_message",
        "is_published",
        "created_at",
    )

    list_editable = (
        "is_published",
    )

    list_filter = (
        "is_published",
        "rating",
    )

    search_fields = ("name", "role", "message")

    actions = [publish_reviews, hide_reviews]

    @admin.display(description="Rating", ordering="rating")
    def stars(self, obj):
        return format_html(
            '<span class="rd-stars" title="{} out of 5">{}<span class="rd-stars-off">{}</span></span>',
            obj.rating,
            "★" * obj.rating,
            "★" * (5 - obj.rating),
        )

    @admin.display(description="Review")
    def short_message(self, obj):
        return obj.message if len(obj.message) <= 70 else obj.message[:70] + "…"
