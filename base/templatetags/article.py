"""
{{ post.body|article }} — simple, safe formatting for blog posts.

    ## Heading          -> <h2>
    ### Smaller heading -> <h3>
    - item              -> bullet list
    **bold**            -> <strong>
    (empty line)        -> new paragraph

Everything is HTML-escaped first, so a post can never inject HTML or scripts.
Posts written as plain paragraphs look exactly as before.
"""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

BOLD = re.compile(r"\*\*(.+?)\*\*")


def _inline(text):
    return BOLD.sub(r"<strong>\1</strong>", escape(text))


@register.filter
def article(body):
    html = []
    paragraph = []
    items = []

    def flush_paragraph():
        if paragraph:
            html.append("<p>" + "<br>".join(_inline(line) for line in paragraph) + "</p>")
            paragraph.clear()

    def flush_list():
        if items:
            html.append("<ul>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for raw in str(body or "").replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            flush_paragraph()
            flush_list()
        elif line.startswith("### "):
            flush_paragraph(); flush_list()
            html.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_paragraph(); flush_list()
            html.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith(("- ", "• ")):
            flush_paragraph()
            items.append(line[2:])
        else:
            flush_list()
            paragraph.append(line)

    flush_paragraph()
    flush_list()
    return mark_safe("\n".join(html))
