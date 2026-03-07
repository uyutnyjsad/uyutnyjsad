from django import template
from products.models import Category

register = template.Library()

@register.filter
def get_category(categories, slug):
    try:
        return categories.get(slug=slug).name
    except Category.DoesNotExist:
        return ""
