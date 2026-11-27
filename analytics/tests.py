from datetime import date, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import PageView
from .stats import visitor_summary
from .tracking import device_of, visitor_id

CHROME = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
IPHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


class TrackingTests(TestCase):

    def visit(self, path="/", ua=CHROME, **headers):
        return self.client.get(path, HTTP_USER_AGENT=ua, **headers)

    def test_public_page_view_is_recorded(self):
        self.visit("/", HTTP_REFERER="https://www.google.com/search?q=rana+umar")
        view = PageView.objects.get()
        self.assertEqual(view.path, "/")
        self.assertEqual(view.source, "Google")
        self.assertEqual(view.device, "desktop")
        self.assertEqual(len(view.visitor), 16)

    def test_clicks_inside_the_site_have_no_source(self):
        self.visit("/about/", HTTP_REFERER="http://testserver/")
        self.assertEqual(PageView.objects.get().source, "")

    def test_direct_and_utm_sources(self):
        self.visit("/")
        self.visit("/projects/?utm_source=linkedin")
        self.assertEqual(list(PageView.objects.order_by("id").values_list("source", flat=True)), ["Direct", "Linkedin"])

    def test_mobile_device(self):
        self.visit("/", ua=IPHONE)
        self.assertEqual(PageView.objects.get().device, "mobile")

    def test_things_that_are_not_counted(self):
        self.visit("/", ua="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
        self.visit("/", ua="WhatsApp/2.23.20.0 A")             # link preview, not a visit
        self.visit("/", ua="")                                   # no browser at all
        self.visit("/", HTTP_SEC_PURPOSE="prefetch")             # browser prefetch
        self.visit(reverse("terminal_data"))                     # JSON endpoint
        self.visit("/robots.txt")
        self.visit("/this-page-does-not-exist/")                 # 404
        self.client.post("/contact/", {}, HTTP_USER_AGENT=CHROME)  # not a GET
        self.assertEqual(PageView.objects.count(), 0)

    def test_staff_visits_are_not_counted(self):
        admin = get_user_model().objects.create_superuser("boss", "boss@example.com", "pass12345")
        self.client.force_login(admin)
        self.visit("/")
        self.visit("/admin/")
        self.assertEqual(PageView.objects.count(), 0)

    def test_visitor_id_is_anonymous_and_changes_daily(self):
        rf = RequestFactory()
        req = rf.get("/", HTTP_USER_AGENT=CHROME, REMOTE_ADDR="203.0.113.7")
        today = date(2026, 11, 25)
        self.assertEqual(visitor_id(req, today), visitor_id(req, today))
        self.assertNotEqual(visitor_id(req, today), visitor_id(req, today + timedelta(days=1)))
        self.assertNotIn("203.0.113.7", visitor_id(req, today))
        field_names = {f.name for f in PageView._meta.get_fields()}
        self.assertFalse({"ip", "ip_address", "user_agent"} & field_names, "no personal data is stored")

    def test_analytics_errors_never_break_the_site(self):
        with mock.patch("analytics.models.PageView.objects.create", side_effect=RuntimeError("db down")):
            response = self.visit("/")
        self.assertEqual(response.status_code, 200)

    def test_device_detection(self):
        self.assertEqual(device_of(IPHONE), "mobile")
        self.assertEqual(device_of("Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X)"), "tablet")
        self.assertEqual(device_of(CHROME), "desktop")


class DashboardTests(TestCase):

    def setUp(self):
        self.admin = get_user_model().objects.create_superuser("boss", "boss@example.com", "pass12345")

    def test_summary_numbers(self):
        from django.utils import timezone
        today = timezone.localdate()
        PageView.objects.create(day=today, path="/", visitor="a", source="Google", device="mobile")
        PageView.objects.create(day=today, path="/projects/", visitor="a", source="", device="mobile")
        PageView.objects.create(day=today, path="/", visitor="b", source="Direct", device="desktop")
        PageView.objects.create(day=today - timedelta(days=3), path="/", visitor="c", source="LinkedIn", device="desktop")
        PageView.objects.create(day=today - timedelta(days=45), path="/", visitor="old", source="Direct")  # previous period

        s = visitor_summary(30)
        self.assertEqual(s["views_today"], 3)
        self.assertEqual(s["visitors_today"], 2)
        self.assertEqual(s["views"], 4)
        self.assertEqual(s["visits"], 3)
        self.assertEqual(s["change"], 300)
        self.assertEqual(s["pages"][0]["label"], "Home")
        self.assertEqual({x["label"] for x in s["sources"]}, {"Google", "Direct", "LinkedIn"})  # internal clicks excluded
        self.assertEqual(len(s["daily"]), 30)
        self.assertEqual(s["daily"][-1]["count"], 3)

    def test_dashboard_shows_visitors_section(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Website visitors")
        self.assertContains(response, "No visits recorded yet")

        from django.utils import timezone
        PageView.objects.create(day=timezone.localdate(), path="/about/", visitor="x", source="GitHub")
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "Views per day")
        self.assertContains(response, "GitHub")
        self.assertNotContains(response, "No visits recorded yet")

    def test_page_view_admin_is_read_only(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("admin:analytics_pageview_changelist")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:analytics_pageview_add")).status_code, 403)
