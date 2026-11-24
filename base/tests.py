from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage, Post, Project, Testimonial


class PageTests(TestCase):

    def test_main_pages_load(self):
        for name in ["home", "about", "projects", "services", "contact", "blog", "estimate", "leave_review"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)

    def test_home_service_prices_come_from_the_estimator(self):
        from .views import ESTIMATOR_PRICES
        response = self.client.get(reverse("home"))
        for t in ESTIMATOR_PRICES["types"]:
            self.assertContains(response, f"Rs {t['base']:,}")
        self.assertContains(response, 'id="hpProcess"')

    def test_services_prices_come_from_the_estimator(self):
        from .views import ESTIMATOR_PRICES
        response = self.client.get(reverse("services"))
        html = response.content.decode()
        self.assertEqual(html.count("<h1"), 1)
        for t in ESTIMATOR_PRICES["types"]:
            self.assertContains(response, f"Rs {t['base']:,}")
            self.assertContains(response, f"?type={t['id']}")
        for f in ESTIMATOR_PRICES["features"]:
            self.assertContains(response, f"+ Rs {f['price']:,}")

    def test_estimator_preselects_type_from_url(self):
        response = self.client.get(reverse("estimate"), {"type": "ecommerce"})
        self.assertEqual(response.context["selected_type"], "ecommerce")
        self.assertContains(response, 'value="ecommerce" checked')
        # Unknown values fall back to the default package
        response = self.client.get(reverse("estimate"), {"type": "<script>"})
        self.assertEqual(response.context["selected_type"], "business")

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

    def test_projects_page_filters_and_cards(self):
        Project.objects.create(title="Shop X", description="d", image="projects/x.jpg",
                               category="django", technologies="Django", live_demo="https://example.com")
        response = self.client.get(reverse("projects"))
        html = response.content.decode()
        self.assertEqual(html.count("<h1"), 1)
        self.assertEqual(html.count('class="pj-card'), Project.objects.count())
        django_count = Project.objects.filter(category="django").count()
        self.assertContains(response, f'data-filter="django" aria-pressed="false">\n                    Django <span>{django_count}</span>')
        self.assertEqual(response.context["live_count"], Project.objects.exclude(live_demo="").count())

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

    def test_newest_post_is_featured_and_topics_are_counted(self):
        from datetime import timedelta
        from django.utils import timezone
        now = timezone.now()
        Post.objects.create(title="Older one", excerpt="e", body="b", is_published=True,
                            tags="Django, SEO", published_at=now - timedelta(days=2))
        Post.objects.create(title="Newest one", excerpt="e", body="b", is_published=True,
                            tags="seo", published_at=now)

        response = self.client.get(reverse("blog"))
        self.assertEqual(response.context["featured"].title, "Newest one")
        self.assertEqual([p.title for p in response.context["posts"]], ["Older one"])
        # Tags are counted case-insensitively, most used first
        self.assertEqual(response.context["all_tags"], [{"name": "SEO", "count": 2}, {"name": "Django", "count": 1}])
        self.assertEqual(self.client.get(reverse("blog")).content.decode().count("<h1"), 1)

        # A tag filter shows a plain grid, no featured card
        filtered = self.client.get(reverse("blog"), {"tag": "Django"})
        self.assertIsNone(filtered.context["featured"])

    def test_empty_blog_shows_coming_soon(self):
        response = self.client.get(reverse("blog"))
        self.assertContains(response, "The first articles are on the way")

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


