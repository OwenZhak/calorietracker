from django import template
from app.models import FoodItem

register = template.Library()

@register.filter(name='get_category_name')
def get_category_name(category_key):
    """Convert category key to display name"""
    CATEGORY_NAMES = {
        'fast_food': 'Фастфуд',
        'fruits': 'Фрукти',
        'vegetables': 'Овочі',
        'meat': "М'ясо",
        'dairy': 'Молочні продукти',
        'grains': 'Крупи',
        'sweets': 'Солодощі',
        'drinks': 'Напої',
        'other': 'Інше',
    }
    return CATEGORY_NAMES.get(category_key, category_key)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get value from dictionary by key"""
    return dictionary.get(key, 0)


@register.filter
def divide_into_weeks(days):
    """Divide days into weeks (lists of 7 days)"""
    weeks = []
    week = []
    for day in days:
        week.append(day)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)
    return weeks