# -*- coding: utf-8 -*-
"""Planilla de enlazado interno de Jorge Urzua (Indexo), 23-11-2026.

Lo que vive en codigo: las 14 guias (filas 1-36), el hub del sur (49), el
bloque "Parcelas por comuna" de la home (58), la plantilla de ficha (59-60) y
la 301 de la ficha duplicada de Don Bastian (41). Lo que vive en la base
(descripciones de fichas, nombre de Bosques de Frutillar) se hace por el panel.
"""
import re
from html import unescape

from django.test import TestCase, override_settings

from . import guias as _guias
from .models import Parcela
from .redirecciones import REDIRECCIONES_301

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

# Las fichas destino de la planilla, con slug fijo (el real del sitio).
FICHAS = [
    ('parque-algarrobo',                'valparaiso', 'Algarrobo'),
    ('vive-santo-domingo',              'valparaiso', 'Santo Domingo'),
    ('fundo-la-turquesa-macrolotes-desde-11-hectareas-en-leyda-desde-95000000', 'valparaiso', 'San Antonio'),
    ('praderas-de-cauquenes',           'maule', 'Cauquenes'),
    ('lomas-de-constitucion',           'maule', 'Constitución'),
    ('hacienda-vichuquen-3',            'maule', 'Vichuquén'),
    ('valles-del-maule',                'maule', 'Hualañé'),
    ('vive-chillan',                    'nuble', 'Chillán'),
    ('prados-de-frutillar',             'los_lagos', 'Frutillar'),
    ('vive-osorno',                     'los_lagos', 'Osorno'),
    ('parcelas-cerca-del-mar-matanzas-3', 'ohiggins', 'Matanzas'),
    ('lomas-de-puertecillo',            'ohiggins', 'Puertecillo'),
    ('fundo-la-puntilla',               'ohiggins', 'La Estrella'),
    ('estancia-paredones',              'ohiggins', 'Paredones'),
    ('alto-pichilemu-ii',               'ohiggins', 'Pichilemu'),
    ('mirador-de-puente-negro-parcelas-desde-16990000-a-25-min-de-san-fernando', 'ohiggins', 'San Fernando'),
    ('vive-ovalle',                     'coquimbo', 'Ovalle'),
]

