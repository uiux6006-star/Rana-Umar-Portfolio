from django.db import models
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

    created_at = models.DateTimeField(auto_now_add=True)

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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    @property
    def tech_list(self):
        separator = "," if "," in self.technologies else None
        return [tech.strip() for tech in self.technologies.split(separator) if tech.strip()]

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
