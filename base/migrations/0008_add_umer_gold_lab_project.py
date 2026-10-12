from django.db import migrations


SLUG = "umer-gold-lab"


def add_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    if Project.objects.filter(slug=SLUG).exists():
        return
    Project.objects.create(
        title="Umer Gold Lab",
        slug=SLUG,
        description=(
            "A live business website for Umer Gold Lab, a gold and silver refinery in Faisalabad. "
            "It features live gold and silver rates, a QR code and serial number product verification "
            "system, a price calculator, a user login area and a premium white and gold design that "
            "works on every device."
        ),
        image="projects/umergoldlab.jpg",
        category="django",
        technologies="Python, Django, JavaScript, Bootstrap, Responsive Design",
        github_link="",
        live_demo="https://umergoldlab.com",
        featured=True,
    )


def remove_project(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0007_format_project_technologies"),
    ]

    operations = [
        migrations.RunPython(add_project, remove_project),
    ]
