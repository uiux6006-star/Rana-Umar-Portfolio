from django.db import migrations


SLUG = "eternal-wedding-invitation"

GALLERY = [
    ("projects/gallery/eternal-wedding-mehndi.jpg", "Mehndi page: emerald green with marigold garlands"),
    ("projects/gallery/eternal-wedding-baraat.jpg", "Baraat page: royal palace, lanterns and string lights"),
    ("projects/gallery/eternal-wedding-walima.jpg", "Walima page: ivory and gold reception card"),
]


def add_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    ProjectImage = apps.get_model("base", "ProjectImage")
    if Project.objects.filter(slug=SLUG).exists():
        return

    project = Project.objects.create(
        title="Eternal Wedding Invitation",
        slug=SLUG,
        description=(
            "A luxury digital wedding invitation for the Mehndi, Baraat and Walima. Guests open a "
            "maroon and gold envelope by breaking its wax seal, then explore a separate themed page "
            "for each event with a live countdown, venue details with Google Maps, a photo gallery "
            "and an RSVP form that sends their reply straight to WhatsApp. Background music, falling "
            "petals and smooth GSAP animations make it feel like a real royal card, and every name, "
            "date and venue is edited from one simple config file."
        ),
        image="projects/eternal-wedding.jpg",
        category="frontend",
        technologies="HTML5, CSS3, JavaScript, GSAP, Responsive Design",
        github_link="",
        live_demo="https://sweet-duckanoo-9b0470.netlify.app/",
        featured=True,
        client="Concept project",
        duration="",
        problem=(
            "Printed wedding cards are expensive, slow to deliver and easy to lose. Guests forget "
            "dates and venues, and families spend days chasing RSVPs by phone."
        ),
        solution=(
            "One shareable link that works like a premium card. An animated envelope opens the "
            "invitation, and each event (Mehndi, Baraat, Walima) gets its own page and colour theme "
            "with a countdown, map link and gallery. The RSVP form collects the guest's name, whether "
            "they can attend and how many guests are coming, and sends it to the family on WhatsApp "
            "in one tap."
        ),
        result=(
            "A fast, mobile-friendly invitation that can be sent to every guest on WhatsApp in "
            "seconds, keeps all event details in one place, and can be re-used for any couple by "
            "changing a single config file."
        ),
    )

    for order, (image, caption) in enumerate(GALLERY):
        ProjectImage.objects.create(project=project, image=image, caption=caption, order=order)


def remove_project(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0011_add_universe_explorer_project"),
    ]

    operations = [
        migrations.RunPython(add_project, remove_project),
    ]
