"""
Management command: scrape_puntoparcelas
Scrapea todas las parcelas de puntoparcelas.cl, descarga imágenes HD y
puebla la base de datos incluyendo planes de pago.

Uso:
    python manage.py scrape_puntoparcelas
    python manage.py scrape_puntoparcelas --skip-images
    python manage.py scrape_puntoparcelas --force-images   # re-descarga todas
    python manage.py scrape_puntoparcelas --slug vive-ovalle
    python manage.py scrape_puntoparcelas --skip-planes    # no parsea tablas precios
"""
import re
import time
from io import BytesIO

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import FotoParcela, Parcela, PlanPago

BASE_URL = 'https://www.puntoparcelas.cl'

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}

# slug → (region_key, sector, destacada)
PARCELAS_META = {
    'vive-ovalle':                    ('coquimbo',      'Sector Los Baños, Playa Talcaruca',           True),
    'parque-algarrobo':               ('valparaiso',    'Santo Domingo',                               True),
    'proyecto-vive-til-til':          ('metropolitana', 'Til Til, cercanías de Lampa',                 True),
    'hacienda-don-bastian':           ('ohiggins',      'La Estrella, VI Región',                      True),
    'estancia-de-paredones':          ('ohiggins',      'Paredones, VI Región',                        False),
    'olivos-de-trinidad':             ('ohiggins',      'Marchigue, cerca de Peralillo',               False),
    'jardines-de-litueche-vi-region': ('ohiggins',      'Litueche, VI Región',                         False),
    'brisas-de-bucalemu':             ('ohiggins',      'Bucalemu, VI Región',                         False),
    'lomas-de-puertecillo':           ('ohiggins',      'Puertecillo, VI Región',                      False),
    'vive-puertecillo-vi-region':     ('ohiggins',      'Puertecillo, VI Región',                      False),
    'mirador-de-puente-negro-san-fernando': ('ohiggins','San Fernando, VI Región',                     False),
    'punta-pichilemu-vi-region':      ('ohiggins',      'Pichilemu, VI Región',                        False),
    'vive-marchigue':                 ('ohiggins',      'Marchigue, VI Región',                        False),
    'vive-matanzas':                  ('valparaiso',    'Matanzas, V Región',                          False),
    'vive-santo-domingo':             ('valparaiso',    'Santo Domingo, V Región',                     False),
    'fundo-la-quirigua':              ('maule',         'Lago Vichuquén, VII Región',                  True),
    'fundo-la-puntilla':              ('maule',         'VII Región del Maule',                        False),
    'fundo-cauquenes':                ('maule',         'Cauquenes, VII Región',                       False),
    'praderas-de-cauquenes':          ('maule',         'Cauquenes, VII Región',                       False),
    'hacienda-vichuquen-vii-region':  ('maule',         'Vichuquén, VII Región',                       False),
    'lomas-de-constitucion':          ('maule',         'Constitución, VII Región',                    False),
    'robles-de-rio-llico':            ('maule',         'Río Llico, VII Región',                       False),
    'vive-longavi-vii-region':        ('maule',         'Longaví, VII Región',                         False),
    'vive-chillan':                   ('nuble',         'Portezuelo–San Nicolás, XVI Región',          False),
    'parcelas-chillan-sector-portezuelo': ('nuble',     'Portezuelo, XVI Región',                      False),
    'parcelas-precio-oferta-chillan': ('nuble',         'Chillán, XVI Región',                         False),
    'vive-lonquimay':                 ('araucania',     'Lonquimay, IX Región',                        False),
    'bosques-de-frutillar':           ('los_lagos',     'Frutillar, X Región',                         True),
    'vive-osorno-x-region':           ('los_lagos',     'Osorno, X Región',                            True),
    'alta-vista-frutillar':           ('los_lagos',     'Frutillar, X Región',                         False),
    'prados-de-frutillar-x-region':   ('los_lagos',     'Frutillar, X Región',                         False),
    'bahia-chacao-xvii-region':       ('los_lagos',     'Chacao, Chiloé, X Región',                    False),
    'costa-contao-x-region':          ('los_lagos',     'Contao, X Región',                            False),
    'lomas-de-sarao-x-region-fresia-region-de-los-lagos': ('los_lagos', 'Fresia, X Región',           False),
    'vive-puelo-x-region':            ('los_lagos',     'Puelo, X Región',                             False),
    'vive-puerto-varas':              ('los_lagos',     'Puerto Varas, X Región',                      False),
    'vive-rupanco-x-region':          ('los_lagos',     'Lago Rupanco, X Región',                      False),
    'don-guillermo':                  ('maule',         'VII Región del Maule',                        False),
    'hacienda-do-felix':              ('ohiggins',      'VI Región',                                   False),
    'punta-de-toros':                 ('valparaiso',    'V Región',                                    False),
    'cabana-en-pichilemu-frente-a-la-playa': ('ohiggins', 'Pichilemu, VI Región',                     False),
}

