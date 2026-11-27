"""
Who Rana Umar is, in one place.

Everything here comes from the CV (cv_source/cv.html) and the existing site,
so the About page, the Skills Universe, the terminal and the CV centre all
say the same thing. Edit this file to update them all at once.

Nothing is invented: no fake percentages, dates or achievements. Skill levels
use three honest labels instead of numbers.
"""

GITHUB_USERNAME = "uiux6006-star"
GITHUB_URL = f"https://github.com/{GITHUB_USERNAME}"
LINKEDIN_URL = "https://www.linkedin.com/in/rana-umar-476b19409"
# Paste your full TikTok profile link here, e.g. "https://www.tiktok.com/@yourname".
# While it's empty, no TikTok icon is shown anywhere on the site.
TIKTOK_URL = "https://www.tiktok.com/@legend765463"
EMAIL = "uiux6006@gmail.com"
WHATSAPP_NUMBER = "923238144826"
LOCATION = "Faisalabad, Pakistan"
CV_PATH = "cv/Rana_Umar_CV.pdf"  # inside /static/

ROLE = "Web Developer"
FUTURE_ROLE = "Future Python Developer"

SUMMARY = (
    "Full stack developer who builds fast, premium websites and web apps with Python, Django, "
    "JavaScript and Bootstrap. I have delivered a live production website for a gold & silver "
    "refinery, and I deploy and maintain my own Django projects, focused on clean UI and websites "
    "that turn visitors into customers."
)

# Honest skill levels (no percentages)
BUILDING = "Building Projects"
WORKING = "Working With"
LEARNING = "Learning"
LEVELS = [BUILDING, WORKING, LEARNING]

SKILL_GROUPS = [
    {"id": "frontend", "label": "Frontend", "icon": "fa-palette"},
    {"id": "backend", "label": "Backend", "icon": "fa-server"},
    {"id": "concepts", "label": "Programming Concepts", "icon": "fa-cubes"},
    {"id": "design", "label": "Design & Tools", "icon": "fa-pen-ruler"},
]

