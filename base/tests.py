from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage, Post, Project, Testimonial


class PageTests(TestCase):

    def test_main_pages_load(self):
        for name in ["home", "about", "projects", "services", "contact", "blog", "estimate", "leave_review"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_site_chrome_is_on_every_page(self):
        for name in ["home", "about", "projects", "contact"]:
            response = self.client.get(reverse(name))
            with self.subTest(page=name):
                self.assertContains(response, 'id="loader"')
                self.assertContains(response, 'id="siteNav"')
                self.assertContains(response, 'id="snMenu"')
                self.assertContains(response, 'class="site-footer"')

    def test_about_project_count_follows_database(self):
        for i in range(3):
            Project.objects.create(title=f"P{i}", description="d", image="projects/x.jpg",
                                   category="django", technologies="Django")
        # Data migrations also add projects, so compare with the real count.
        expected = f"{Project.objects.count():02d}+"
        response = self.client.get(reverse("about"))
        self.assertContains(response, expected)

    def test_about_page_has_one_h1(self):
        html = self.client.get(reverse("about")).content.decode()
        self.assertEqual(html.count("<h1"), 1)

    def test_current_page_is_marked_in_navbar(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, 'class="sn-link is-active" aria-current="page">About</a>', html=False)
        self.assertNotContains(response, 'class="sn-link is-active" aria-current="page">Home</a>', html=False)

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
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(NOTIFY_EMAILS=["owner@example.com"])
    def test_new_message_emails_owner_and_client(self):
        self.client.post(reverse("contact"), self.valid_data())

        self.assertEqual(len(mail.outbox), 2)
        owner, client = mail.outbox
        self.assertEqual(owner.to, ["owner@example.com"])
        self.assertEqual(owner.reply_to, ["client@example.com"])
        self.assertIn("Online Store", owner.body)
        self.assertEqual(client.to, ["client@example.com"])

    def test_estimator_prefills_contact_form(self):
        response = self.client.get(reverse("contact"), {
            "type": "ecommerce",
            "budget": "50k_100k",
            "subject": "Quote for store",
            "message": "Estimate details",
        })
        form = response.context["form"]
        self.assertEqual(form.initial["project_type"], "ecommerce")
        self.assertEqual(form.initial["budget"], "50k_100k")
        self.assertContains(response, "Estimate details")

    def test_estimator_prefill_selects_the_right_chips(self):
        response = self.client.get(reverse("contact"), {"type": "ecommerce", "budget": "50k_100k"})
        self.assertContains(response, 'name="project_type" value="ecommerce" checked', html=False)
        self.assertContains(response, 'name="budget" value="50k_100k" checked', html=False)
        self.assertNotContains(response, 'name="project_type" value="business" checked', html=False)

    def test_failed_submit_keeps_what_the_visitor_typed(self):
        response = self.client.post(reverse("contact"), self.valid_data(email="nope", subject="My shop", project_type="webapp"))
        self.assertContains(response, 'value="My shop"', html=False)
        self.assertContains(response, 'name="project_type" value="webapp" checked', html=False)
        self.assertContains(response, "has-error")

    def test_success_shows_confirmation_card(self):
        response = self.client.post(reverse("contact"), self.valid_data(), follow=True)
        self.assertContains(response, "Message sent!")
        self.assertNotContains(response, 'id="ctForm"')

    def test_prefill_ignores_unknown_choices(self):
        response = self.client.get(reverse("contact"), {"type": "hack", "budget": "lots"})
        self.assertEqual(response.context["form"].initial, {})


class ReviewTests(TestCase):

    @override_settings(NOTIFY_EMAILS=["owner@example.com"])
    def test_submitted_review_is_hidden_until_approved(self):
        response = self.client.post(reverse("leave_review"), {
            "name": "Ahmed",
            "role": "Owner, Shop",
            "rating": 5,
            "message": "Superb website",
            "website": "",
        })
        self.assertRedirects(response, reverse("leave_review"))

        review = Testimonial.objects.get()
        self.assertFalse(review.is_published)
        self.assertNotContains(self.client.get(reverse("home")), "Superb website")
        self.assertEqual(len(mail.outbox), 1)

    def test_review_honeypot(self):
        self.client.post(reverse("leave_review"), {
            "name": "Bot", "rating": 5, "message": "spam", "website": "x",
        })
        self.assertEqual(Testimonial.objects.count(), 0)


class BlogTests(TestCase):

    def test_only_published_posts_are_visible(self):
        live = Post.objects.create(title="Live post", excerpt="e", body="word " * 450, is_published=True, tags="Django, SEO")
        draft = Post.objects.create(title="Draft post", excerpt="e", body="b")

        response = self.client.get(reverse("blog"))
        self.assertContains(response, "Live post")
        self.assertNotContains(response, "Draft post")

        self.assertEqual(self.client.get(live.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(draft.get_absolute_url()).status_code, 404)

        self.assertEqual(live.reading_time, 3)
        self.assertEqual(live.tag_list, ["Django", "SEO"])

    def test_tag_filter(self):
        Post.objects.create(title="About Django", excerpt="e", body="b", is_published=True, tags="Django")
        Post.objects.create(title="About SEO", excerpt="e", body="b", is_published=True, tags="SEO")

        response = self.client.get(reverse("blog"), {"tag": "SEO"})
        self.assertContains(response, "About SEO")
        self.assertNotContains(response, "About Django")

    def test_duplicate_titles_get_unique_slugs(self):
        a = Post.objects.create(title="Same", excerpt="e", body="b")
        b = Post.objects.create(title="Same", excerpt="e", body="b")
        self.assertNotEqual(a.slug, b.slug)


class DashboardTests(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        self.admin = get_user_model().objects.create_superuser("boss", "boss@example.com", "pass12345")
        self.client.force_login(self.admin)

    def test_dashboard_and_admin_lists_load(self):
        ContactMessage.objects.create(name="Ali", email="a@example.com", subject="Shop", message="m", budget="25k_50k", project_type="ecommerce")
        ContactMessage.objects.create(name="Sara", email="s@example.com", subject="Site", message="m", status="won")
        Testimonial.objects.create(name="Zed", message="Pending one", is_published=False)

        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leads per month")
        self.assertContains(response, "1 new lead")
        self.assertContains(response, "Rs 25,000 - 50,000")

        for name in ["contactmessage", "project", "post", "testimonial"]:
            url = reverse(f"admin:base_{name}_changelist")
            self.assertEqual(self.client.get(url).status_code, 200, name)

    def test_dashboard_works_with_no_data(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No enquiries yet")

    def test_bulk_mark_leads_as_won(self):
        lead = ContactMessage.objects.create(name="Ali", email="a@example.com", subject="Shop", message="m")
        self.assertEqual(lead.status, "new")

        self.client.post(reverse("admin:base_contactmessage_changelist"), {
            "action": "mark_won",
            "_selected_action": [lead.pk],
        })
        lead.refresh_from_db()
        self.assertEqual(lead.status, "won")

    def test_lead_detail_has_reply_button(self):
        lead = ContactMessage.objects.create(name="Ali", email="a@example.com", subject="Shop", message="m")
        response = self.client.get(reverse("admin:base_contactmessage_change", args=[lead.pk]))
        self.assertContains(response, "mailto:a@example.com")


class ChatbotTests(TestCase):

    def post_lead(self, client=None, **data):
        import json
        payload = {"name": "Ali", "email": "ali@example.com", "message": "Need a shop", "website": ""}
        payload.update(data)
        return (client or self.client).post(reverse("chat_lead"), json.dumps(payload), content_type="application/json")

    def test_widget_is_on_every_page(self):
        for name in ["home", "about", "projects", "contact"]:
            self.assertContains(self.client.get(reverse(name)), 'id="chatbot"')

    def test_knowledge_comes_from_site_data(self):
        from .views import ESTIMATOR_PRICES
        data = self.client.get(reverse("chat_knowledge")).json()
        self.assertEqual(len(data["prices"]), len(ESTIMATOR_PRICES["types"]))
        self.assertEqual(data["prices"][0]["from"], ESTIMATOR_PRICES["types"][0]["base"])
        self.assertEqual(data["project_count"], Project.objects.count())
        self.assertTrue(all(p["url"].startswith("/project/") for p in data["projects"]))

    @override_settings(NOTIFY_EMAILS=["owner@example.com"])
    def test_lead_is_saved_as_enquiry_and_emailed(self):
        response = self.post_lead(project_type="ecommerce")
        self.assertEqual(response.json(), {"ok": True})

        lead = ContactMessage.objects.get()
        self.assertEqual((lead.name, lead.email, lead.project_type), ("Ali", "ali@example.com", "ecommerce"))
        self.assertIn("Chatbot", lead.subject)
        self.assertIn("chat assistant", lead.notes)
        self.assertEqual(len(mail.outbox), 2)

    def test_lead_without_message_is_allowed(self):
        self.assertEqual(self.post_lead(message="").status_code, 200)
        self.assertIn("no message", ContactMessage.objects.get().message)

    def test_invalid_email_is_rejected(self):
        response = self.post_lead(email="not-an-email")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json()["errors"])
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_unknown_project_type_is_ignored(self):
        self.post_lead(project_type="<script>")
        self.assertEqual(ContactMessage.objects.get().project_type, "")

    def test_honeypot_blocks_bots(self):
        self.assertEqual(self.post_lead(website="spam").status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_rate_limit_per_visitor(self):
        for _ in range(3):
            self.assertEqual(self.post_lead().status_code, 200)
        self.assertEqual(self.post_lead().status_code, 429)
        self.assertEqual(ContactMessage.objects.count(), 3)

    def test_csrf_is_required(self):
        from django.test import Client
        response = self.post_lead(client=Client(enforce_csrf_checks=True))
        self.assertEqual(response.status_code, 403)

    def test_get_is_not_allowed_on_lead(self):
        self.assertEqual(self.client.get(reverse("chat_lead")).status_code, 405)


class SeoTests(TestCase):

    def test_sitemap_and_robots(self):
        Post.objects.create(title="Indexed post", excerpt="e", body="b", is_published=True)

        sitemap = self.client.get(reverse("sitemap"))
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/blog/indexed-post/")
        self.assertContains(sitemap, "/estimate/")

        robots = self.client.get("/robots.txt")
        self.assertEqual(robots["Content-Type"], "text/plain")
        self.assertContains(robots, "Sitemap: http://testserver/sitemap.xml")

    def test_pages_have_social_preview_tags(self):
        response = self.client.get(reverse("about"))
        self.assertContains(response, 'property="og:image"')
        self.assertContains(response, "images/pic2.jpg")
        self.assertContains(response, 'rel="canonical"')
