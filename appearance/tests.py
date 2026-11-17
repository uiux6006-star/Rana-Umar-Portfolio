from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.urls import reverse

from .models import SiteTheme
from .themes import ORIGINAL, THEMES, build_css, build_tokens, contrast

PUBLIC_PAGES = ["home", "about", "projects", "services", "blog", "estimate", "leave_review", "contact"]


def make_admin(username="boss"):
    return get_user_model().objects.create_superuser(username, f"{username}@example.com", "pass12345")


class ThemeDefinitionTests(TestCase):

    def test_there_are_nine_themes_with_original_first(self):
        self.assertEqual(len(THEMES), 9)
        self.assertEqual(list(THEMES)[0], ORIGINAL)

    def test_every_theme_is_readable_in_both_modes(self):
        for slug in THEMES:
            tokens = build_tokens(slug)
            dark, light = tokens["dark"], tokens["light"]
            with self.subTest(theme=slug):
                self.assertGreaterEqual(contrast(dark["--text"], dark["--bg"]), 7)
                self.assertGreaterEqual(contrast(dark["--text-muted"], dark["--bg"]), 4.5)
                self.assertGreaterEqual(contrast(dark["--on-accent"], dark["--accent"]), 4.5)
                self.assertGreaterEqual(contrast(light["--accent"], "#ffffff"), 4.5)
                self.assertGreaterEqual(contrast(light["--on-accent"], light["--accent"]), 4.5)

    def test_original_theme_adds_no_overrides(self):
        # The stylesheet's own colours are used untouched.
        self.assertEqual(build_css(ORIGINAL), "")

    def test_original_with_custom_accent_only_changes_accent(self):
        css = build_css(ORIGINAL, "#ff0066")
        self.assertIn("--accent:#ff0066", css)
        self.assertNotIn("--bg:", css)

    def test_unsafe_accent_never_reaches_css(self):
        css = build_css("royal-gold", "red;}</style><script>")
        self.assertNotIn("script", css)
        self.assertIn("--accent:#d4af37", css)


class PublicSiteTests(TestCase):

    def test_original_theme_by_default(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-site-theme="original"')
        self.assertNotContains(response, 'id="site-theme"')

    def test_every_theme_renders_on_every_page(self):
        setting = SiteTheme.load()
        for slug in THEMES:
            setting.apply(slug)
            for page in PUBLIC_PAGES:
                with self.subTest(theme=slug, page=page):
                    response = self.client.get(reverse(page))
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, f'data-site-theme="{slug}"')
                    if slug != ORIGINAL:
                        self.assertContains(response, 'id="site-theme"')
                        self.assertContains(response, THEMES[slug]["primary"])

    def test_serif_font_is_loaded_only_for_royal_gold(self):
        SiteTheme.load().apply("royal-gold")
        self.assertContains(self.client.get(reverse("home")), "Playfair+Display")
        SiteTheme.load().apply("ocean-teal")
        self.assertNotContains(self.client.get(reverse("home")), "Playfair+Display")

    def test_sora_font_is_loaded_only_for_obsidian_emerald(self):
        SiteTheme.load().apply("obsidian-emerald")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "family=Sora")
        self.assertContains(response, "--accent:#34e0a1")
        SiteTheme.load().apply("ocean-teal")
        self.assertNotContains(self.client.get(reverse("home")), "family=Sora")

    def test_theme_persists_across_requests(self):
        SiteTheme.load().apply("neon-pink")
        for _ in range(2):
            self.assertContains(self.client.get(reverse("about")), 'data-site-theme="neon-pink"')

    def test_preview_is_not_visible_to_visitors(self):
        session = self.client.session
        session["theme_preview"] = {"theme": "neon-hacker", "accent": ""}
        session.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, 'data-site-theme="original"')
        self.assertNotContains(response, "theme-preview-bar")


