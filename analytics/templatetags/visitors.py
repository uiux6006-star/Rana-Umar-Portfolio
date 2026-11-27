from django import template

from analytics.stats import visitor_summary

register = template.Library()


@register.simple_tag
def visitor_stats(days=30):
    return visitor_summary(days)
