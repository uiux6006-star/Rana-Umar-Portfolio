"""
Theme definitions and the colour maths that turns 6 brand colours into a
full design system (dark + light) of CSS custom properties.

To add a theme: add an entry to THEMES. Nothing else needs to change.
"""

import re
from functools import lru_cache

ORIGINAL = "original"

HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


# ---------------------------------------------------------------------------
#  The 8 themes
#  bg / surface / primary / accent / text / muted  -> the brand palette
#  font / radius / tracking / glow                  -> the "personality"
# ---------------------------------------------------------------------------

THEMES = {
    ORIGINAL: {
        "name": "Original",
        "tagline": "Your current RUD look: deep navy, electric cyan, crisp edges.",
        "tags": ["tech", "default"],
        "bg": "#070b16", "surface": "#0d1526",
        "primary": "#69d7ff", "accent": "#a5e8ff",
        "text": "#eef3ff", "muted": "#8f9db6",
        "font": "manrope", "radius": "sharp",
    },
    "royal-gold": {
        "name": "Royal Gold Luxury",
        "tagline": "Black and metallic gold with elegant serif headlines.",
        "tags": ["luxury"],
        "bg": "#08090d", "surface": "#111318",
        "primary": "#d4af37", "accent": "#f5d76e",
        "text": "#ffffff", "muted": "#a1a1aa",
        "font": "serif", "radius": "pill",
    },
    "midnight-blue": {
        "name": "Midnight Blue",
        "tagline": "Calm, professional developer aesthetic in sky blue.",
        "tags": ["tech"],
        "bg": "#0b1120", "surface": "#111c32",
        "primary": "#38bdf8", "accent": "#60a5fa",
        "text": "#e2e8f0", "muted": "#94a3b8",
        "font": "manrope", "radius": "soft",
    },
    "cyber-purple": {
        "name": "Cyber Purple",
        "tagline": "Futuristic and creative with a soft violet glow.",
        "tags": ["creative", "tech"],
        "bg": "#09090b", "surface": "#18181b",
        "primary": "#a855f7", "accent": "#c084fc",
        "text": "#fafafa", "muted": "#a1a1aa",
        "font": "manrope", "radius": "soft",
    },
    "ocean-teal": {
        "name": "Ocean Teal",
        "tagline": "Clean, elegant and calm. Great for corporate clients.",
        "tags": ["professional"],
        "bg": "#0f172a", "surface": "#172033",
        "primary": "#14b8a6", "accent": "#2dd4bf",
        "text": "#f8fafc", "muted": "#94a3b8",
        "font": "manrope", "radius": "round",
    },
    "sunset-orange": {
        "name": "Sunset Orange",
        "tagline": "Bold charcoal and orange. Energetic and confident.",
        "tags": ["bold"],
        "bg": "#111827", "surface": "#1f2937",
        "primary": "#f97316", "accent": "#fb923c",
        "text": "#fff7ed", "muted": "#9ca3af",
        "font": "manrope", "radius": "round",
    },
    "neon-hacker": {
        "name": "Neon Hacker",
        "tagline": "Terminal green and monospace type for a coder vibe.",
        "tags": ["tech", "bold"],
        "bg": "#020617", "surface": "#0f172a",
        "primary": "#22c55e", "accent": "#4ade80",
        "text": "#f1f5f9", "muted": "#94a3b8",
        "font": "mono", "radius": "sharp",
    },
    "neon-pink": {
        "name": "Neon Pink",
        "tagline": "Stylish and distinctive. Stands out from every other portfolio.",
        "tags": ["creative", "bold"],
        "bg": "#18181b", "surface": "#27272a",
        "primary": "#ec4899", "accent": "#f472b6",
        "text": "#fff1f2", "muted": "#a1a1aa",
        "font": "manrope", "radius": "round",
    },
}

THEME_CHOICES = [(slug, t["name"]) for slug, t in THEMES.items()]

FONTS = {
    "manrope": {
        "heading": '"Manrope", "Segoe UI", sans-serif',
        "tracking": "-.055em",
        "google": None,  # already loaded by base.html
    },
    "serif": {
        "heading": '"Playfair Display", Georgia, serif',
        "tracking": "-.02em",
        "google": "family=Playfair+Display:wght@600;700;800",
    },
    "mono": {
        "heading": '"DM Mono", ui-monospace, monospace',
        "tracking": "-.04em",
        "google": None,
    },
}

RADII = {
    "sharp": ("2px", "2px"),
    "soft": ("10px", "8px"),
    "round": ("14px", "10px"),
    "pill": ("999px", "999px"),
}


