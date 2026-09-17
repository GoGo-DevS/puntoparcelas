"""SEO: ciudades, migas y los schemas de la lista de Jorge Urzua (17-09-2026).

Por que vive aca y no en views.py: los schemas se arman con json.dumps y NO en
la plantilla. Una comilla o un salto de linea en la descripcion de una parcela
rompe el JSON-LD, Google descarta el bloque entero y no avisa: la pagina se ve
perfecta y el rich result no sale nunca.

La lista que pidio Jorge, y como quedo cada punto:

  1    Enlazado interno hacia ciudades .......... `ciudades_de_region`
  2    BreadcrumbList en region, ciudad y parcela `migas`
  2.2  Organization solo en la home ............. `schema_negocio`
  2.3  RealEstateAgent en las parcelas .......... `schema_parcela`
  2.5  CollectionPage en categorias ............. `schema_coleccion`
"""
import json

from django.utils.text import slugify

from .models import REGIONES, Parcela

REGION_LABEL = dict(REGIONES)


def slug_ciudad(nombre):
    return slugify(nombre or '')


def ciudades_de_region(region, solo_disponibles=False):
    """Las ciudades de una region QUE TIENEN parcelas, con cuantas.

    Sale de los datos, no de una lista fija: `Parcela.ciudad` es texto libre
    que escribe Leonardo en su panel. Una lista escrita a mano quedaria
    desactualizada la primera vez que el cargue una parcela en una ciudad nueva,
    y el sintoma seria una pagina que no existe sin que nadie se entere.

    Devuelve [{nombre, slug, total}], ordenado de mas a menos parcelas.
    """
    qs = Parcela.objects.filter(region=region).exclude(ciudad='')
    if solo_disponibles:
        qs = qs.filter(estado='disponible')

    cuenta = {}
    for nombre in qs.values_list('ciudad', flat=True):
        limpio = (nombre or '').strip()
        if not limpio:
            continue
        # Se agrupa por SLUG y no por el texto: "Puerto Varas" y "puerto varas"
        # son la misma ciudad y tienen que ser una sola pagina.
        clave = slug_ciudad(limpio)
        if clave not in cuenta:
            cuenta[clave] = {'nombre': limpio, 'slug': clave, 'total': 0}
        cuenta[clave]['total'] += 1
    return sorted(cuenta.values(), key=lambda c: (-c['total'], c['nombre']))


def ciudad_por_slug(region, slug):
    """El nombre real de la ciudad a partir del slug de la URL, o None.

    None significa 404: una URL de ciudad sin parcelas no puede devolver un
    catalogo vacio con estado 200, porque Google la indexa igual.
    """
    for ciudad in ciudades_de_region(region):
        if ciudad['slug'] == slug:
            return ciudad['nombre']
    return None


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

def _absoluta(request, ruta):
    return request.build_absolute_uri(ruta)


def migas(request, tramos):
    """BreadcrumbList. `tramos` es [(nombre, ruta)] SIN incluir Inicio.

    La ultima miga tambien lleva `item`: Google lo acepta y asi la pagina
    actual queda identificada con su URL canonica.
    """
    elementos = [{
        '@type': 'ListItem', 'position': 1,
        'name': 'Inicio', 'item': _absoluta(request, '/'),
    }]
    for i, (nombre, ruta) in enumerate(tramos, start=2):
        elementos.append({
            '@type': 'ListItem', 'position': i,
            'name': nombre, 'item': _absoluta(request, ruta),
        })
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': elementos,
    }


def schema_negocio(request):
    """El negocio. VA SOLO EN LA HOME (punto 2.2 de Jorge).

    Hasta el 17-09 estaba en `base.html`, o sea repetido en las 40 y tantas
    paginas del sitio. Declarar la misma entidad una y otra vez no suma: lo que
    Google necesita es UNA pagina que la defina, y esa es la home.

    Se conserva `RealEstateAgent` y no se cambia a `Organization` a secas
    porque RealEstateAgent YA ES un Organization (via LocalBusiness) y ademas
    dice a que se dedica. Bajarlo a Organization seria perder informacion.
    """
    inicio = _absoluta(request, '/')
    logo = _absoluta(request, '/static/img/logo-isotipo.png')
    return {
        '@context': 'https://schema.org',
        '@type': 'RealEstateAgent',
        '@id': inicio + '#negocio',
        'name': 'Punto Parcelas',
        'description': ('Venta de parcelas de inversión en Chile. Rol propio, '
                        'acceso pavimentado y documentación al día.'),
        'url': inicio,
        'logo': logo,
        'image': logo,
        'telephone': '+56964090173',
        'areaServed': {'@type': 'Country', 'name': 'Chile'},
        'sameAs': [
            'https://www.instagram.com/punto_parcelas/',
            'https://www.facebook.com/puntoparcelas1',
            'https://www.youtube.com/@PuntoParcelas',
            'https://www.tiktok.com/@puntoparcelas.cl',
        ],
    }


def schema_coleccion(request, nombre, descripcion, ruta, parcelas):
    """CollectionPage + ItemList (punto 2.5). Region = categoria, ciudad = subcategoria.

    El ItemList lleva solo nombre y URL de cada parcela: el detalle de cada una
    vive en su propia ficha, y repetirlo aca no agrega nada.
    """
    items = [{
        '@type': 'ListItem',
        'position': i,
        'url': _absoluta(request, p.get_absolute_url()),
        'name': p.nombre,
    } for i, p in enumerate(parcelas, start=1)]

    return {
        '@context': 'https://schema.org',
        '@type': 'CollectionPage',
        'name': nombre,
        'description': descripcion,
        'url': _absoluta(request, ruta),
        'isPartOf': {'@type': 'WebSite', 'url': _absoluta(request, '/'),
                     'name': 'Punto Parcelas'},
        'mainEntity': {
            '@type': 'ItemList',
            'numberOfItems': len(items),
            'itemListElement': items,
        },
    }


def ruta_region(slug_region):
    return f'/catalogo/{slug_region}/'


def ruta_ciudad(slug_region, slug_ciudad_):
    return f'/catalogo/{slug_region}/{slug_ciudad_}/'


def a_json(schemas):
    """Una lista de schemas en un solo bloque, listo para el template."""
    return json.dumps(schemas, ensure_ascii=False)
