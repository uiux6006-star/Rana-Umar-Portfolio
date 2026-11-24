from django.db import migrations


# Created oldest first, so ZAAYKA ends up newest and is listed first.
PROJECTS = [
    {
        "title": "VAULTIX Password Intelligence",
        "slug": "vaultix-password-intelligence",
        "kind": "webapp",
        "client": "Personal project",
        "description": (
            "A privacy-first password toolkit that runs entirely in the browser. It generates "
            "cryptographically secure passwords with the Web Crypto API, analyses the strength of any "
            "password you type, and explains entropy, reuse, MFA and phishing in a plain-language "
            "security guide. History is off by default, a strict Content Security Policy blocks every "
            "network request, and the dashboard comes with dark, light and system themes."
        ),
        "image": "projects/vaultix-password.jpg",
        "technologies": "HTML5, CSS3, JavaScript, Web Crypto API, Content Security Policy, LocalStorage",
        "live_demo": "https://fabulous-tapioca-5c83dc.netlify.app/",
        "features": "\n".join([
            "Secure generator using crypto.getRandomValues()",
            "Unbiased rejection sampling",
            "Length from 8 to 128 with character group options",
            "Exclude similar and ambiguous characters",
            "Private strength analyzer with entropy estimate",
            "Opt-in password history, off by default",
            "Security guide and personal checklist",
            "Dark, light and system themes",
        ]),
        "problem": (
            "Many online password generators are full of ads, use weak randomness or quietly send data "
            "to a server, and they rarely explain what actually makes a password strong."
        ),
        "solution": (
            "A local-only app built around the browser's Web Crypto API, with rejection sampling so every "
            "character is equally likely. A Content Security Policy with connect-src 'none' means the page "
            "cannot send anything over the network, the analyzer never stores what you type, and history is "
            "strictly opt-in. A guide and checklist turn security advice into simple steps."
        ),
        "result": (
            "A fast, trustworthy password tool that works on any device, keeps every password on the "
            "user's own machine and teaches good security habits along the way."
        ),
    },
    {
        "title": "ZAAYKA Restaurant Website",
        "slug": "zaayka-restaurant",
        "kind": "business",
        "client": "Concept project",
        "description": (
            "A cinematic restaurant website for a desi fine-dining brand known for dum biryani, BBQ and "
            "karahi. Scroll-driven animations tell the story of five signature dishes, a filterable menu "
            "opens dish details with portion and heat options, and an order drawer sends the order on "
            "WhatsApp. Guests can preview a table reservation, find the restaurant on Google Maps and "
            "explore the chef's story, all with smooth scrolling and a warm black and gold design."
        ),
        "image": "projects/zaayka-restaurant.jpg",
        "technologies": "HTML5, CSS3, JavaScript, GSAP, ScrollTrigger, Lenis, Responsive Design",
        "live_demo": "https://stellular-seahorse-51958e.netlify.app/",
        "features": "\n".join([
            "Scroll-told story of five signature dishes",
            "Menu with category filters",
            "Dish details with portion and heat options",
            "Order drawer that sends the order on WhatsApp",
            "Table reservation preview with WhatsApp confirmation",
            "Google Maps directions and opening hours",
            "Smooth scrolling and text animations",
            "Black and gold luxury design",
        ]),
        "problem": (
            "Restaurant websites often show a plain menu and a phone number, so they fail to capture the "
            "atmosphere and flavour that make people want to visit or order."
        ),
        "solution": (
            "A story-first experience built with GSAP and ScrollTrigger: each signature dish is revealed as "
            "you scroll, with its ingredients and price. The menu, dish modal and order drawer work together "
            "so guests can build an order and send it on WhatsApp in one tap, while the reservation form "
            "previews the booking and hands off to WhatsApp until a booking backend is connected."
        ),
        "result": (
            "A premium, mobile-friendly restaurant website that feels like a fine-dining brand and turns "
            "visitors into WhatsApp orders and table requests, ready to adapt for any restaurant."
        ),
    },
]


def add_projects(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    for data in PROJECTS:
        if Project.objects.filter(slug=data["slug"]).exists():
            continue
        Project.objects.create(category="frontend", github_link="", featured=True, duration="", **data)


def remove_projects(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug__in=[p["slug"] for p in PROJECTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0017_set_project_kinds_and_features"),
    ]

    operations = [
        migrations.RunPython(add_projects, remove_projects),
    ]
