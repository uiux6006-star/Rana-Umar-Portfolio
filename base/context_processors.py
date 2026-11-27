from . import profile


def social_links(request):
    """Social profile links for every template, set once in base/profile.py."""
    return {
        "social": {
            "github": profile.GITHUB_URL,
            "linkedin": profile.LINKEDIN_URL,
            "tiktok": profile.TIKTOK_URL,
            "whatsapp": f"https://wa.me/{profile.WHATSAPP_NUMBER}",
            "email": profile.EMAIL,
        }
    }