# (guia, anchor exacto, href exacto) por fila de la planilla.
ESPERADOS = [
    ('que-es-una-parcela-de-agrado', 'parcelas en venta', '/'),                                     # 1
    ('que-es-una-parcela-de-agrado', 'parcelas con rol propio', '/catalogo/parcela-con-rol-propio/'),  # 2
    ('que-es-una-parcela-de-agrado', 'parcelas en cuotas', '/catalogo/parcela-con-credito-directo/'),  # 3
    ('que-hacer-en-algarrobo', 'terrenos en Algarrobo', '/catalogo/parque-algarrobo/'),             # 4
    ('que-hacer-en-algarrobo', 'parcelas en la Región de Valparaíso', '/catalogo/valparaiso/'),     # 5
    ('que-hacer-en-algarrobo', 'parcelas en Santo Domingo', '/catalogo/vive-santo-domingo/'),       # 6
    ('que-hacer-en-cauquenes', 'parcelas en Cauquenes', '/catalogo/praderas-de-cauquenes/'),        # 7
    ('que-hacer-en-chillan', 'parcelas en Chillán', '/catalogo/vive-chillan/'),                     # 8
    ('que-hacer-en-chillan', 'parcelas en Ñuble', '/catalogo/nuble/'),                              # 9
    ('que-hacer-en-constitucion', 'parcelas en Constitución', '/catalogo/lomas-de-constitucion/'),  # 10
    ('que-hacer-en-constitucion', 'parcelas en Cauquenes', '/catalogo/praderas-de-cauquenes/'),     # 11
    ('que-hacer-en-frutillar', 'parcelas en Frutillar', '/catalogo/prados-de-frutillar/'),          # 12
    ('que-hacer-en-litueche', 'parcelas en Matanzas', '/catalogo/parcelas-cerca-del-mar-matanzas-3/'),  # 13
    ('que-hacer-en-litueche', 'terreno en Puertecillo', '/catalogo/lomas-de-puertecillo/'),         # 14
    ('que-hacer-en-litueche', 'parcelas en La Estrella', '/catalogo/fundo-la-puntilla/'),           # 15
    ('que-hacer-en-osorno', 'parcelas en Osorno', '/catalogo/vive-osorno/'),                        # 16
    ('que-hacer-en-osorno', 'parcela en Frutillar', '/catalogo/prados-de-frutillar/'),              # 17
    ('que-hacer-en-osorno', 'terrenos en el sur de Chile', '/catalogo/parcelas-sur-de-chile/'),     # 18
    ('que-hacer-en-pichilemu', 'parcela en Pichilemu', '/catalogo/alto-pichilemu-ii/'),             # 19
    ('que-hacer-en-pichilemu', 'terrenos en Matanzas', '/catalogo/parcelas-cerca-del-mar-matanzas-3/'),  # 20
    ('que-hacer-en-pichilemu', 'terrenos en Puertecillo', '/catalogo/lomas-de-puertecillo/'),       # 21
    ('que-hacer-en-pichilemu', 'parcelas en Paredones', '/catalogo/estancia-paredones/'),           # 22
    ('que-hacer-en-pichilemu', 'parcelas en San Fernando',
     '/catalogo/mirador-de-puente-negro-parcelas-desde-16990000-a-25-min-de-san-fernando/'),       # 23
    ('que-hacer-en-puerto-varas', 'parcelas en Frutillar', '/catalogo/prados-de-frutillar/'),       # 24
    ('que-hacer-en-puerto-varas', 'parcelas en el sur de Chile', '/catalogo/parcelas-sur-de-chile/'),  # 25
    ('que-hacer-en-santo-domingo', 'parcelas en Santo Domingo', '/catalogo/vive-santo-domingo/'),   # 26
    ('que-hacer-en-santo-domingo', 'parcelas en la Región de Valparaíso', '/catalogo/valparaiso/'), # 27
    ('que-hacer-en-santo-domingo', 'terrenos en Algarrobo', '/catalogo/parque-algarrobo/'),         # 28
    ('que-hacer-en-santo-domingo', 'macrolotes en la Región de Valparaíso',
     '/catalogo/fundo-la-turquesa-macrolotes-desde-11-hectareas-en-leyda-desde-95000000/'),       # 29
    ('que-hacer-en-vichuquen', 'parcelas en Vichuquén', '/catalogo/hacienda-vichuquen-3/'),         # 30
    ('que-hacer-en-vichuquen', 'parcelas en Hualañé y Lolol', '/catalogo/valles-del-maule/'),       # 31
    ('que-hacer-en-vichuquen', 'parcelas en Paredones', '/catalogo/estancia-paredones/'),           # 32
    ('que-hacer-en-villarrica', 'parcelas en el sur de Chile', '/catalogo/parcelas-sur-de-chile/'), # 33
    ('que-revisar-antes-de-comprar-una-parcela', 'parcelas sin pie en cuotas',
     '/catalogo/parcela-con-credito-directo/'),                                                    # 34
    ('que-revisar-antes-de-comprar-una-parcela', 'parcelas con crédito directo',
     '/catalogo/parcela-con-credito-directo/'),                                                    # 34
    ('que-revisar-antes-de-comprar-una-parcela', 'terrenos con rol propio',
     '/catalogo/parcela-con-rol-propio/'),                                                         # 35
    ('que-revisar-antes-de-comprar-una-parcela', 'parcelas en Ovalle', '/catalogo/vive-ovalle/'),  # 36
]

_A = re.compile(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S)


def _enlaces(html):
    """[(texto, href)] de un trozo de HTML, con el texto plano y sin espacios de mas."""
    return [(' '.join(unescape(re.sub(r'<[^>]+>', '', t)).split()), unescape(h))
            for h, t in _A.findall(html)]


def _sin_migas(html):
    """La pagina sin la miga de pan: Jorge la deja fuera de la regla."""
    return re.sub(r'<nav class="guia__migas".*?</nav>', '', html, flags=re.S)


