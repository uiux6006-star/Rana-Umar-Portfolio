from django.db import migrations


# Old space-separated values -> new comma-separated values (edited locally via admin).
TECHNOLOGIES = {
    "Python OOP File Handling Console Application": "Python, OOP, File Handling, Console App",
    "Python OOP File Handling Classes": "Python, OOP, File Handling, Classes",
    "Python OOP File Handling Management System": "Python, OOP, File Handling",
    "HTML CSS Bootstrap JavaScript Responsive Design": "HTML, CSS, Bootstrap, JavaScript, Responsive Design",
    "HTML CSS Bootstrap JavaScript UI UX Design": "HTML, CSS, Bootstrap, JavaScript, UI/UX Design",
}


def format_technologies(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    for old, new in TECHNOLOGIES.items():
        Project.objects.filter(technologies=old).update(technologies=new)


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0006_testimonial_contactmessage_budget_and_more"),
    ]

    operations = [
        migrations.RunPython(format_technologies, migrations.RunPython.noop),
    ]