# Texto de nav que contamina la descripción en el site de WP
_NAV_SKIP = ['idioma:', 'español (chile)', 'facebook', 'instagram', 'youtube', 'tiktok',
             'región de coquimbo', 'región metropolitana', 'región de valparaíso',
             'hablemos', 'iniciar búsqueda', 'inicio sesión']


def _extract_price(text):
    """Primer precio CLP del texto. Retorna int o 0."""
    match = re.search(r'\$\s*([\d]{1,3}(?:[\.,]\d{3})*)', text)
    if match:
        raw = match.group(1).replace('.', '').replace(',', '')
        try:
            return int(raw)
        except ValueError:
            pass
    return 0


def _extract_superficie(text):
    """Superficie en m². Retorna int o 5000 por defecto."""
    m = re.search(r'(\d{1,3}(?:\.\d{3}){0,3})\s*(?:m²|m2|hectárea|ha)', text, re.IGNORECASE)
    if m:
        raw = m.group(1).replace('.', '')
        try:
            val = float(raw)
            if 'ha' in text[m.start():m.end()+5].lower() or 'hectárea' in text[m.start():m.end()+10].lower():
                result = int(val * 10000)
            else:
                result = int(val)
            if result > 99_999_999:
                return 5000
            return result
        except ValueError:
            pass
    return 5000


def _detect_booleans(text):
    t = text.lower()
    return {
        'tiene_luz':          any(w in t for w in ['luz', 'electricidad', 'eléctrica', 'panel solar']),
        'tiene_agua':         any(w in t for w in ['agua potable', 'red de agua', 'canal de riego', 'aljibe', 'pozo']),
        'tiene_acceso':       any(w in t for w in ['pavimentado', 'asfaltado', 'estabilizado', 'acceso']),
        'vista_privilegiada': any(w in t for w in ['vista', 'panorámica', 'privilegiada', 'volcán', 'lago', 'mar', 'río']),
        'tiene_cercado':      any(w in t for w in ['cercado', 'cierro', 'malla']),
        'tiene_porton':       any(w in t for w in ['portón', 'porton', 'entrada']),
        'es_turistico':       any(w in t for w in ['turístico', 'turistico', 'cabaña', 'cabana', 'arriendo', 'ecoturismo']),
        'bosque_nativo':      any(w in t for w in ['bosque nativo', 'arbolado', 'nativo', 'arrayán', 'tepa']),
        'rol_propio':         any(w in t for w in ['rol propio', 'escriturado', 'rol individual']),
    }


def _upgrade_url(url):
    """Devuelve la URL en mayor resolución posible según CDN."""
    if not url:
        return url
    if 'jumpseller.com' in url:
        # Jumpseller CDN: /thumb/70/92 → /thumb/1200/900
        return re.sub(r'/thumb/\d+/\d+', '/thumb/1200/900', url)
    # WordPress: quitar sufijo -WxH antes de extensión
    return re.sub(r'-\d{2,4}x\d{2,4}(?=\.[a-zA-Z]{2,5}$)', '', url)


