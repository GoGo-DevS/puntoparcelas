from .models import SiteConfig


def site_globals(request):
    # La config se lee una vez por request. Si la tabla todavia no existe
    # (primer deploy, antes de migrar) se devuelve None y las plantillas
    # simplemente no dibujan las etiquetas: nunca revienta el sitio.
    try:
        cfg = SiteConfig.get()
    except Exception:
        cfg = None
    return {
        'WA_NUMERO': '56964090173',
        'WA_LINK': 'https://wa.me/56964090173?text=Hola%20Leonardo%2C%20quiero%20consultar%20por%20una%20parcela.',
        'EMAIL_CONTACTO': 'Contacto@puntoparcelas.cl',
        'SLOGAN': 'Tu inversión hoy, tu patrimonio mañana.',
        'SITE_CONFIG': cfg,
    }
