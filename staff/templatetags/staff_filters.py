from django import template
import os

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='dict_get')
def dict_get(dictionary, key):
    return dictionary.get(key)

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