def _crear_fichas(estado='disponible'):
    for slug, region, ciudad in FICHAS:
        Parcela.objects.create(nombre=slug.replace('-', ' ').title(), slug=slug, region=region,
                               ciudad=ciudad, precio=15_000_000, moneda='CLP',
                               superficie=5000, estado=estado)
    # Las tres paginas por caracteristica que se enlazan existen solo si
    # alguna parcela calza (si no, 404 a proposito).
    Parcela.objects.filter(slug='praderas-de-cauquenes').update(rol_propio=True, credito_directo=True)


@sin_manifiesto
class GuiasEnlazanALaFichaQuePosiciona(TestCase):
    """Filas 1-36: cada anchor de la planilla, con su URL exacta, en su guia."""

    @classmethod
    def setUpTestData(cls):
        _crear_fichas()

    def test_cada_fila_publica_su_anchor_con_la_url_exacta(self):
        faltan = []
        cache = {}
        for guia, anchor, href in ESPERADOS:
            if guia not in cache:
                cache[guia] = _enlaces(self.client.get(f'/guias/{guia}/').content.decode('utf8'))
            if (anchor, href) not in cache[guia]:
                faltan.append(f'{guia}: "{anchor}" -> {href}')
        self.assertEqual(faltan, [], 'faltan: %s' % faltan)

    def test_un_anchor_una_sola_url_en_cada_guia(self):
        """La regla de "enlaces que chocan": sin contar la miga de pan."""
        choques = []
        for slug in _guias.SLUGS:
            html = _sin_migas(self.client.get(f'/guias/{slug}/').content.decode('utf8'))
            destinos = {}
            for texto, href in _enlaces(html):
                if texto:                 # los iconos de redes no tienen anchor
                    destinos.setdefault(texto.lower(), set()).add(href)
            choques += [f'{slug}: "{t}" -> {sorted(h)}' for t, h in destinos.items() if len(h) > 1]
        self.assertEqual(choques, [], 'anchors con dos destinos: %s' % choques)

    def test_maximo_dos_enlaces_por_parrafo(self):
        for slug in _guias.SLUGS:
            for _tipo, texto in _guias.GUIAS[slug]['cuerpo']:
                self.assertLessEqual(len(_guias._ENLACE.findall(texto)), 2, (slug, texto[:60]))

    def test_las_categorias_quedan_con_el_anchor_ver_todas(self):
        html = self.client.get('/guias/que-hacer-en-frutillar/').content.decode('utf8')
        self.assertIn(('ver todas las parcelas disponibles en Frutillar', '/catalogo/los-lagos/frutillar/'),
                      _enlaces(html))

    def test_ya_no_quedan_los_anchors_sin_relacion(self):
        for slug in ('que-hacer-en-algarrobo', 'que-hacer-en-santo-domingo', 'que-hacer-en-chillan'):
            texto = ' '.join(t for _x, t in _guias.GUIAS[slug]['cuerpo']).lower()
            self.assertNotIn('terrenos en viña del mar', texto)
            self.assertNotIn('parcelas chillan|', texto)


@sin_manifiesto
class UnaFichaQueYaNoExisteNoDejaUnEnlaceRoto(TestCase):
    """Sin las fichas en la base, los enlaces bajan al catalogo (nunca un 404)."""

    def test_sin_fichas_todo_destino_responde_200(self):
        rotos = []
        for slug in _guias.SLUGS:
            for texto, href in _enlaces(self.client.get(f'/guias/{slug}/').content.decode('utf8')):
                if href.startswith('/catalogo/') and self.client.get(href).status_code != 200:
                    rotos.append(f'{slug}: {texto} -> {href}')
        self.assertEqual(rotos, [], rotos)

    def test_la_ficha_ausente_baja_al_catalogo(self):
        self.assertEqual(_guias._ruta_viva('/catalogo/vive-chillan/'), '/catalogo/')

    def test_la_caracteristica_vacia_baja_al_catalogo(self):
        self.assertEqual(_guias._ruta_viva('/catalogo/parcela-con-rol-propio/'), '/catalogo/')

    def test_las_fichas_se_buscan_en_una_sola_consulta_por_pagina(self):
        # Pichilemu cita 5 fichas: UNA consulta para todas, no una por enlace (G-04).
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        _crear_fichas()
        with CaptureQueriesContext(connection) as q:
            _guias.cuerpo_renderizado('que-hacer-en-pichilemu')
        # Las que traen slugs de fichas (todas las de `publicas` FILTRAN por slug
        # para excluir las redirigidas; esas no cuentan).
        por_slug = [x['sql'] for x in q.captured_queries
                    if x['sql'].startswith('SELECT "core_parcela"."slug"')]
        self.assertEqual(len(por_slug), 1, por_slug)


