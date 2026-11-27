from django.db import migrations


# Latest showcase videos from @legend765463, newest first. Titles are the
# videos' own captions, shortened. Thumbnails are stored in media/tiktok/.
VIDEOS = [
    ("7712666950576491797", "ZAAYKAA — Where Taste Meets Elegance"),
    ("7712398121480752405", "Turning ideas into reality 💻 Every line of code tells a story."),
    ("7712396186136759558", "Digital Security. Redefined. Introducing VAULTIX"),
    ("7710815634019454229", "Not just a clock, it's CHRONIX. Time management meets premium design."),
]


def add_videos(apps, schema_editor):
    TikTokVideo = apps.get_model("base", "TikTokVideo")
    for order, (video_id, title) in enumerate(VIDEOS):
        if TikTokVideo.objects.filter(video_id=video_id).exists():
            continue
        TikTokVideo.objects.create(
            url=f"https://www.tiktok.com/@legend765463/video/{video_id}",
            video_id=video_id,
            title=title,
            thumbnail=f"tiktok/{video_id}.jpg",
            order=order,
            is_published=True,
        )


def remove_videos(apps, schema_editor):
    apps.get_model("base", "TikTokVideo").objects.filter(video_id__in=[v for v, _ in VIDEOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0021_tiktok_videos"),
    ]

    operations = [
        migrations.RunPython(add_videos, remove_videos),
    ]