# ---------------------------------------------------------------------------
#  Colour helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def mix(a, b, amount):
    """Mix hex colour a toward b by `amount` (0..1)."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex([x + (y - x) * amount for x, y in zip(ra, rb)])


def rgb_triplet(value):
    return " ".join(str(c) for c in hex_to_rgb(value))


def luminance(value):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in hex_to_rgb(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def darken_until(color, against, ratio):
    """Darken `color` until it reaches `ratio` contrast against `against`."""
    step = 0.0
    result = color
    while contrast(result, against) < ratio and step < 1:
        step += 0.04
        result = mix(color, "#000000", step)
    return result


def readable_on(color, dark="#07101c", light="#ffffff"):
    """Text colour for content placed on top of `color`."""
    return dark if contrast(color, dark) >= contrast(color, light) else light


# ---------------------------------------------------------------------------
#  Theme -> CSS custom properties
# ---------------------------------------------------------------------------

@lru_cache(maxsize=64)
def build_tokens(slug, custom_accent=""):
    """Return {"dark": {...}, "light": {...}, "shared": {...}} CSS variables."""

    theme = THEMES.get(slug, THEMES[ORIGINAL])
    if custom_accent and not HEX_RE.match(custom_accent):
        custom_accent = ""  # never let an unchecked value reach the page's <style>
    bg, surface = theme["bg"], theme["surface"]
    text, muted = theme["text"], theme["muted"]
    primary = custom_accent or theme["primary"]
    accent = mix(custom_accent, "#ffffff", 0.3) if custom_accent else theme["accent"]

    dark = {
        "--bg": bg,
        "--bg-alt": mix(bg, surface, 0.35),
        "--surface": surface,
        "--surface-2": mix(surface, text, 0.05),
        "--surface-rgb": rgb_triplet(surface),
        "--input-bg": mix(bg, surface, 0.5),
        "--text": text,
        "--text-soft": mix(text, muted, 0.45),
        "--text-muted": muted,
        "--text-dim": mix(muted, bg, 0.28),
        "--accent": primary,
        "--accent-2": accent,
        "--accent-rgb": rgb_triplet(primary),
        "--on-accent": readable_on(primary, dark=mix(bg, "#000000", 0.4)),
        "--fg-rgb": rgb_triplet(muted),
        "--line": f"rgb({rgb_triplet(muted)} / .15)",
        "--shadow-rgb": "0 0 0",
        "--shadow-k": "1",
        "--nav-bg": f"rgb({rgb_triplet(bg)} / .85)",
        "--nav-bg-solid": f"rgb({rgb_triplet(bg)} / .96)",
        "--grid-line": f"rgb({rgb_triplet(muted)} / .055)",
        "--glow": f"rgb({rgb_triplet(primary)} / .16)",
        "color-scheme": "dark",
    }

    # Light mode: neutral paper tinted with the brand colour, and a primary
    # darkened just enough to pass WCAG AA (4.5:1) as text on white.
    light_bg = mix("#f6f7fb", primary, 0.035)
    light_primary = darken_until(primary, "#ffffff", 4.5)
    light_accent = darken_until(accent, "#ffffff", 3.0)

    light = {
        "--bg": light_bg,
        "--bg-alt": mix("#eef1f6", primary, 0.04),
        "--surface": "#ffffff",
        "--surface-2": mix("#f8fafc", primary, 0.02),
        "--surface-rgb": "255 255 255",
        "--input-bg": "#ffffff",
        "--text": "#0b1324",
        "--text-soft": "#334155",
        "--text-muted": "#52607a",
        "--text-dim": "#74819a",
        "--accent": light_primary,
        "--accent-2": light_accent,
        "--accent-rgb": rgb_triplet(light_primary),
        "--on-accent": readable_on(light_primary),
        "--fg-rgb": "15 23 42",
        "--line": "rgb(15 23 42 / .1)",
        "--shadow-rgb": "30 45 80",
        "--shadow-k": ".3",
        "--nav-bg": f"rgb({rgb_triplet(light_bg)} / .85)",
        "--nav-bg-solid": f"rgb({rgb_triplet(light_bg)} / .96)",
        "--grid-line": "rgb(15 23 42 / .05)",
        "--glow": f"rgb({rgb_triplet(light_primary)} / .12)",
        "color-scheme": "light",
    }

    font = FONTS[theme["font"]]
    radius_btn, radius_sm = RADII[theme["radius"]]

    shared = {
        "--glow-rgb": rgb_triplet(primary),
        "--radius-btn": radius_btn,
        "--radius-sm": radius_sm,
        "--hero-tracking": font["tracking"],
        "--font-heading": font["heading"],
    }

    return {"dark": dark, "light": light, "shared": shared}


def _declarations(tokens):
    return "".join(f"{name}:{value};" for name, value in tokens.items())


@lru_cache(maxsize=64)
def build_css(slug, custom_accent=""):
    """Inline CSS for the public site. Empty for the untouched Original theme,
    so the stylesheet's own values are used exactly as they are."""

    if custom_accent and not HEX_RE.match(custom_accent):
        custom_accent = ""

    if slug == ORIGINAL and not custom_accent:
        return ""

    tokens = build_tokens(slug, custom_accent)

    if slug == ORIGINAL:
        # Keep the original palette; only swap the accent family.
        keep = ("--accent", "--accent-2", "--accent-rgb", "--on-accent", "--glow")
        dark = {k: v for k, v in tokens["dark"].items() if k in keep}
        light = {k: v for k, v in tokens["light"].items() if k in keep}
        shared = {"--glow-rgb": tokens["shared"]["--glow-rgb"]}
    else:
        dark, light, shared = tokens["dark"], tokens["light"], tokens["shared"]

    # html[...] beats the stylesheet's :root / [data-bs-theme] selectors
    # without needing !important.
    return (
        f"html[data-site-theme]{{{_declarations(shared)}}}"
        f"html[data-bs-theme=\"dark\"]{{{_declarations(dark)}}}"
        f"html[data-bs-theme=\"light\"]{{{_declarations(light)}}}"
    )


def google_font_query(slug):
    theme = THEMES.get(slug, THEMES[ORIGINAL])
    return FONTS[theme["font"]]["google"]


def swatches(slug):
    theme = THEMES[slug]
    return [
        {"label": "Background", "value": theme["bg"]},
        {"label": "Primary", "value": theme["primary"]},
        {"label": "Accent", "value": theme["accent"]},
        {"label": "Text", "value": theme["text"]},
    ]
