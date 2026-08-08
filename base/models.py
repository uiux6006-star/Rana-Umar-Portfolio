from django.db import models
from django.utils.text import slugify


# ================= CONTACT MODEL =================

class ContactMessage(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField()

    subject = models.CharField(max_length=200)

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

    # unique=True hata diya
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
        max_length=255
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
           return self.technologies.split(",")

    def __str__(self):
        return self.title