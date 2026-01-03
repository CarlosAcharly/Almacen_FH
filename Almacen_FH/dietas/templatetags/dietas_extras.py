from django import template

register = template.Library()

@register.filter
def get_item(dic, key):
    return dic.get(key)
