from django.db import migrations


SLUG = "royal-world-of-queen"


def add_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    if Project.objects.filter(slug=SLUG).exists():
        return

    Project.objects.create(
        title="The Royal World of Queen",
        slug=SLUG,
        description=(
            "A cinematic, story-driven proposal website designed like a royal palace in maroon and "
            "gold. The journey opens at animated palace gates, then moves through chapters: a private "
            "letter sealed with wax, a timeline with calendar dates, a gallery of moments, flip cards "
            "of reasons, a promise and the final proposal with a hidden treasure. Falling petals and "
            "glowing hearts are drawn on canvas, a built-in music player sets the mood, and every "
            "name, date, message and photo is edited from one config file."
        ),
        image="projects/royal-world-of-queen.jpg",
        category="frontend",
        technologies="HTML5, CSS3, JavaScript, GSAP, Canvas API, Responsive Design",
        github_link="",
        live_demo="https://astonishing-sherbet-75944e.netlify.app/",
        featured=True,
        client="Personal project",
        duration="",
        problem=(
            "A proposal is one of the most important moments in someone's life, but a text message "
            "or a plain card cannot carry the feeling, the shared memories and the surprise it deserves."
        ),
        solution=(
            "An interactive experience that unfolds like a royal story. Each chapter is revealed step "
            "by step with GSAP animations: tap the wax seal to open the letter, browse the timeline and "
            "photo gallery, flip cards to read the reasons, and reach the proposal at the end. A canvas "
            "particle system adds petals, hearts and glow, background music plays with its own controls, "
            "and an optional heart keypad can lock the entrance. All content lives in a single "
            "config.js file, so the whole site can be personalised without touching the layout."
        ),
        result=(
            "A one-of-a-kind, mobile-friendly experience that can be shared as a single link, feels "
            "like a premium film rather than a web page, and can be re-used for any couple by editing "
            "one file."
        ),
    )


def remove_project(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0012_add_eternal_wedding_project"),
    ]

    operations = [
        migrations.RunPython(add_project, remove_project),
    ]
