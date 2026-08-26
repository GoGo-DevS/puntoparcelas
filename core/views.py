import requests as http_requests

from django.conf import settings
from django.contrib import messages
from django.contrib.sitemaps import Sitemap
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static as static_url

from .forms import ConsultaForm
from .models import REGIONES, Consulta, Parcela, SiteConfig, Testimonio


def home(request):
    destacadas = Parcela.objects.filter(destacada=True, estado='disponible')[:6]
    testimonios = Testimonio.objects.filter(activo=True)[:3]
    return render(request, 'core/home.html', {
        'destacadas': destacadas,
        'testimonios': testimonios,
    })


def catalogo(request):
    from django.db.models import Case, IntegerField, Q, Value, When
    region = request.GET.get('region', '').strip()
    q = request.GET.get('q', '').strip()
    estado_order = Case(
        When(estado='disponible', then=Value(0)),
        When(estado='reservada',  then=Value(1)),
        When(estado='vendida',    then=Value(2)),
        default=Value(3), output_field=IntegerField(),
    )
    qs = Parcela.objects.annotate(estado_order=estado_order).order_by('-destacada', 'estado_order', 'precio')
    if region:
        qs = qs.filter(region=region)
    if q:
        qs = qs.filter(Q(nombre__icontains=q) | Q(sector__icontains=q) | Q(descripcion__icontains=q))

    paginator = Paginator(qs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'core/catalogo.html', {
        'page_obj': page_obj,
        'region_activa': region,
        'q': q,
        'regiones': REGIONES,
        'total': qs.count(),
    })


def parcela_detail(request, slug):
    parcela = get_object_or_404(Parcela, slug=slug)
    form = ConsultaForm(initial={'parcela': parcela.pk})
    relacionadas = (
        Parcela.objects
        .filter(region=parcela.region, estado='disponible')
        .exclude(pk=parcela.pk)[:3]
    )
    return render(request, 'core/parcela_detail.html', {
        'parcela': parcela,
        'form': form,
        'relacionadas': relacionadas,
        'schema_json': _parcela_schema(request, parcela),
    })


def _parcela_schema(request, parcela):
    """JSON-LD Product+Offer + BreadcrumbList para rich results en Google.
    Se arma con json.dumps (no en el template) para no romper el JSON con
    comillas o saltos de línea de la descripción."""
    import json as _json

    url = request.build_absolute_uri(parcela.get_absolute_url()) \
        if hasattr(parcela, 'get_absolute_url') \
        else request.build_absolute_uri(f'/catalogo/{parcela.slug}/')
    home = request.build_absolute_uri('/')
    catalogo = request.build_absolute_uri('/catalogo/')

    imagenes = []
    for foto in parcela.fotos.all()[:5]:
        try:
            imagenes.append(request.build_absolute_uri(foto.imagen.url))
        except ValueError:
            pass

    disponibilidad = {
        'disponible': 'https://schema.org/InStock',
        'reservada':  'https://schema.org/LimitedAvailability',
        'vendida':    'https://schema.org/SoldOut',
    }.get(parcela.estado, 'https://schema.org/InStock')

    descripcion = (parcela.descripcion or
                   f'Parcela de {parcela.superficie_display} en '
                   f'{parcela.get_region_display()}.').strip()

    breadcrumb = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': home},
            {'@type': 'ListItem', 'position': 2, 'name': 'Catálogo', 'item': catalogo},
            {'@type': 'ListItem', 'position': 3, 'name': parcela.nombre, 'item': url},
        ],
    }
    schemas = [breadcrumb]

    # Product SOLO para parcelas en CLP con precio: Google exige que un Product
    # tenga offers/review/aggregateRating, y el Offer requiere moneda ISO (CLP,
    # no UF). Para parcelas en UF se omite el Product (no puede mostrar precio
    # en Google igual); igual quedan el breadcrumb y el negocio (RealEstateAgent).
    if parcela.precio and parcela.moneda == 'CLP':
        product = {
            '@context': 'https://schema.org',
            '@type': 'Product',
            'name': parcela.nombre,
            'description': descripcion[:300],
            'category': 'Parcela / Terreno de inversión',
            'url': url,
            'brand': {'@type': 'Brand', 'name': 'Punto Parcelas'},
            'offers': {
                '@type': 'Offer',
                'price': str(parcela.precio),
                'priceCurrency': 'CLP',
                'availability': disponibilidad,
                'url': url,
                'seller': {'@type': 'RealEstateAgent', 'name': 'Punto Parcelas'},
            },
        }
        if imagenes:
            product['image'] = imagenes
        schemas.insert(0, product)

    return _json.dumps(schemas, ensure_ascii=False)


def reserva(request):
    config = SiteConfig.get()
    if request.method == 'POST':
        if request.user.is_authenticated and 'foto_contacto' in request.FILES:
            config.foto_contacto = request.FILES['foto_contacto']
            config.save()
            messages.success(request, 'Foto actualizada.')
            return redirect('core:reserva')
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save()
            _enviar_notificacion(consulta)
            messages.success(request, '¡Mensaje enviado! Leonardo te contactará pronto.')
            return redirect('core:reserva')
    else:
        form = ConsultaForm()
    return render(request, 'core/reserva.html', {'form': form, 'config': config})


