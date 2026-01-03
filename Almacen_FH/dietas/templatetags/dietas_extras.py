from django import template

register = template.Library()

@register.filter
def get_item(dic, key):
    return dic.get(key)

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={'class': css})