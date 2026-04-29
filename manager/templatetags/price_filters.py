from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def format_price(value):
    """
    Formate un prix en entier sans décimales
    """
    try:
        # Convertir en entier
        price = int(float(value))
        return f"{price:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value

@register.filter
def format_price_fcfa(value):
    """
    Formate un prix en FCFA sans décimales
    """
    try:
        # Convertir en entier
        price = int(float(value))
        return f"{price:,} FCFA".replace(",", " ")
    except (ValueError, TypeError):
        return f"{value} FCFA" 