# `match` = words looked for in a project's technologies to link real projects.
SKILLS = [
    # ---------- Frontend ----------
    {
        "id": "html", "name": "HTML5", "group": "frontend", "icon": "fab fa-html5", "level": BUILDING,
        "about": "The structure of every page I build: semantic, accessible markup that search engines and screen readers understand.",
        "builds": ["Multi-page business websites", "Landing pages", "Accessible forms and layouts"],
        "related": ["css", "js", "responsive"], "match": ["html"],
    },
    {
        "id": "css", "name": "CSS3", "group": "frontend", "icon": "fab fa-css3-alt", "level": BUILDING,
        "about": "Layouts, colour systems and animations, from grid and flexbox to theme variables and smooth motion.",
        "builds": ["Premium themed designs", "Animated sections and hover effects", "Dark and light modes"],
        "related": ["html", "bootstrap", "responsive"], "match": ["css"],
    },
    {
        "id": "js", "name": "JavaScript", "group": "frontend", "icon": "fab fa-js", "level": BUILDING,
        "about": "Interactivity in the browser: dashboards, calculators, live clocks, filters, API calls and animations.",
        "builds": ["Interactive web apps", "Live data dashboards", "Animated, story-driven experiences"],
        "related": ["html", "css", "django"], "match": ["javascript"],
    },
    {
        "id": "bootstrap", "name": "Bootstrap", "group": "frontend", "icon": "fab fa-bootstrap", "level": BUILDING,
        "about": "A fast, reliable grid and component system I use to ship responsive business sites quickly.",
        "builds": ["Responsive business websites", "Admin-friendly page layouts"],
        "related": ["css", "responsive", "django"], "match": ["bootstrap"],
    },
    {
        "id": "responsive", "name": "Responsive Web Design", "group": "frontend", "icon": "fas fa-mobile-screen", "level": BUILDING,
        "about": "Mobile-first layouts tested on phones, tablets and desktops, so every visitor gets a great experience.",
        "builds": ["Sites that work on every screen", "Touch-friendly navigation and forms"],
        "related": ["css", "bootstrap", "html"], "match": ["responsive"],
    },

    # ---------- Backend ----------
    {
        "id": "python", "name": "Python", "group": "backend", "icon": "fab fa-python", "level": BUILDING,
        "about": "My main programming language, used for problem solving, management systems and Django web apps.",
        "builds": ["Management systems", "Automation and data handling", "Backend logic for web apps"],
        "related": ["oop", "django"], "match": ["python"],
    },
    {
        "id": "django", "name": "Django", "group": "backend", "icon": "fas fa-leaf", "level": BUILDING,
        "about": "Database-driven websites with admin panels, forms, email and secure logins. This portfolio itself runs on Django.",
        "builds": ["Business sites you can edit yourself", "Custom web apps and dashboards", "Lead and enquiry systems"],
        "related": ["python", "sqlite", "bootstrap", "js"], "match": ["django"],
    },
    {
        "id": "sqlite", "name": "SQLite & Django ORM", "group": "backend", "icon": "fas fa-database", "level": WORKING,
        "about": "Storing projects, leads, posts and settings through Django's ORM and migrations.",
        "builds": ["Content you manage from an admin panel", "Data migrations that update a live site safely"],
        "related": ["django", "python"], "match": ["sqlite"],
    },

    # ---------- Programming concepts ----------
    {
        "id": "oop", "name": "Object-Oriented Programming", "group": "concepts", "icon": "fas fa-cubes", "level": BUILDING,
        "about": "Organising code into classes and objects. My hospital, library and e-commerce management systems are built around it.",
        "builds": ["Management systems with clear structure", "Reusable, testable code"],
        "related": ["python", "encapsulation", "inheritance", "polymorphism", "association"], "match": ["oop", "classes"],
    },
    {
        "id": "encapsulation", "name": "Encapsulation", "group": "concepts", "icon": "fas fa-lock", "level": WORKING,
        "about": "Keeping an object's data private and exposing only safe methods, so records can't be changed by accident.",
        "builds": ["Safe data models for patients, books and orders"],
        "related": ["oop", "inheritance"], "match": ["oop"],
    },
    {
        "id": "inheritance", "name": "Inheritance", "group": "concepts", "icon": "fas fa-sitemap", "level": WORKING,
        "about": "Sharing behaviour between related classes, like different user or item types built on one base class.",
        "builds": ["Class hierarchies without repeated code"],
        "related": ["oop", "polymorphism", "encapsulation"], "match": ["oop"],
    },
    {
        "id": "polymorphism", "name": "Polymorphism", "group": "concepts", "icon": "fas fa-shapes", "level": WORKING,
        "about": "One interface, many behaviours: the same method doing the right thing for each kind of object.",
        "builds": ["Flexible features that are easy to extend"],
        "related": ["oop", "inheritance"], "match": ["oop"],
    },
    {
        "id": "association", "name": "Association", "group": "concepts", "icon": "fas fa-link", "level": WORKING,
        "about": "Objects that work together while staying independent, like a doctor and a patient in an appointment.",
        "builds": ["Real-world relationships in code"],
        "related": ["oop", "aggregation", "composition"], "match": ["oop"],
    },
    {
        "id": "aggregation", "name": "Aggregation", "group": "concepts", "icon": "fas fa-object-group", "level": WORKING,
        "about": "A whole that holds parts which can also live on their own, like a library holding books.",
        "builds": ["Collections of independent records"],
        "related": ["association", "composition", "oop"], "match": ["oop"],
    },
    {
        "id": "composition", "name": "Composition", "group": "concepts", "icon": "fas fa-puzzle-piece", "level": WORKING,
        "about": "A whole made of parts that only exist inside it, like an order and its line items.",
        "builds": ["Tightly structured models such as orders and bills"],
        "related": ["aggregation", "association", "oop"], "match": ["oop"],
    },

    # ---------- Design & tools ----------
    {
        "id": "figma", "name": "Figma", "group": "design", "icon": "fab fa-figma", "level": WORKING,
        "about": "Planning layouts and UI before code, so clients can see and approve the design first.",
        "builds": ["Website mock-ups and UI designs"],
        "related": ["photoshop", "css"], "match": [],
    },
    {
        "id": "photoshop", "name": "Adobe Photoshop", "group": "design", "icon": "fas fa-image", "level": WORKING,
        "about": "Preparing and editing images, banners and graphics for websites.",
        "builds": ["Web-ready images and banners"],
        "related": ["figma"], "match": [],
    },
    {
        "id": "git", "name": "Git & GitHub", "group": "design", "icon": "fab fa-git-alt", "level": WORKING,
        "about": "Version control for every project, and the way this portfolio is deployed to PythonAnywhere.",
        "builds": ["Clean project history", "Safe, repeatable deployments"],
        "related": ["django", "python"], "match": [],
    },
]