class CustomizerTests(TestCase):

    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)
        self.url = reverse("admin:theme_customizer")

    def test_customizer_page_lists_all_themes(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for theme in THEMES.values():
            self.assertContains(response, theme["name"])
        self.assertContains(response, "Reset to Original", count=0)  # already original

    def test_sidebar_link_opens_customizer(self):
        # The model's changelist URL (used by the sidebar) is the customizer itself.
        self.assertEqual(reverse("admin:appearance_sitetheme_changelist"), self.url)
        response = self.client.get(reverse("admin:appearance_sitetheme_changelist"))
        self.assertContains(response, "Theme Customizer")

    def test_change_page_redirects_to_customizer(self):
        SiteTheme.load()
        response = self.client.get(reverse("admin:appearance_sitetheme_change", args=[1]))
        self.assertRedirects(response, self.url)

    def test_apply_theme_updates_public_site(self):
        response = self.client.post(reverse("admin:theme_apply"), {"theme": "cyber-purple"})
        self.assertRedirects(response, self.url)

        setting = SiteTheme.objects.get()
        self.assertEqual(setting.theme, "cyber-purple")
        self.assertEqual(setting.previous_theme, ORIGINAL)
        self.assertEqual(setting.updated_by, self.admin)

        public = Client()
        self.assertContains(public.get(reverse("projects")), 'data-site-theme="cyber-purple"')

    def test_apply_shows_success_message(self):
        response = self.client.post(reverse("admin:theme_apply"), {"theme": "ocean-teal"}, follow=True)
        self.assertContains(response, "is now live on your website")

    def test_unknown_theme_is_rejected(self):
        response = self.client.post(reverse("admin:theme_apply"), {"theme": "hacked"}, follow=True)
        self.assertContains(response, "doesn&#x27;t exist")
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)

    def test_get_cannot_change_theme(self):
        response = self.client.get(reverse("admin:theme_apply"), {"theme": "neon-pink"})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)

    def test_custom_accent(self):
        self.client.post(reverse("admin:theme_apply"), {"theme": "midnight-blue"})
        self.client.post(reverse("admin:theme_accent"), {"accent": "#FF3366"})
        self.assertEqual(SiteTheme.load().custom_accent, "#ff3366")
        self.assertContains(Client().get(reverse("home")), "--accent:#ff3366")

        self.client.post(reverse("admin:theme_accent"), {"clear": "1"})
        self.assertEqual(SiteTheme.load().custom_accent, "")

    def test_invalid_accent_is_rejected(self):
        response = self.client.post(reverse("admin:theme_accent"), {"accent": "blue"}, follow=True)
        self.assertContains(response, "valid colour")
        self.assertEqual(SiteTheme.load().custom_accent, "")

    def test_reset_to_original(self):
        self.client.post(reverse("admin:theme_apply"), {"theme": "sunset-orange"})
        self.client.post(reverse("admin:theme_accent"), {"accent": "#123456"})
        self.client.post(reverse("admin:theme_reset"))

        setting = SiteTheme.load()
        self.assertEqual(setting.theme, ORIGINAL)
        self.assertEqual(setting.custom_accent, "")
        self.assertEqual(setting.previous_theme, "sunset-orange")

    def test_restore_previous_theme(self):
        self.client.post(reverse("admin:theme_apply"), {"theme": "royal-gold"})
        self.client.post(reverse("admin:theme_apply"), {"theme": "neon-hacker"})
        response = self.client.get(self.url)
        self.assertContains(response, "Restore previous: Royal Gold Luxury")

    def test_preview_only_for_this_admin_then_exit(self):
        response = self.client.post(reverse("admin:theme_preview"), {"theme": "neon-hacker"})
        self.assertRedirects(response, reverse("home"))

        mine = self.client.get(reverse("home"))
        self.assertContains(mine, 'data-site-theme="neon-hacker"')
        self.assertContains(mine, "theme-preview-bar")

        visitor = Client().get(reverse("home"))
        self.assertContains(visitor, 'data-site-theme="original"')
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)

        self.client.post(reverse("admin:theme_preview_exit"))
        self.assertContains(self.client.get(reverse("home")), 'data-site-theme="original"')

    def test_apply_from_preview_bar_keeps_preview_accent(self):
        self.client.post(reverse("admin:theme_apply"), {"theme": "ocean-teal", "accent": "#00aa88", "next": "/about/"})
        setting = SiteTheme.load()
        self.assertEqual((setting.theme, setting.custom_accent), ("ocean-teal", "#00aa88"))

    def test_open_redirect_is_blocked(self):
        response = self.client.post(reverse("admin:theme_apply"), {"theme": "neon-pink", "next": "https://evil.example"})
        self.assertRedirects(response, self.url)


class PermissionTests(TestCase):

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(reverse("admin:theme_customizer"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response["Location"])

        self.client.post(reverse("admin:theme_apply"), {"theme": "neon-pink"})
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)

    def test_staff_without_permission_cannot_change_theme(self):
        user = get_user_model().objects.create_user("helper", password="pass12345", is_staff=True)
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("admin:theme_customizer")).status_code, 403)
        self.assertEqual(self.client.post(reverse("admin:theme_apply"), {"theme": "neon-pink"}).status_code, 403)
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)

    def test_staff_with_view_permission_sees_page_but_cannot_apply(self):
        user = get_user_model().objects.create_user("viewer", password="pass12345", is_staff=True)
        user.user_permissions.add(Permission.objects.get(codename="view_sitetheme"))
        self.client.force_login(user)

        response = self.client.get(reverse("admin:theme_customizer"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("admin:theme_reset"))
        self.assertEqual(self.client.post(reverse("admin:theme_apply"), {"theme": "neon-pink"}).status_code, 403)

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(make_admin("csrf"))
        response = client.post(reverse("admin:theme_apply"), {"theme": "neon-pink"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(SiteTheme.load().theme, ORIGINAL)
