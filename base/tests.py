from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, Project, Testimonial


class PageTests(TestCase):

    def test_main_pages_load(self):
        for name in ["home", "about", "projects", "services", "contact"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_testimonials_section_only_shows_published(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "What Clients")

        Testimonial.objects.create(name="Ali", message="Great work", is_published=False)
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "What Clients")

        Testimonial.objects.create(name="Sara", message="Excellent website")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Excellent website")
        self.assertNotContains(response, "Great work")


class ProjectTests(TestCase):

    def test_tech_list_supports_commas_and_spaces(self):
        project = Project(technologies="Python, File Handling, OOP")
        self.assertEqual(project.tech_list, ["Python", "File Handling", "OOP"])

        project.technologies = "HTML CSS"
        self.assertEqual(project.tech_list, ["HTML", "CSS"])


class ContactFormTests(TestCase):

    def valid_data(self, **extra):
        data = {
            "name": "Client",
            "email": "client@example.com",
            "project_type": "ecommerce",
            "budget": "25k_50k",
            "subject": "Online store",
            "message": "I need an online store.",
            "website": "",
        }
        data.update(extra)
        return data

    def test_valid_message_is_saved(self):
        response = self.client.post(reverse("contact"), self.valid_data())
        self.assertRedirects(response, reverse("contact"))

        message = ContactMessage.objects.get()
        self.assertEqual(message.project_type, "ecommerce")
        self.assertEqual(message.budget, "25k_50k")

    def test_project_type_and_budget_are_optional(self):
        self.client.post(reverse("contact"), self.valid_data(project_type="", budget=""))
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_invalid_email_shows_error(self):
        response = self.client.post(reverse("contact"), self.valid_data(email="not-an-email"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please check the highlighted fields")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_blocks_bots(self):
        response = self.client.post(reverse("contact"), self.valid_data(website="http://spam.example"))
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)
