from django.templatetags.static import static

from .models import SiteConfig


def _og_image(request, cfg):
    """URL ABSOLUTA de la miniatura que se ve al compartir el link.

    Tiene que ser absoluta: WhatsApp y Facebook leen la etiqueta desde sus
    propios servidores, una ruta relativa no les sirve.

    Se calcula aca y no en la plantilla porque en produccion las imagenes que
    sube Leonardo viven en Cloudinary y `.url` YA viene absoluta; en local es
    `/media/...` y hay que anteponerle el host. Anteponerlo siempre romperia
    la de Cloudinary, y no anteponerlo nunca romperia la local.
    """
    ruta = ''
    if cfg is not None:
        try:
            if cfg.imagen_compartir:
                ruta = cfg.imagen_compartir.url
        except Exception:
            # Un archivo faltante o un storage caido no puede tumbar TODAS las
            # paginas del sitio por una miniatura.
            ruta = ''
    if not ruta:
        # Este logo si existe en el repo. El og-cover.jpg que estaba escrito a
        # mano antes no existia y devolvia 404 (ver models.SiteConfig).
        ruta = static('img/logo-tagline.png')
    if ruta.startswith(('http://', 'https://', '//')):
        return ruta
    return f'{request.scheme}://{request.get_host()}{ruta}'


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
        'OG_IMAGE': _og_image(request, cfg),
    }
