import math

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# ================= CONTACT MODEL =================

class ContactMessage(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField()

    subject = models.CharField(max_length=200)

    PROJECT_TYPE_CHOICES = [
        ('business', 'Business / Brand Website'),
        ('ecommerce', 'Online Store (E-commerce)'),
        ('webapp', 'Custom Web App / Management System'),
        ('landing', 'Landing Page / Portfolio'),
        ('redesign', 'Website Redesign / Fix'),
        ('other', 'Something Else'),
    ]

    BUDGET_CHOICES = [
        ('unsure', 'Not sure yet'),
        ('under_25k', 'Under Rs 25,000'),
        ('25k_50k', 'Rs 25,000 - 50,000'),
        ('50k_100k', 'Rs 50,000 - 100,000'),
        ('100k_plus', 'Rs 100,000+'),
    ]

    project_type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, blank=True)

    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)

    message = models.TextField()

    STATUS_NEW = "new"
    STATUS_REPLIED = "replied"
    STATUS_WON = "won"
    STATUS_LOST = "lost"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REPLIED, "Replied"),
        (STATUS_WON, "Won (client)"),
        (STATUS_LOST, "Lost"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
    )

    notes = models.TextField(
        blank=True,
        help_text="Private notes: calls, quotes sent, follow-up dates. Only you can see this."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead / Enquiry"
        verbose_name_plural = "Leads / Enquiries"

    def __str__(self):
        return f"{self.name} - {self.subject}"


# ================= PROJECT MODEL =================

class Project(models.Model):

    CATEGORY_CHOICES = [
        ('python', 'Python'),
        ('django', 'Django'),
        ('frontend', 'Frontend'),
    ]

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        blank=True,
        null=True
    )

    description = models.TextField()

    image = models.ImageField(
        upload_to='projects/',
        blank=False,
        null=False
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    technologies = models.CharField(
        max_length=255,
        help_text="Comma separated, e.g. Python, Django, Bootstrap"
    )

    github_link = models.URLField(
        blank=True
    )

    live_demo = models.URLField(
        blank=True
    )

    featured = models.BooleanField(
        default=False
    )

    # ----- Case study (all optional; sections only show when filled) -----

    client = models.CharField(
        max_length=150,
        blank=True,
        help_text="e.g. Royal Stitch (Lahore)"
    )

    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g. 3 weeks"
    )

    problem = models.TextField(
        blank=True,
        help_text="What problem did the client have?"
    )

    solution = models.TextField(
        blank=True,
        help_text="What did you build and how did it solve the problem?"
    )

    result = models.TextField(
        blank=True,
        help_text="What changed after launch? Numbers work best."
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])

    @property
    def has_case_study(self):
        return bool(self.problem or self.solution or self.result)

    @property
    def tech_list(self):
        separator = "," if "," in self.technologies else None
        return [tech.strip() for tech in self.technologies.split(separator) if tech.strip()]

    def __str__(self):
        return self.title


# ================= PROJECT GALLERY =================

class ProjectImage(models.Model):

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="gallery"
    )

    image = models.ImageField(upload_to="projects/gallery/")

    caption = models.CharField(max_length=200, blank=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"{self.project.title} image"


# ================= BLOG POST =================

class Post(models.Model):

    title = models.CharField(max_length=200)

    slug = models.SlugField(max_length=220, unique=True, blank=True)

    excerpt = models.CharField(
        max_length=300,
        help_text="1-2 lines shown on the blog list and in Google results."
    )

    cover_image = models.ImageField(upload_to="blog/", blank=True)

    body = models.TextField(
        help_text="Leave an empty line between paragraphs."
    )

    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma separated, e.g. Django, SEO, Tips"
    )

    is_published = models.BooleanField(default=False)

    published_at = models.DateTimeField(default=timezone.now)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at"]

    def save(self, *args, **kwargs):

        if not self.slug:
            base = slugify(self.title)[:200] or "post"
            slug = base
            n = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("post_detail", args=[self.slug])

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @property
    def reading_time(self):
        return max(1, math.ceil(len(self.body.split()) / 200))

    def __str__(self):
        return self.title


# ================= TESTIMONIAL MODEL =================

class Testimonial(models.Model):

    name = models.CharField(max_length=100)

    role = models.CharField(
        max_length=150,
        blank=True,
        help_text="e.g. Owner, Royal Stitch"
    )

    message = models.TextField()

    rating = models.PositiveSmallIntegerField(
        default=5,
        choices=[(i, i) for i in range(1, 6)]
    )

    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rating}/5)"
