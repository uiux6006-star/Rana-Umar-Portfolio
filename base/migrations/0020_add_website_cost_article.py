from django.db import migrations


SLUG = "how-much-does-a-website-cost-in-pakistan"

TITLE = "How Much Does a Website Cost in Pakistan? A Clear 2026 Guide"

EXCERPT = (
    "Real starting prices for landing pages, business websites, online stores and custom web apps, "
    "what changes the price, and how to avoid paying twice."
)

BODY = """\
"How much will my website cost?" is the first question almost every client asks me, and it's a fair one. The honest answer is that it depends on what you need. But "it depends" isn't very helpful when you're planning a budget, so in this guide I'll show you my actual starting prices, explain what pushes a price up or down, and share a few tips so you don't end up paying for the same website twice.

All prices below are in Pakistani rupees and are my own rates for 2026. Other developers and agencies will charge differently, but the factors that decide the price are the same everywhere.

## Quick answer: starting prices

Here is where each type of website starts:

- **Landing page or portfolio:** from **Rs 15,000**. One focused page, usually ready in about 5 days.
- **Business or brand website:** from **Rs 30,000**. Around 5 pages, usually about 10 days.
- **Online store (e-commerce):** from **Rs 70,000**. Products, categories, cart and checkout, usually about 3 weeks.
- **Custom web app or management system:** from **Rs 90,000**. Built with Python and Django, usually about a month.

These are starting points, not final quotes. Your exact price depends on the things below.

## What actually changes the price

### 1. The number of pages

Every page needs its own design and content: Home, About, Services, Contact and so on. Each extra page beyond the package adds around **Rs 3,000**. In an online store, product pages don't count, so you can add as many products as you like.

### 2. Features

Features are where most of the cost comes from, because each one is real work behind the scenes. Here are some common ones and what I charge for them:

- **Admin panel** so you can edit text, images and products yourself: + Rs 15,000
- **Online payments** with JazzCash, Easypaisa or card: + Rs 15,000
- **Appointment or booking system:** + Rs 12,000
- **English and Urdu** (two languages): + Rs 12,000
- **Blog or news section:** + Rs 10,000
- **SEO setup** so Google can find and understand your site: + Rs 8,000
- **Domain and hosting setup:** + Rs 5,000
- **WhatsApp chat and order button:** + Rs 3,000

You don't need all of these. A small business website might only need a contact form and a WhatsApp button, while an online store will need payments and an admin panel.

### 3. Design

A clean, simple design built from proven layouts keeps the price low. A **premium custom design**, made from scratch around your brand with custom animations and details, takes more time and adds about **30%**.

### 4. Deadline

If you need your website urgently, I can move it to the front of the queue. Priority delivery adds about **25%**, because it means working extra hours to hit your date.

## Costs people forget about

Some costs aren't part of building the website, but you will still pay them:

- **Domain name** (like yourbusiness.pk or .com): renewed every year.
- **Hosting** (the server your website lives on): usually paid monthly or yearly. A simple business site needs much less than an online store with many visitors.
- **Content:** good photos and well-written text make a huge difference. If you don't have them, budget time or money for them.
- **Updates and fixes after launch:** websites need small changes over time, like new prices, new products or a fresh offer.

Always ask your developer which of these are included in the quote, so there are no surprises later.

## Why a very cheap website often costs more

It's tempting to go for the lowest price you can find. But a website that's slow, breaks on mobile phones or can't be updated without calling the developer every time usually ends up being rebuilt, and then you pay twice. Before you choose, check that:

- The site works properly on **mobile phones**, where most of your visitors will be.
- It **loads fast**, even on a normal mobile connection.
- You can **update it yourself**, or you know exactly what updates will cost.
- You get a **clear written quote** with everything listed.
- You can see **real, live websites** the developer has built before.

## How to save money (the smart way)

- **Start small.** Launch with the pages and features you need today and add more later. A good website is easy to grow.
- **Prepare your content early.** Having your text, logo and photos ready saves days of back-and-forth.
- **Skip what you won't use.** A booking system is great for a clinic, but a clothing brand probably needs a store instead.
- **Give yourself time.** Avoiding a rush deadline alone can save you around a quarter of the cost.

## Get your own estimate in a minute

Every project is different, so the best way to know your price is to try my free **Project Planner** on this website. Pick your website type, number of pages and features, and it shows you a price range and timeline instantly, with no sign-up. You can then send me the details by email or WhatsApp and I'll reply with an exact quote, usually within a day.

Have a question that isn't answered here? Send me a message from the Contact page. I'm always happy to help you figure out what you really need.
"""


def add_post(apps, schema_editor):
    Post = apps.get_model("base", "Post")
    if Post.objects.filter(slug=SLUG).exists():
        return
    Post.objects.create(
        title=TITLE,
        slug=SLUG,
        excerpt=EXCERPT,
        body=BODY,
        tags="Pricing, Business, Pakistan, Web Development",
        # Saved as a draft: review it in the admin, then tick "Is published".
        is_published=False,
    )


def remove_post(apps, schema_editor):
    apps.get_model("base", "Post").objects.filter(slug=SLUG).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0019_post_body_help_text"),
    ]

    operations = [
        migrations.RunPython(add_post, remove_post),
    ]
