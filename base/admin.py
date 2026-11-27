from django import forms as dj_forms
from django.contrib import admin, messages
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.timesince import timesince

from . import profile, tiktok
from .models import ContactMessage, Post, Project, ProjectImage, Testimonial, TikTokVideo


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
        "kind",
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
                "title", "slug", "category", "kind", "description",
                "cover_preview", "image",
                "technologies", "github_link", "live_demo", "featured",
            ),
        }),
        ("Case study", {
            "description": "Optional. Each part only shows on the project page when it's filled in.",
            "fields": ("client", "duration", "problem", "solution", "features", "challenges", "result"),
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


# ================= TIKTOK VIDEOS =================

class TikTokVideoForm(dj_forms.ModelForm):

    class Meta:
        model = TikTokVideo
        fields = ("url", "title", "thumbnail", "order", "is_published")

    def clean_url(self):
        url = self.cleaned_data["url"].strip()
        if not tiktok.is_tiktok_url(url):
            raise dj_forms.ValidationError("Please paste a TikTok link (https://www.tiktok.com/...).")
        if not tiktok.video_id_from_url(url):
            url = tiktok.resolve(url)  # short links like vt.tiktok.com/...
        if not tiktok.video_id_from_url(url):
            raise dj_forms.ValidationError(
                "This doesn't look like a video link. Open the video in a browser and copy the address, "
                "it should contain /video/ followed by numbers."
            )
        return url


@admin.register(TikTokVideo)
class TikTokVideoAdmin(admin.ModelAdmin):

    form = TikTokVideoForm
    list_display = ("preview", "title_or_link", "order", "is_published", "created_at")
    list_display_links = ("preview", "title_or_link")
    list_editable = ("order", "is_published")
    readonly_fields = ("thumbnail_preview",)
    fields = ("url", "title", "thumbnail_preview", "thumbnail", "order", "is_published")

    change_list_template = "admin/base/tiktokvideo/change_list.html"

    def get_urls(self):
        from django.urls import path
        return [
            path("import-latest/", self.admin_site.admin_view(self.import_latest), name="base_tiktokvideo_import"),
        ] + super().get_urls()

    def import_latest(self, request):
        """Adds the newest videos from the TikTok profile that aren't on the site yet."""
        from django.shortcuts import redirect

        changelist = reverse("admin:base_tiktokvideo_changelist")
        if request.method != "POST" or not self.has_add_permission(request):
            return redirect(changelist)

        username = tiktok.username_from_url(profile.TIKTOK_URL)
        videos = tiktok.creator_videos(username)
        if not videos:
            self.message_user(request, "Couldn't reach TikTok right now. Try again later, or add a video by pasting its link.", messages.WARNING)
            return redirect(changelist)

        existing = set(TikTokVideo.objects.values_list("video_id", flat=True))
        added = 0
        for v in videos[:4]:
            if v["id"] in existing:
                continue
            video = TikTokVideo(
                url=f"https://www.tiktok.com/@{username}/video/{v['id']}",
                video_id=v["id"],
                title=v["title"][:200],
                order=TikTokVideo.objects.count(),
            )
            image = tiktok.download_image(v["cover"])
            if image:
                video.thumbnail.save(f"{v['id']}.jpg", ContentFile(image), save=False)
            video.save()
            added += 1

        if added:
            self.message_user(request, f"Added {added} new video{'s' if added != 1 else ''} from TikTok.", messages.SUCCESS)
        else:
            self.message_user(request, "Your latest TikTok videos are already on the site.", messages.INFO)
        return redirect(changelist)

    @admin.display(description="")
    def preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" alt="" style="width:44px;height:58px;object-fit:cover;border-radius:6px">', obj.thumbnail.url)
        return "—"

    @admin.display(description="Video")
    def title_or_link(self, obj):
        return obj.title or obj.url

    @admin.display(description="Current thumbnail")
    def thumbnail_preview(self, obj):
        if obj and obj.thumbnail:
            return format_html('<img src="{}" alt="" style="max-width:160px;border-radius:10px">', obj.thumbnail.url)
        return "Fetched from TikTok when you save."

    def save_model(self, request, obj, form, change):
        obj.video_id = tiktok.video_id_from_url(obj.url)

        if not obj.title or not obj.thumbnail:
            details = tiktok.fetch_details(obj.url, tiktok.username_from_url(profile.TIKTOK_URL))
            if details is None:
                self.message_user(
                    request,
                    "Saved, but TikTok couldn't be reached to fetch the title and thumbnail. "
                    "You can type a title and upload a thumbnail yourself.",
                    messages.WARNING,
                )
            else:
                obj.video_id = details["video_id"] or obj.video_id
                if not obj.title and details["title"]:
                    obj.title = details["title"][:200]
                if not obj.thumbnail:
                    image = tiktok.download_image(details["thumbnail_url"])
                    if image:
                        obj.thumbnail.save(f"{obj.video_id or 'video'}.jpg", ContentFile(image), save=False)
                    else:
                        self.message_user(request, "Saved, but the thumbnail couldn't be downloaded. You can upload one yourself.", messages.WARNING)

        super().save_model(request, obj, form, change)