@sin_manifiesto
class FichaDuplicadaResponde301(TestCase):
    """Fila 41. Las filas 37 y 42 NO son duplicadas (ver core/redirecciones.py)."""

    VIEJA = 'hacienda-don-bastian-5000-m2-con-rol-propio-por-16990000-2'

    @classmethod
    def setUpTestData(cls):
        for slug in ('hacienda-don-bastian', cls.VIEJA, 'hacienda-don-bastian-parcela-i381-3'):
            Parcela.objects.create(nombre=slug, slug=slug, region='ohiggins', ciudad='La Estrella',
                                   precio=16_990_000, moneda='CLP', estado='disponible')

    def test_la_duplicada_redirige_301_a_la_canonica(self):
        r = self.client.get(f'/catalogo/{self.VIEJA}/')
        self.assertEqual(r.status_code, 301)
        self.assertEqual(r['Location'], '/catalogo/hacienda-don-bastian/')
        self.assertEqual(self.client.get(r['Location']).status_code, 200)

    def test_sin_cadenas(self):
        for origen, destino in REDIRECCIONES_301.items():
            self.assertNotIn(destino, REDIRECCIONES_301, origen)

    def test_la_parcela_i381_no_se_redirige(self):
        self.assertEqual(self.client.get('/catalogo/hacienda-don-bastian-parcela-i381-3/').status_code, 200)

    def test_el_sitio_no_enlaza_a_la_url_que_redirige(self):
        for ruta in ('/', '/catalogo/', '/catalogo/ohiggins/', '/catalogo/ohiggins/la-estrella/',
                     '/sitemap.xml', '/catalogo/hacienda-don-bastian/'):
            with self.subTest(ruta=ruta):
                self.assertNotIn(self.VIEJA, self.client.get(ruta).content.decode('utf8'))

    def test_el_panel_la_sigue_viendo(self):
        # La fila no se borra: Leonardo decide. Solo deja de ser publica.
        self.assertTrue(Parcela.objects.filter(slug=self.VIEJA).exists())
        self.assertFalse(Parcela.publicas.filter(slug=self.VIEJA).exists())


@sin_manifiesto
class PlantillaDeFicha(TestCase):
    """Filas 59 y 60."""

    def _p(self, nombre, ciudad='Frutillar', region='los_lagos', precio=15_000_000, **extra):
        return Parcela.objects.create(nombre=nombre, region=region, ciudad=ciudad, precio=precio,
                                      moneda='CLP', superficie=5000, estado='disponible', **extra)

    def test_el_enlace_final_dice_ver_todas(self):
        p = self._p('La ficha')
        html = self.client.get(p.get_absolute_url()).content.decode('utf8')
        self.assertIn(('Ver todas las parcelas disponibles en Frutillar', '/catalogo/los-lagos/frutillar/'),
                      _enlaces(html))
        # El boton del final ya no usa el anchor de la keyword...
        botones = html[html.rindex('btn-outline-gold') - 400:]
        self.assertNotIn('>\n        Parcelas en Frutillar', botones)
        # ...pero la miga de arriba se mantiene igual.
        self.assertIn('Parcelas en Frutillar', html[:html.index('btn-outline-gold')])

    def test_relacionadas_son_de_la_misma_zona_y_no_de_otras_regiones(self):
        p = self._p('La ficha')
        for i in range(4):
            self._p(f'Vecina {i}', ciudad='Osorno')
        self._p('De otra region', region='maule', ciudad='Talca')
        ctx = self.client.get(p.get_absolute_url()).context
        self.assertEqual(len(ctx['relacionadas']), 4)
        self.assertTrue(all(r.region == 'los_lagos' for r in ctx['relacionadas']))
        self.assertEqual(list(ctx['similares']), [])

    def test_la_misma_comuna_va_primero(self):
        p = self._p('La ficha')
        self._p('Otra comuna', ciudad='Osorno', precio=1_000_000)
        misma = self._p('Misma comuna', precio=90_000_000)
        self.assertEqual(self.client.get(p.get_absolute_url()).context['relacionadas'][0], misma)

    def test_ficha_sola_en_su_region_igual_tiene_enlaces_laterales(self):
        p = self._p('Sola en Coquimbo', region='coquimbo', ciudad='Ovalle')
        otra = self._p('En otra region', region='maule', ciudad='Talca')
        ctx = self.client.get(p.get_absolute_url()).context
        self.assertEqual(list(ctx['relacionadas']), [])
        self.assertEqual(list(ctx['similares']), [otra])


