from django import template
import os

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key)
    except Exception:
        return None

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    try:
        return dictionary.get(key)
    except Exception:
        return None

@register.filter(name='dict_lookup')
def dict_lookup(dictionary, key):
    """Get value from dictionary by key"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None

@register.filter
def is_video(url):
    if not url:
        return False
    _, ext = os.path.splitext(str(url).lower())
    return ext in {'.mp4', '.webm', '.mov', '.mkv'}

@register.filter
def is_image(url):
    if not url:
        return False
    _, ext = os.path.splitext(str(url).lower())
    return ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
