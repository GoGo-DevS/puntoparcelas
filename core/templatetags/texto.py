from django import template

register = template.Library()


@register.filter(is_safe=True)
def una_linea(valor):
    """Junta todo en una linea: sin saltos ni espacios repetidos.

    13-10-2026: la meta description de cada ficha salia de la descripcion que
    escribe Leonardo, con sus saltos de linea adentro del atributo. Es HTML
    valido, pero WhatsApp armaba la vista previa del link sin titulo ni foto.
    Lo que va dentro de una etiqueta <meta> va siempre en una linea.
    """
    return ' '.join(str(valor or '').split())
