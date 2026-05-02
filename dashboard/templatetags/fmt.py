from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()


@register.filter
def tzs(value, decimals=0):
    """
    Format a number as TZS with thousand separators.
    {{ 1234567.5|tzs }}      → TZS 1,234,568
    {{ 1234567.5|tzs:2 }}    → TZS 1,234,567.50
    """
    try:
        v = Decimal(str(value))
    except (InvalidOperation, TypeError):
        return '—'
    decimals = int(decimals)
    formatted = f'{v:,.{decimals}f}'
    return f'TZS {formatted}'


@register.filter
def intcomma(value):
    """Plain integer with thousand separators, no currency prefix."""
    try:
        v = int(value)
        return f'{v:,}'
    except (TypeError, ValueError):
        return str(value)
