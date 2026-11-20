from django.db import migrations


# Created oldest first, so ATMOS ends up newest and is listed first.
PROJECTS = [
    {
        "title": "NEXCALC Ultimate Calculator",
        "slug": "nexcalc-calculator",
        "description": (
            "An ultra-premium calculator app with four modes in one dashboard: Standard, Scientific, "
            "Programmer and Unit Converter. It handles trigonometry, logarithms, powers and roots in "
            "degrees or radians, a programmer mode with HEX, DEC, OCT and BIN side by side and a "
            "clickable bit toggler, and a unit converter that accepts expressions like 5*12. "
            "Calculation history, memory keys, scientific constants, keyboard shortcuts and dark or "
            "light themes are all built in, and everything is saved in the browser."
        ),
        "image": "projects/nexcalc-calculator.jpg",
        "technologies": "HTML5, CSS3, JavaScript, BigInt, LocalStorage, Responsive Design",
        "live_demo": "https://comfy-marzipan-34324b.netlify.app/",
        "problem": (
            "Most online calculators do one job, look dated and are full of ads. Students and "
            "developers end up switching between separate tools for scientific maths, number "
            "systems and unit conversions."
        ),
        "solution": (
            "One fast, focused app with four calculators that share the same history and memory. "
            "A safe expression parser evaluates input without eval, the programmer mode uses BigInt "
            "so large 64-bit values stay exact, and every button has a keyboard shortcut. Settings, "
            "history and memory are stored locally so they are still there on the next visit."
        ),
        "result": (
            "A polished, accessible calculator that works smoothly on desktop and mobile, replaces "
            "several single-purpose tools and runs entirely in the browser with no sign-up."
        ),
    },
    {
        "title": "CHRONIX Time Dashboard",
        "slug": "chronix-time-dashboard",
        "description": (
            "A premium digital time dashboard. A large live clock switches between 12 and 24 hours "
            "and shows day and year progress, a date panel tracks week number, day of the year and "
            "days remaining, and a world clock pins cities like Karachi, Dubai, London and New York "
            "with the time difference from you. A stopwatch with lap history and a countdown timer "
            "with quick presets and an alert sound complete the toolkit, with dark and light modes."
        ),
        "image": "projects/chronix-time.jpg",
        "technologies": "HTML5, CSS3, JavaScript, Intl API, LocalStorage, Responsive Design",
        "live_demo": "https://peppy-truffle-88a180.netlify.app/",
        "problem": (
            "Clocks, world time, stopwatches and timers usually live in different apps or cluttered "
            "websites, which makes something as simple as checking a client's time zone or timing a "
            "task feel scattered."
        ),
        "solution": (
            "A single elegant workspace that brings them together. Time zones are calculated with the "
            "browser's Intl API, so any city can be added to the world clock, while the stopwatch and "
            "countdown keep running in the background and are visible from the overview. Pinned "
            "cities, the time format, theme and alert sound are remembered between visits."
        ),
        "result": (
            "A clean, distraction-free dashboard that is accurate to the second, easy to read on any "
            "screen and useful every day for remote work across time zones."
        ),
    },
    {
        "title": "ATMOS Weather Dashboard",
        "slug": "atmos-weather-dashboard",
        "description": (
            "A live global weather dashboard that works for any city in the world. Search a city or "
            "use your location to see current conditions, a 24-hour forecast, a 7-day outlook and a "
            "sunrise and sunset arc. Detailed metrics cover humidity, wind, UV index, visibility, "
            "pressure and feels-like temperature, smart insights suggest the best time for outdoor "
            "activities, an interactive map shows live conditions anywhere you click, and a compare "
            "view puts two cities head to head. Data comes from the Open-Meteo API, with Celsius or "
            "Fahrenheit and dark or light themes."
        ),
        "image": "projects/atmos-weather.jpg",
        "technologies": "HTML5, CSS3, JavaScript, Open-Meteo API, Leaflet, Geolocation, LocalStorage",
        "live_demo": "https://lambent-fenglisu-0624f9.netlify.app/",
        "problem": (
            "Popular weather sites are crowded with ads and raw numbers, so it is hard to quickly "
            "understand what the weather actually means for your day."
        ),
        "solution": (
            "A calm, dashboard-style app that turns forecast data into clear answers. It fetches live "
            "forecasts and city search results from the Open-Meteo API, then explains them with "
            "insight cards for comfort, UV, wind and the best time to go out. Favourite locations, "
            "units and theme are saved in the browser, and a city comparison view helps plan travel."
        ),
        "result": (
            "A fast, real-time weather experience for any city that is easy to read at a glance, works "
            "on mobile and desktop, and needs no API key or sign-up."
        ),
    },
]


def add_projects(apps, schema_editor):
    Project = apps.get_model("base", "Project")
    for data in PROJECTS:
        if Project.objects.filter(slug=data["slug"]).exists():
            continue
        Project.objects.create(
            category="frontend",
            github_link="",
            featured=True,
            client="Personal project",
            duration="",
            **data,
        )


def remove_projects(apps, schema_editor):
    apps.get_model("base", "Project").objects.filter(
        slug__in=[p["slug"] for p in PROJECTS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0013_add_royal_world_of_queen_project"),
    ]

    operations = [
        migrations.RunPython(add_projects, remove_projects),
    ]