def _best_img_url(tag):
    """Extrae la URL de mayor resolución de un tag <img>."""
    # Jumpseller product gallery: imagen principal sin /thumb/
    src = tag.get('src', '')
    if 'jumpseller.com' in src and '/thumb/' not in src and not src.startswith('data:'):
        return src  # ya es el original

    # Prioriza data-large_image (WooCommerce / Jumpseller)
    large = tag.get('data-large_image', '')
    if large:
        return _upgrade_url(large)

    # srcset: elegir mayor ancho
    for srcset_attr in ('data-srcset', 'srcset'):
        srcset = tag.get(srcset_attr, '')
        if not srcset:
            continue
        best_url, best_w = None, 0
        for entry in srcset.split(','):
            parts = entry.strip().split()
            if not parts:
                continue
            url = parts[0]
            w = 0
            if len(parts) >= 2 and parts[1].endswith('w'):
                try:
                    w = int(parts[1][:-1])
                except ValueError:
                    pass
            if w > best_w:
                best_w, best_url = w, url
        if best_url:
            return _upgrade_url(best_url)

    # Fallback: data-src o src
    fallback = tag.get('data-src') or tag.get('src') or ''
    if not fallback or fallback.startswith('data:'):
        return ''
    return _upgrade_url(fallback)


def _extract_images(soup):
    """URLs absolutas de imágenes HD del contenido. Máx 8."""
    imgs = []
    seen = set()

    def _add(url):
        if not url or url in seen:
            return
        if any(s in url.lower() for s in ['logo', 'icon', 'favicon', 'placeholder', '1x1', '.gif', '.svg']):
            return
        if not url.startswith('http'):
            return
        seen.add(url)
        imgs.append(url)

    # ── Jumpseller CDN ────────────────────────────────────────────────────────
    is_jumpseller = bool(soup.find('img', src=re.compile(r'jumpseller\.com')))
    if is_jumpseller:
        # 1) Imagen principal del producto: cdnx.jumpseller.com/.../image/{ID}/{filename} (sin /thumb/)
        for tag in soup.find_all('img'):
            src = tag.get('src', '')
            if 'jumpseller.com' in src and '/thumb/' not in src:
                _add(src)
                break  # solo una principal

        # 2) Galería del producto: img.selected con /thumb/70/92 → /thumb/1200/900
        for tag in soup.select('img.selected'):
            src = tag.get('src', '') or tag.get('data-src', '')
            if 'jumpseller.com' in src:
                _add(_upgrade_url(src))

        return imgs[:8]

    # ── WordPress (fallback) ─────────────────────────────────────────────────
    selectors = [
        'img[data-srcset*="wp-content/uploads"]',
        'img[srcset*="wp-content/uploads"]',
        '.wp-block-gallery img',
        '.gallery img',
        '.entry-content img',
        'figure img',
        'article img',
        '.elementor-image img',
        '.swiper-slide img',
        '.slider img',
        'img[src*="wp-content/uploads"]',
        'img[data-src*="wp-content/uploads"]',
    ]

    for sel in selectors:
        for tag in soup.select(sel):
            url = _best_img_url(tag)
            if not url or url in seen:
                continue
            if any(s in url.lower() for s in ['logo', 'icon', 'favicon', 'placeholder', '1x1', '.gif', '.svg']):
                continue
            if 'wp-content/uploads' not in url and not url.startswith('http'):
                continue
            abs_url = url if url.startswith('http') else f"{BASE_URL}{url}"
            seen.add(url)
            imgs.append(abs_url)
        if len(imgs) >= 8:
            break

    return imgs[:8]


