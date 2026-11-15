from django.db import migrations


SLUG = "universe-explorer"


def add_project(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    if Project.objects.filter(slug=SLUG).exists():
        return
    Project.objects.create(
        title="Universe Explorer",
        slug=SLUG,
        description=(
            "A cinematic, interactive 3D journey from Earth to the Milky Way, built with Three.js. "
            "Visitors can explore the Solar System, fly a spaceship with keyboard controls and "
            "autopilot, discover nebulae, and design their own galaxy in the Galaxy Creator, "
            "then save it as an image. It includes live flight telemetry, quality settings from "
            "Low to Ultra, ambient sound and an exploration log of discoveries."
        ),
        image="projects/universe-explorer.jpg",
        category="frontend",
        technologies="Three.js, WebGL, JavaScript, GSAP, HTML5, CSS3",
        github_link="",
        live_demo="https://stately-mooncake-cda4a5.netlify.app/",
        featured=True,
        duration="",
        client="Personal project",
        problem=(
            "Space is hard to picture. Most astronomy websites are flat pages of text and photos, "
            "so the scale of planets, the Sun and our galaxy never really sinks in."
        ),
        solution=(
            "A real-time 3D experience that runs in the browser with no installs. "
            "A modular Three.js engine renders the Solar System, the Milky Way, procedural nebulae "
            "and a flyable spaceship, with GSAP-powered camera moves between destinations. "
            "The Galaxy Creator lets visitors tweak stars, spiral arms, colours and rotation "
            "and export their galaxy as a PNG."
        ),
        result=(
            "An immersive, shareable experience that works on desktop and mobile, adapts its "
            "graphics quality to the device, and shows advanced 3D, animation and performance skills."
        ),
    )


def remove_project(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0010_lead_status_notes"),
    ]

    operations = [
        migrations.RunPython(add_project, remove_project),
    ]
