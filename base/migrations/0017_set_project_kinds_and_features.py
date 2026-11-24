from django.db import migrations


# Project type for the Projects page filters.
KINDS = {
    "hospital-management-system": "system",
    "library-management-system": "system",
    "e-commerce-management-system": "system",
    "royal-stitch": "business",
    "rana-umar-jewellers": "business",
    "umer-gold-lab": "business",
    "dentora-dental-clinic": "business",
    "atmos-weather-dashboard": "webapp",
    "chronix-time-dashboard": "webapp",
    "nexcalc-calculator": "webapp",
    "universe-explorer": "experience",
    "eternal-wedding-invitation": "experience",
    "royal-world-of-queen": "experience",
}

# Key features, taken only from the CV, the existing project descriptions or
# the live sites' own code. Nothing invented.
FEATURES = {
    "hospital-management-system": [
        "Patient records", "Doctor management", "Appointments", "Billing", "Pharmacy", "Reports",
    ],
    "library-management-system": [
        "Book catalogue", "Member records", "Issuing books", "Returns", "Record keeping",
    ],
    "e-commerce-management-system": [
        "Customer management", "Inventory", "Cart", "Order processing", "Billing",
    ],
    "royal-stitch": [
        "Luxury black and gold design", "Smooth animations", "Responsive layout",
    ],
    "rana-umar-jewellers": [
        "Luxury jewellery branding", "Responsive layout",
    ],
    "umer-gold-lab": [
        "Live gold and silver market rates", "QR code product authentication",
        "Price calculator", "Premium white and gold design",
    ],
    "universe-explorer": [
        "3D Solar System and Milky Way", "Flyable spaceship with autopilot", "Galaxy Creator with PNG export",
        "Live flight telemetry", "Quality settings from Low to Ultra", "Ambient sound and exploration log",
    ],
    "eternal-wedding-invitation": [
        "Wax-seal envelope opening", "Separate Mehndi, Baraat and Walima pages", "Live countdown",
        "Venue details with Google Maps", "Photo gallery", "RSVP sent to WhatsApp",
        "Background music and falling petals",
    ],
    "royal-world-of-queen": [
        "Animated palace gates entrance", "Wax-sealed private letter", "Timeline with calendar dates",
        "Gallery of moments", "Flip cards of reasons", "Built-in music player",
        "Canvas petals, hearts and glow", "Everything editable from one config file",
    ],
    "nexcalc-calculator": [
        "Standard, Scientific, Programmer and Unit Converter modes", "Safe expression parser (no eval)",
        "HEX, DEC, OCT and BIN with a bit toggler", "BigInt engine for exact 64-bit values",
        "History, memory and constants", "Keyboard shortcuts", "Dark and light themes",
    ],
    "chronix-time-dashboard": [
        "Live clock in 12 or 24 hours", "Day and year progress", "Calendar with week number",
        "World clock with time differences", "Stopwatch with lap history",
        "Countdown with presets and alert sound", "Dark and light modes",
    ],
    "atmos-weather-dashboard": [
        "Live weather for any city", "24-hour and 7-day forecasts", "Sunrise and sunset arc",
        "Humidity, wind, UV, visibility and pressure", "Smart activity insights",
        "Interactive map with live conditions", "Compare two cities", "Celsius or Fahrenheit",
    ],
    "dentora-dental-clinic": [
        "Seven pages: Home, Services, Team, About, Reviews, FAQs, Contact",
        "Appointment form with date and time slots", "Service links pre-fill the treatment",
        "Dark mode with circular reveal", "Search overlay", "Testimonial slider and FAQ filters",
        "WhatsApp button",
    ],
}


def apply(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    for project in Project.objects.filter(slug__in=list(KINDS) + list(FEATURES)):
        changed = []
        # Never overwrite something already filled in from the admin
        if not project.kind and project.slug in KINDS:
            project.kind = KINDS[project.slug]
            changed.append("kind")
        if not project.features.strip() and project.slug in FEATURES:
            project.features = "\n".join(FEATURES[project.slug])
            changed.append("features")
        if changed:
            project.save(update_fields=changed)


def undo(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    Project.objects.filter(slug__in=list(KINDS)).update(kind="")


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0016_project_kind_features_challenges"),
    ]

    operations = [
        migrations.RunPython(apply, undo),
    ]