def _extract_planes(soup):
    """Extrae planes de pago de tablas HTML. Retorna lista de dicts."""
    planes = []

    # Busca en toda la página — la tabla puede estar en .summary, .short-desc, etc.
    for table in soup.find_all('table'):
        table_text = table.get_text().lower()
        if not any(k in table_text for k in ['cuota', 'contado', 'crédito', 'credito', 'pie']):
            continue

        rows = table.find_all('tr')
        if len(rows) < 2:
            continue

        # Detectar fila de encabezado
        header_cells = rows[0].find_all(['th', 'td'])
        headers = [c.get_text(strip=True).lower() for c in header_cells]

        col = {}
        for i, h in enumerate(headers):
            if 'contado' in h:
                col['contado'] = i
            elif 'crédito' in h or 'credito' in h or 'valor crédito' in h:
                col['credito'] = i
            elif 'diferencia' in h:
                col['diferencia'] = i
            elif h == 'pie' or 'pie' in h:
                col['pie'] = i
            elif 'cuota' in h:
                col['cuota'] = i

        for idx, row in enumerate(rows[1:], 1):
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            nombre_raw = cells[0].get_text(strip=True) if cells else ''

            # Fila de continuación (rowspan): la primera celda es un precio, no un nombre
            # → los índices de columna se desplazan -1
            is_continuation = bool(re.match(r'^\$[\d.,]+$', nombre_raw))
            shift = -1 if is_continuation else 0

            def price(key):
                i = col.get(key)
                if i is None:
                    return None
                i += shift
                if i < 0 or i >= len(cells):
                    return None
                return _extract_price(cells[i].get_text()) or None

            if is_continuation:
                # Sin nombre propio — saltear (ya capturamos la fila principal arriba)
                continue

            nombre = re.sub(r'([A-ZÁÉÍÓÚÑ])(\d)', r'\1 \2', nombre_raw) if nombre_raw else f'Plan {idx}'
            nombre = nombre.strip()
            m = re.search(r'(\d+)\s*cuotas?', nombre, re.IGNORECASE)
            num_cuotas = int(m.group(1)) if m else None

            plan = {
                'nombre': nombre[:120],
                'precio_contado': price('contado') or 0,
                'precio_credito': price('credito'),
                'diferencia':     price('diferencia'),
                'pie':            price('pie'),
                'cuota':          price('cuota'),
                'num_cuotas':     num_cuotas,
                'orden':          idx,
            }
            if plan['precio_contado'] or plan['precio_credito']:
                planes.append(plan)

    return planes


def _clean_content_div(content_div):
    """Elimina elementos de nav/menú del div de contenido."""
    for bad in content_div.find_all(['nav', 'script', 'style', 'noscript']):
        bad.decompose()
    for bad in content_div.select(
        '[class*="nav"], [class*="menu"], [class*="social"], [class*="share"], '
        '[class*="breadcrumb"], [class*="footer"], [class*="header"]'
    ):
        bad.decompose()


def _extract_description(content_div):
    """Descripción real (filtra basura de nav)."""
    if not content_div:
        return ''
    _clean_content_div(content_div)
    parts = []
    for tag in content_div.find_all(['p']):
        txt = tag.get_text(strip=True)
        if len(txt) < 60:
            continue
        txt_low = txt.lower()
        if any(skip in txt_low for skip in _NAV_SKIP):
            continue
        parts.append(txt)
        if len(parts) >= 4:
            break
    return '\n\n'.join(parts)


def _download_image(url, session):
    """Descarga imagen. Retorna (filename, ContentFile) o None.
    Rechaza imágenes < 400x300 (íconos/thumbnails del tema WP)."""
    try:
        r = session.get(url, timeout=20)
        if r.status_code != 200:
            return None
        ct = r.headers.get('content-type', '')
        if 'image' not in ct:
            return None

        # Validar dimensiones mínimas — evita descargar íconos de 70x92
        from PIL import Image as PILImage
        import io
        try:
            img = PILImage.open(io.BytesIO(r.content))
            w, h = img.size
            if w < 400 or h < 300:
                return None
        except Exception:
            return None

        ext = 'jpg'
        if 'png' in ct:
            ext = 'png'
        elif 'webp' in ct:
            ext = 'webp'
        filename = url.split('/')[-1].split('?')[0] or f'foto.{ext}'
        if '.' not in filename[-6:]:
            filename = f"{filename}.{ext}"
        return filename, ContentFile(r.content)
    except Exception:
        return None


def _scrape_page(slug, session):
    url = f"{BASE_URL}/{slug}"
    try:
        r = session.get(url, timeout=20)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')

        title_tag = (
            soup.find('h1', class_=re.compile(r'entry-title|page-title|titulo', re.I))
            or soup.find('h1')
        )
        nombre = title_tag.get_text(strip=True) if title_tag else slug.replace('-', ' ').title()

        content_div = soup.find(class_=re.compile(r'entry-content|post-content|page-content', re.I))
        full_text = content_div.get_text(' ', strip=True) if content_div else soup.get_text(' ', strip=True)

        precio = _extract_price(full_text)
        superficie = _extract_superficie(full_text)
        bools = _detect_booleans(full_text)
        descripcion = _extract_description(content_div)
        images = _extract_images(soup)
        planes = _extract_planes(soup)

        return {
            'nombre': nombre,
            'precio': precio,
            'superficie': superficie,
            'descripcion': descripcion,
            'images': images,
            'planes': planes,
            **bools,
        }
    except Exception:
        return None