@sin_manifiesto
class HomeParcelasPorComuna(TestCase):
    """Fila 58."""

    def _bloque(self):
        html = self.client.get('/').content.decode('utf8')
        if 'class="home-comunas"' not in html:
            return ''
        return html[html.index('class="home-comunas"'):html.index('</section>', html.index('class="home-comunas"'))]

    def test_el_bloque_enlaza_cada_comuna_a_su_ficha(self):
        _crear_fichas()
        bloque = self._bloque()
        self.assertIn('<h2 class="home-comunas__h2">Parcelas por comuna</h2>', bloque)
        enlaces = _enlaces(bloque)
        for texto, href in [('Parcelas en Frutillar', '/catalogo/prados-de-frutillar/'),
                            ('Parcelas en Santo Domingo', '/catalogo/vive-santo-domingo/'),
                            ('Parcelas en Cauquenes', '/catalogo/praderas-de-cauquenes/'),
                            ('Parcelas en Matanzas', '/catalogo/parcelas-cerca-del-mar-matanzas-3/'),
                            ('Parcelas en Chillán', '/catalogo/vive-chillan/'),
                            ('Parcelas en Osorno', '/catalogo/vive-osorno/'),
                            ('Parcelas en Ovalle', '/catalogo/vive-ovalle/'),
                            ('Parcelas en Constitución', '/catalogo/lomas-de-constitucion/')]:
            self.assertIn((texto, href), enlaces)
        self.assertEqual(len(enlaces), 8)

    def test_una_ficha_vendida_o_borrada_sale_sola(self):
        _crear_fichas()
        Parcela.objects.filter(slug='vive-ovalle').update(estado='vendida')
        Parcela.objects.filter(slug='vive-chillan').delete()
        hrefs = [h for _t, h in _enlaces(self._bloque())]
        self.assertNotIn('/catalogo/vive-ovalle/', hrefs)
        self.assertNotIn('/catalogo/vive-chillan/', hrefs)
        self.assertEqual(len(hrefs), 6)

    def test_sin_ninguna_no_se_dibuja(self):
        self.assertEqual(self._bloque(), '')


@sin_manifiesto
class HubSurDeChile(TestCase):
    """Fila 49."""

    def setUp(self):
        Parcela.objects.create(nombre='En el sur', region='los_lagos', ciudad='Frutillar',
                               precio=15_000_000, moneda='CLP', estado='disponible')

    def test_enlaza_terrenos_en_ovalle(self):
        Parcela.objects.create(nombre='Vive Ovalle', slug='vive-ovalle', region='coquimbo',
                               ciudad='Ovalle', precio=10_990_000, moneda='CLP', estado='disponible')
        html = self.client.get('/catalogo/parcelas-sur-de-chile/').content.decode('utf8')
        self.assertIn(('terrenos en Ovalle', '/catalogo/vive-ovalle/'), _enlaces(html))

    def test_sin_la_ficha_baja_al_catalogo_y_no_publica_el_marcador(self):
        html = self.client.get('/catalogo/parcelas-sur-de-chile/').content.decode('utf8')
        self.assertIn(('terrenos en Ovalle', '/catalogo/'), _enlaces(html))
        self.assertNotIn('[[', html)