def _enviar_notificacion(consulta):
    try:
        asunto = f"Nueva consulta — {consulta.nombre}"
        cuerpo = (
            f"Nombre: {consulta.nombre}\n"
            f"Teléfono: {consulta.telefono}\n"
            f"Email: {consulta.email}\n"
            f"Región de interés: {consulta.get_region_interes_display() if consulta.region_interes else '—'}\n"
            f"Monto a invertir: {consulta.monto_display}\n"
            f"¿Cómo nos conoció?: {consulta.get_como_nos_conociste_display() if consulta.como_nos_conociste else '—'}\n"
            f"Parcela consultada: {consulta.parcela or '—'}\n\n"
            f"Mensaje:\n{consulta.mensaje}"
        )
        send_mail(
            asunto, cuerpo,
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_DESTINO],
            fail_silently=True,
        )
    except Exception:
        pass


def links(request):
    return render(request, 'core/links.html')


def robots_txt(request):
    content = "User-agent: *\nAllow: /\nDisallow: /admin-panel/\nDisallow: /django-admin/\n\nSitemap: https://puntoparcelas.cl/sitemap.xml\n"
    return HttpResponse(content, content_type='text/plain')


def google_verify(request):
    """Verificación de Google Search Console (archivo HTML)."""
    return HttpResponse('google-site-verification: google7385daff3a5a9bec.html',
                        content_type='text/html')


def manifest_webmanifest(request):
    """Web App Manifest para instalar la web como app con el logo.
    Se sirve por vista (no archivo estático) para resolver el hash de {% static %}.

    ?app=panel → la app de Leonardo: abre directo /admin-panel/ (gestión), no el
    sitio público. El manifest solo se enlaza desde el panel, así el "Instalar"
    no le aparece a los visitantes del sitio."""
    es_panel = request.GET.get('app') == 'panel'
    icon = request.build_absolute_uri(static_url('img/logo-isotipo.png'))
    return JsonResponse({
        'name': 'Punto Parcelas — Panel' if es_panel else 'Punto Parcelas',
        'short_name': 'PP Panel' if es_panel else 'Punto Parcelas',
        'description': ('Panel de gestión de Punto Parcelas.' if es_panel
                        else 'Parcelas de inversión en Chile. Tu parcela, tu futuro.'),
        'start_url': '/admin-panel/' if es_panel else '/',
        'scope': '/admin-panel/' if es_panel else '/',
        'display': 'standalone',
        'background_color': '#0D0D0D',
        'theme_color': '#0D0D0D',
        'icons': [
            {'src': icon, 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
            {'src': icon, 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
        ],
    }, content_type='application/manifest+json')


def sitemap_xml(request):
    parcelas = Parcela.objects.filter(estado='disponible').values_list('slug', flat=True)
    base = "https://puntoparcelas.cl"
    urls = [
        f"  <url><loc>{base}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{base}/catalogo/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{base}/reserva/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
    ]
    for slug in parcelas:
        urls.append(f"  <url><loc>{base}/catalogo/{slug}/</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += '\n'.join(urls)
    xml += '\n</urlset>'
    return HttpResponse(xml, content_type='application/xml')


def parcela_geo_pdf(request, slug):
    """Sirve el plano GEO desde nuestro dominio, venga de donde venga.

    POR QUE EXISTE ESTA VISTA
    Nacio para saltarse las restricciones de entrega de PDF de Cloudinary
    firmando la URL. Cuando las fotos se migraron a R2 (20-08) esta vista quedo
    atras: buscaba `/raw/upload/` con una expresion regular y una URL de R2 no
    lo trae nunca, asi que TODO plano moria con "No public_id en URL".

    Se sigue sirviendo por aca en vez de enlazar el archivo directo por dos
    motivos concretos:
      · R2 devuelve estos PDF con Content-Type `image/jpeg` (asi quedaron al
        subirlos). El navegador intenta dibujar un PDF como imagen y no muestra
        nada. Aca se manda `application/pdf` y se ve.
      · El enlace queda en puntoparcelas.cl y no expone el bucket.
    """
    parcela = get_object_or_404(Parcela, slug=slug)
    if not parcela.geo_pdf:
        raise Http404

    raw_url = parcela.geo_pdf.url
    url = raw_url

    # Camino viejo: los planos que todavia apunten a Cloudinary necesitan la
    # URL firmada. Si la URL no es de Cloudinary este bloque no corre.
    if '/raw/upload/' in raw_url:
        try:
            import re
            from urllib.parse import unquote

            import cloudinary.utils
            m = re.search(r'/raw/upload/(?:s--[^/]+--/)?(?:v\d+/)?(.+)', raw_url)
            # `.url` viene URL-encodeada (ñ -> %C3%B1) y el public_id real no,
            # asi que sin decodificar no calza ("Viñas de Cauquenes").
            public_id = unquote(m.group(1))
            url = cloudinary.utils.private_download_url(
                public_id, '', resource_type='raw', type='upload', attachment=False)
        except Exception as e:
            return HttpResponse(f'Sign error: {e}', status=500,
                                content_type='text/plain')

    try:
        r = http_requests.get(url, timeout=30)
        r.raise_for_status()
        contenido = r.content
    except Exception as e:
        # Ultimo recurso: leerlo por el propio storage. Sirve si el bucket
        # dejara de ser publico o si la URL quedara mal guardada.
        try:
            parcela.geo_pdf.open('rb')
            contenido = parcela.geo_pdf.read()
            parcela.geo_pdf.close()
        except Exception:
            return HttpResponse(f'No se pudo leer el plano: {e}', status=502,
                                content_type='text/plain')

    if not contenido[:5].startswith(b'%PDF'):
        # Se avisa en vez de entregar bytes que el visor va a mostrar en blanco.
        return HttpResponse('El archivo guardado como plano no es un PDF.',
                            status=500, content_type='text/plain')

    response = HttpResponse(contenido, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="plano-geo.pdf"'
    response['Cache-Control'] = 'public, max-age=3600'
    return response
