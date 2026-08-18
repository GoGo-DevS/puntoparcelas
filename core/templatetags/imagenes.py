from django import template

from core.models import _cloudinary_achicada

register = template.Library()


@register.filter
def achicar(url, ancho=1200):
    """Inserta f_auto,q_auto,w_<ancho> en una URL de Cloudinary. Ver
    core/models.py:_cloudinary_achicada - misma logica, expuesta al template
    para los casos donde se accede al campo imagen directo (no via property)."""
    if not url:
        return url
    return _cloudinary_achicada(str(url), ancho=ancho)