class Command(BaseCommand):
    help = 'Scrapea puntoparcelas.cl y carga parcelas con imágenes HD y planes de pago'

    def add_arguments(self, parser):
        parser.add_argument('--skip-images',  action='store_true', help='No descarga imágenes')
        parser.add_argument('--force-images', action='store_true', help='Re-descarga imágenes aunque ya existan')
        parser.add_argument('--skip-planes',  action='store_true', help='No parsea tablas de precios')
        parser.add_argument('--slug',  type=str, default=None, help='Solo este slug')
        parser.add_argument('--delay', type=float, default=1.5, help='Segundos entre requests (default 1.5)')

    def handle(self, *args, **options):
        skip_images  = options['skip_images']
        force_images = options['force_images']
        skip_planes  = options['skip_planes']
        only_slug    = options['slug']
        delay        = options['delay']

        session = requests.Session()
        session.headers.update(HEADERS)

        slugs = (
            {only_slug: PARCELAS_META.get(only_slug, ('otro', '', False))}
            if only_slug else PARCELAS_META
        )

        ok = err = 0

        for slug, (region, sector, destacada) in slugs.items():
            self.stdout.write(f'  >> {slug}... ', ending='')

            data = _scrape_page(slug, session)
            if not data:
                self.stdout.write(self.style.WARNING('404 / error'))
                err += 1
                time.sleep(delay)
                continue

            images = data.pop('images')
            planes = data.pop('planes')

            bool_fields = [
                'tiene_luz', 'tiene_agua', 'tiene_acceso', 'vista_privilegiada',
                'tiene_cercado', 'tiene_porton', 'es_turistico', 'bosque_nativo', 'rol_propio',
            ]

            parcela, created = Parcela.objects.get_or_create(
                slug=slug,
                defaults={
                    'nombre': data['nombre'], 'region': region, 'sector': sector,
                    'precio': data['precio'], 'superficie': data['superficie'],
                    'descripcion': data['descripcion'], 'destacada': destacada,
                    'estado': 'disponible',
                    **{k: data[k] for k in bool_fields},
                }
            )

            if not created:
                for field, val in {
                    'nombre': data['nombre'], 'region': region, 'sector': sector,
                    'precio': data['precio'], 'superficie': data['superficie'],
                    'descripcion': data['descripcion'], 'destacada': destacada,
                    **{k: data[k] for k in bool_fields},
                }.items():
                    setattr(parcela, field, val)
                parcela.save()

            # Fotos
            fotos_guardadas = 0
            if not skip_images:
                if force_images and parcela.fotos.exists():
                    parcela.fotos.all().delete()

                if images and (force_images or not parcela.fotos.exists()):
                    for i, img_url in enumerate(images):
                        result = _download_image(img_url, session)
                        if result:
                            filename, content = result
                            foto = FotoParcela(parcela=parcela, principal=(i == 0), orden=i)
                            foto.imagen.save(filename, content, save=True)
                            fotos_guardadas += 1
                        time.sleep(0.3)

            # Planes de pago
            planes_guardados = 0
            if not skip_planes and planes:
                parcela.planes.all().delete()
                for plan_data in planes:
                    PlanPago.objects.create(parcela=parcela, **plan_data)
                    planes_guardados += 1

            status = 'creada' if created else 'actualizada'
            extras = []
            if fotos_guardadas:
                extras.append(f'{fotos_guardadas} fotos HD')
            if planes_guardados:
                extras.append(f'{planes_guardados} planes')
            suffix = (' + ' + ', '.join(extras)) if extras else ''
            self.stdout.write(self.style.SUCCESS(f'{status}{suffix}'))

            ok += 1
            time.sleep(delay)

        self.stdout.write(self.style.SUCCESS(f'\nListo: {ok} OK, {err} errores.'))
