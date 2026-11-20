from django.db import migrations


SLUG = "dentora-dental-clinic"


def add_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    if Project.objects.filter(slug=SLUG).exists():
        return

    Project.objects.create(
        title="Dentora Dental Clinic Website",
        slug=SLUG,
        description=(
            "A premium seven-page website for a modern dental clinic in Lahore: Home, Services, Team, "
            "About, Reviews, FAQs and Contact. Patients can browse treatments like whitening, implants "
            "and braces, meet the dentists, read reviews and book a visit through an appointment form "
            "with a date and time-slot picker. Dark mode switches with a circular reveal, and a search "
            "overlay, testimonial slider, FAQ filters, animated counters and a WhatsApp button make the "
            "whole site feel polished and easy to use."
        ),
        image="projects/dentora-dental.jpg",
        category="frontend",
        technologies="HTML5, CSS3, JavaScript, View Transitions API, Responsive Design, UI/UX Design",
        github_link="",
        live_demo="https://fluffy-sfogliatella-30de62.netlify.app/",
        featured=True,
        client="Concept project",
        duration="",
        problem=(
            "Many local clinics have outdated websites, or none at all, so patients can't quickly see "
            "the treatments on offer, trust the team or book a visit without calling during opening hours."
        ),
        solution=(
            "A calm, trustworthy design in teal and white that puts booking first. Every service page "
            "links to the appointment form with the treatment already selected, the form checks required "
            "fields and shows available time slots for the chosen date, and a friendly confirmation "
            "appears on submit. Dark mode follows the visitor's system setting and is remembered, and "
            "the layout is mobile-first so it works well on any phone."
        ),
        result=(
            "A ready-to-launch clinic website that builds trust at first glance, makes it simple to book "
            "an appointment from any device, and can be adapted for any dental or medical practice."
        ),
    )


def remove_project(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0014_add_nexcalc_chronix_atmos_projects"),
    ]

    operations = [
        migrations.RunPython(add_project, remove_project),
    ]