# Learning path, in order. No invented dates: years only where the CV gives them.
JOURNEY = [
    {"title": "HTML & CSS", "icon": "fas fa-seedling", "skills": ["html", "css"],
     "text": "Where it started: building layouts and pages from scratch and learning how the web is structured."},
    {"title": "JavaScript", "icon": "fab fa-js", "skills": ["js"],
     "text": "Adding interactivity: menus, sliders, forms and later full browser apps like dashboards and calculators."},
    {"title": "Bootstrap & Responsive Design", "icon": "fab fa-bootstrap", "skills": ["bootstrap", "responsive"],
     "text": "Shipping mobile-friendly business websites quickly, like Royal Stitch and Rana Umar Jewellers."},
    {"title": "Python", "icon": "fab fa-python", "skills": ["python"],
     "text": "A real programming language for logic and problem solving, and the base for everything backend."},
    {"title": "Object-Oriented Programming", "icon": "fas fa-cubes",
     "skills": ["oop", "encapsulation", "inheritance", "polymorphism"],
     "text": "Hospital, library and e-commerce management systems built with classes, file handling and clean structure."},
    {"title": "Django", "icon": "fas fa-leaf", "skills": ["django", "sqlite"],
     "text": "Full stack web development: databases, admin panels, forms, email and deployment."},
    {"title": "Real client work", "icon": "fas fa-briefcase", "skills": ["django", "js", "bootstrap"], "when": "2026 — Present",
     "text": "Freelance full stack developer. Built and launched Umer Gold Lab with live rates and QR product verification."},
    {"title": "Next: Python Developer", "icon": "fas fa-rocket", "skills": ["python", "django"], "next": True,
     "text": "Going deeper into Python and Django to build larger, more advanced applications."},
]

EXPERIENCE = [
    {
        "role": "Freelance Full Stack Developer",
        "when": "2026 — Present",
        "where": "Self-employed · Faisalabad, Pakistan",
        "points": [
            "Built and launched Umer Gold Lab with live rates and QR product verification.",
            "Built and deployed my own Django portfolio with contact leads and admin panel.",
            "Own the full process: requirements, UI design, development and deployment.",
        ],
    },
]

EDUCATION = [
    {"title": "F.A. (IT)", "when": "2025 — 2027 · In progress", "where": "Govt. Crescent College, Faisalabad"},
    {"title": "Matric (Science)", "when": "2023 — 2024", "where": "Govt. Crescent High School, Faisalabad"},
]

COURSES = [
    "Python Programming",
    "Django for Beginners",
    "Web Development (HTML, CSS, JS)",
    "Responsive Web Design",
    "Git & GitHub",
]

LANGUAGES = ["Urdu", "Punjabi", "English"]

# Freelance services. `projects` is a query for the Projects page filter.
SERVICES = [
    {"id": "business", "name": "Business Website Development", "icon": "fa-store",
     "text": "Modern websites for businesses and brands that build trust and bring in enquiries.",
     "deliverables": ["Custom design", "Contact form & WhatsApp", "Mobile-first layout"],
     "tech": ["HTML", "CSS", "Bootstrap", "Django"], "projects": "kind=business", "estimate": "business"},
    {"id": "ecommerce", "name": "E-commerce Website Development", "icon": "fa-cart-shopping",
     "text": "Online stores with product catalogues, cart systems and custom functionality.",
     "deliverables": ["Products & categories", "Cart & checkout", "Admin to manage stock"],
     "tech": ["Django", "Python", "JavaScript"], "projects": "q=e-commerce", "estimate": "ecommerce"},
    {"id": "django", "name": "Django Web Development", "icon": "fa-server",
     "text": "Database-driven web apps, admin panels, backend functionality and custom systems.",
     "deliverables": ["Database design", "Admin panel", "Secure forms & email"],
     "tech": ["Python", "Django", "SQLite"], "projects": "category=django", "estimate": "webapp"},
    {"id": "frontend", "name": "Frontend Development", "icon": "fa-wand-magic-sparkles",
     "text": "Responsive layouts, interactive interfaces, animations and modern website UI.",
     "deliverables": ["Pixel-perfect UI", "Smooth animations", "Fast, accessible pages"],
     "tech": ["HTML", "CSS", "JavaScript", "GSAP"], "projects": "category=frontend", "estimate": "landing"},
    {"id": "redesign", "name": "Website Redesign", "icon": "fa-rotate",
     "text": "Transform an outdated website into a modern, fast and professional experience.",
     "deliverables": ["Fresh modern design", "Better speed", "Mobile-friendly rebuild"],
     "tech": ["HTML", "CSS", "JavaScript", "Django"], "projects": "", "contact_type": "redesign"},
    {"id": "maintenance", "name": "Website Maintenance", "icon": "fa-screwdriver-wrench",
     "text": "Updates, bug fixes, optimisation and ongoing support after your site is live.",
     "deliverables": ["Content updates", "Bug fixing", "Speed & security checks"],
     "tech": ["Django", "JavaScript", "PythonAnywhere"], "projects": "", "contact_type": "other"},
]


def skill_by_id():
    return {s["id"]: s for s in SKILLS}


def projects_for_skill(skill, projects):
    """Real projects whose technologies mention one of the skill's keywords."""
    words = [w.lower() for w in skill.get("match", [])]
    if not words:
        return []
    found = []
    for p in projects:
        techs = " | ".join(t.lower() for t in p.tech_list)
        if any(w in techs for w in words):
            found.append(p)
    return found
