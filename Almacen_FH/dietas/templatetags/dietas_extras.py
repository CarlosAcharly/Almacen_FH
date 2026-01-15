from django import template

register = template.Library()

@register.filter
def get_item(dic, key):
    """Obtiene un valor de un diccionario por clave, o 0 si no existe"""
    return dic.get(key, 0)  # Devuelve 0 si la clave no existe

@register.filter(name='add_class')
def add_class(field, css):
    """Añade una clase CSS a un campo de formulario"""
    return field.as_widget(attrs={'class': css})