class AdminLoginTests(TestCase):

    def setUp(self):
        from django.contrib.auth import get_user_model
        get_user_model().objects.create_superuser("boss", "boss@example.com", "Str0ng-pass-123")
        self.url = reverse("admin:login")

    def test_login_page_renders(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Admin <span>Dashboard</span> Login", html=False)
        self.assertContains(response, 'name="remember_me"')
        self.assertContains(response, reverse("admin_password_reset"))

    def test_correct_login_goes_to_dashboard(self):
        response = self.client.post(self.url, {"username": "boss", "password": "Str0ng-pass-123", "next": "/admin/", "remember_me": "1"})
        self.assertRedirects(response, "/admin/")
        self.assertFalse(self.client.session.get_expire_at_browser_close())

    def test_without_remember_me_session_ends_with_browser(self):
        self.client.post(self.url, {"username": "boss", "password": "Str0ng-pass-123", "next": "/admin/"})
        self.assertTrue(self.client.session.get_expire_at_browser_close())

    def test_wrong_password_shows_error_and_keeps_username(self):
        response = self.client.post(self.url, {"username": "boss", "password": "wrong", "next": "/admin/"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "lg-alert")
        self.assertContains(response, 'value="boss"')

    def test_forgot_password_emails_a_reset_link(self):
        response = self.client.post(reverse("admin_password_reset"), {"email": "boss@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/reset/", mail.outbox[0].body)

    def test_forgot_password_does_not_reveal_unknown_emails(self):
        response = self.client.post(reverse("admin_password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)


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


class DeveloperHubTests(TestCase):
    """Terminal, GitHub centre, Skills Universe, CV centre and case studies."""

    def setUp(self):
        from django.core.cache import cache
        cache.clear()

    # ---------- Profile data ----------

    def test_profile_data_is_consistent_and_honest(self):
        from . import profile
        ids = {s["id"] for s in profile.SKILLS}
        for s in profile.SKILLS:
            self.assertIn(s["level"], profile.LEVELS, s["id"])
            self.assertIn(s["group"], {g["id"] for g in profile.SKILL_GROUPS})
            for r in s["related"]:
                self.assertIn(r, ids, f"{s['id']} links to unknown skill {r}")
            self.assertNotRegex(" ".join([s["about"], *s["builds"]]), r"\d+\s*%", "no fake percentages")
        for step in profile.JOURNEY:
            for sid in step["skills"]:
                self.assertIn(sid, ids)

    # ---------- Terminal ----------

    def test_terminal_data(self):
        Project.objects.create(title="Shop T", description="d", image="projects/x.jpg",
                               category="django", technologies="Django, Python", kind="webapp")
        data = self.client.get(reverse("terminal_data")).json()
        self.assertEqual(len(data["projects"]), Project.objects.count())
        self.assertEqual(data["contact"]["github"], "https://github.com/uiux6006-star")
        self.assertTrue(data["cv"].endswith("Rana_Umar_CV.pdf"))
        self.assertEqual(data["experience"][0]["role"], "Freelance Full Stack Developer")
        levels = {i["level"] for g in data["skills"] for i in g["items"]}
        self.assertTrue(levels <= {"Building Projects", "Working With", "Learning"})

    def test_terminal_is_on_every_page(self):
        for name in ["home", "about", "projects", "services", "contact", "blog"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, 'id="rudTerminal"')
                self.assertContains(response, "data-open-terminal")
                self.assertContains(response, "js/terminal.js")
        # The home page also has an inline terminal
        self.assertEqual(self.client.get(reverse("home")).content.decode().count("data-terminal="), 2)

    # ---------- GitHub ----------

    def _fake_github(self, path):
        if path.startswith("/users/uiux6006-star/repos"):
            return [
                {"name": "portfolio", "html_url": "https://github.com/x/portfolio", "language": "Python",
                 "fork": False, "pushed_at": "2026-11-20T10:00:00Z", "stargazers_count": 2},
                {"name": "site", "html_url": "https://github.com/x/site", "language": "HTML",
                 "fork": False, "pushed_at": "2026-11-01T10:00:00Z"},
                {"name": "forked", "html_url": "https://github.com/x/forked", "language": "Go",
                 "fork": True, "pushed_at": "2026-11-22T10:00:00Z"},
            ]
        if path.startswith("/users/uiux6006-star/events"):
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime("%Y-%m-%dT10:00:00Z")
            return [{"type": "PushEvent", "created_at": today, "payload": {"commits": [{}, {}, {}]}},
                    {"type": "CreateEvent", "created_at": "2001-01-01T00:00:00Z"}]
        return {"login": "uiux6006-star", "public_repos": 3, "followers": 4, "following": 1,
                "html_url": "https://github.com/uiux6006-star", "avatar_url": "https://a/x.png"}

    def test_github_data_live(self):
        from unittest import mock
        with mock.patch("base.devhub._get", side_effect=self._fake_github):
            data = self.client.get(reverse("github_data")).json()
        self.assertTrue(data["ok"])
        self.assertEqual([r["name"] for r in data["repos"]], ["portfolio", "site"])  # no forks, newest first
        self.assertEqual({lang["name"] for lang in data["languages"]}, {"Python", "HTML"})
        self.assertEqual(len(data["activity"]), 84)
        self.assertEqual(data["activity_total"], 3)  # old event ignored, a push counts its commits

        # Cached: GitHub is not called again
        with mock.patch("base.devhub._get", side_effect=AssertionError("should use the cache")):
            self.assertTrue(self.client.get(reverse("github_data")).json()["ok"])

    def test_github_failure_falls_back_without_fake_data(self):
        import urllib.error
        from unittest import mock
        with mock.patch("base.devhub._get", side_effect=urllib.error.URLError("offline")):
            data = self.client.get(reverse("github_data")).json()
        self.assertFalse(data["ok"])
        self.assertNotIn("repos", data)
        self.assertEqual(data["profile_url"], "https://github.com/uiux6006-star")

    def test_home_has_github_centre_and_new_hero(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'id="ghHub"')
        self.assertContains(response, "FUTURE PYTHON DEVELOPER")
        self.assertContains(response, "Explore My Projects")
        self.assertContains(response, "Hire Me")
        self.assertContains(response, "cv/Rana_Umar_CV.pdf")

    # ---------- About ----------

    def test_about_has_universe_journey_and_cv(self):
        from . import profile
        response = self.client.get(reverse("about"))
        self.assertContains(response, 'id="suData"')
        self.assertEqual(len(response.context["universe"]), len(profile.SKILLS))
        self.assertEqual(len(response.context["journey"]), len(profile.JOURNEY))
        self.assertContains(response, "Govt. Crescent College, Faisalabad")
        self.assertContains(response, "View CV")
        self.assertNotContains(response, "2025 · START")  # no invented dates
        # A skill only lists projects that really use it
        django = next(s for s in response.context["universe"] if s["id"] == "django")
        for p in django["projects"]:
            project = Project.objects.get(title=p["title"])
            self.assertTrue(any("django" in t.lower() for t in project.tech_list))

    # ---------- Projects + case study ----------

    def test_project_kind_filters_only_show_used_types(self):
        Project.objects.update(kind="")
        Project.objects.create(title="Biz", description="d", image="projects/x.jpg",
                               category="frontend", technologies="HTML", kind="business")
        html = self.client.get(reverse("projects")).content.decode()
        self.assertIn('data-filter="kind:business"', html)
        self.assertNotIn('data-filter="kind:ecommerce"', html)
        self.assertIn('data-kind="business"', html)

    def test_case_study_page(self):
        older = Project.objects.create(title="Older one", description="d", image="projects/x.jpg",
                                       category="django", technologies="Django, SQLite, Bootstrap")
        newer = Project.objects.create(title="Newer one", description="d", image="projects/y.jpg",
                                       category="frontend", technologies="HTML", features="Fast\n- Responsive\n\n",
                                       live_demo="https://example.com/")
        response = self.client.get(older.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count("<h1"), 1)
        self.assertEqual(response.context["prev_project"], newer)
        stack = {g["label"]: g["items"] for g in response.context["stack"]}
        self.assertEqual(stack["Backend"], ["Django"])
        self.assertEqual(stack["Data & storage"], ["SQLite"])
        self.assertEqual(stack["Frontend"], ["Bootstrap"])

        response = self.client.get(newer.get_absolute_url())
        self.assertEqual(newer.feature_list, ["Fast", "Responsive"])
        self.assertContains(response, "Key features")
        self.assertContains(response, 'data-src="https://example.com/"')  # live preview loads only on request

    # ---------- Services ----------

    def test_css_and_js_links_are_versioned_for_cache_busting(self):
        import re
        html = self.client.get(reverse("about")).content.decode()
        self.assertRegex(html, r'/static/css/style\.css\?v=\d+')
        self.assertRegex(html, r'/static/js/about\.js\?v=\d+')
        self.assertFalse(re.search(r'/static/(css|js)/[\w.-]+\.(css|js)"', html), "an unversioned CSS/JS link is left")

    def test_services_lists_six_services_with_working_links(self):
        from . import profile
        response = self.client.get(reverse("services"))
        for s in profile.SERVICES:
            self.assertContains(response, s["name"])
        self.assertContains(response, "/projects/?kind=business")
