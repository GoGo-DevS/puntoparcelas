# -*- coding: utf-8 -*-
"""La descripcion de la ficha admite el marcador de las guias, [[anchor|/ruta/]].

23-11-2026: las filas de la planilla de Jorge que van en fichas se escriben en
el panel. La ficha dibujaba la descripcion con `linebreaks` (escapa todo), asi
que un <a> pegado ahi salia como texto. Ahora el cuerpo dibuja el marcador como
enlace y todo lo demas (meta, JSON-LD, preguntas, busqueda) lo recibe sin
marcadores. Una descripcion sin marcadores sale IGUAL que antes.
"""
import json
import re

from django.db import connection
from django.template.defaultfilters import linebreaks_filter
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from . import guias as _guias
from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

# Una descripcion como las que escribe Leonardo: \r\n del navegador, tres
# saltos seguidos, guiones, emoji, y un "&" y un "<" sueltos que se tienen que
# seguir escapando.
REAL = ('PARCELACIÓN\r\nOlivos de Marchigüe - Sector Marchigüe (cerca de Peralillo), Región '
        "de O'Higgins.\r\n\r\nDETALLE DE PRECIOS\r\n- Parcela de 5.000 m²: desde $14.990.000 "
        '& <b>liquidación</b> si 3 < 5\r\n\r\n\r\n🌿 CERCANÍAS Y REFERENCIAS\r\n'
        '- Peralillo: 15 minutos\r\n- Pichilemu: 1 hora\r\n')


def _p(nombre, descripcion='', slug=None, **extra):
    datos = dict(nombre=nombre, descripcion=descripcion, region='ohiggins', ciudad='Marchigüe',
                 precio=14_990_000, moneda='CLP', superficie=5000, estado='disponible')
    if slug:
        datos['slug'] = slug
    datos.update(extra)
    return Parcela.objects.create(**datos)


def _cuerpo(html):
    """El contenido del primer bloque .pp-descripcion de la ficha."""
    m = re.search(r'<div class="pp-descripcion"[^>]*>(.*?)</div>', html, re.S)
    return m.group(1) if m else None


@sin_manifiesto
class SinMarcadoresSaleIgualQueAntes(TestCase):

    def test_la_funcion_es_linebreaks_byte_por_byte(self):
        self.assertEqual(str(_guias.descripcion_html(REAL)), str(linebreaks_filter(REAL)))

    def test_la_ficha_dibuja_lo_mismo_que_linebreaks(self):
        p = _p('Olivos', REAL)
        html = self.client.get(p.get_absolute_url()).content.decode('utf8')
        self.assertEqual(_cuerpo(html), str(linebreaks_filter(REAL)))
        # el "<" y el "&" sueltos se siguen escapando
        self.assertIn('&amp; &lt;b&gt;liquidación&lt;/b&gt; si 3 &lt; 5', html)

    def test_vacia_y_un_solo_parrafo(self):
        for texto in ('', 'Una sola línea', 'Dos\nlíneas'):
            self.assertEqual(str(_guias.descripcion_html(texto)), str(linebreaks_filter(texto)))


@sin_manifiesto
class ConMarcadores(TestCase):

    DESC = ('DESCRIPCIÓN BREVE DEL PROYECTO\nProyecto en Marchigüe.\n'
            'Si buscas más alternativas de [[parcelas en Cauquenes|/catalogo/praderas-de-cauquenes/]], '
            'revisa también Praderas.\n\nMODALIDAD DE PAGO\n'
            '- Pago al contado o [[crédito directo|/catalogo/parcela-con-credito-directo/]] desde pie $0\n\n'
            'CERCANÍAS\n- Osorno: 45 minutos (ver [[parcelas en Osorno|/catalogo/vive-osorno/]])\n\n'
            '❓ PREGUNTAS FRECUENTES\n¿Hay crédito?\nSí, [[crédito directo|/catalogo/parcela-con-credito-directo/]] '
            'desde pie $0.\n¿Tiene rol propio?\nSí.')

    def setUp(self):
        self.destino = _p('Praderas', slug='praderas-de-cauquenes', region='maule', ciudad='Cauquenes',
                          credito_directo=True)
        self.p = _p('La ficha', self.DESC)

    def _html(self):
        return self.client.get(self.p.get_absolute_url()).content.decode('utf8')

    def test_el_cuerpo_dibuja_los_enlaces_con_la_url_exacta(self):
        cuerpo = _cuerpo(self._html())
        self.assertIn('<a href="/catalogo/praderas-de-cauquenes/">parcelas en Cauquenes</a>', cuerpo)
        self.assertIn('<a href="/catalogo/parcela-con-credito-directo/">crédito directo</a>', self._html())

    def test_la_ficha_que_no_existe_baja_al_catalogo(self):
        self.assertIn('<a href="/catalogo/">parcelas en Osorno</a>', self._html())

    def test_nunca_se_publica_un_marcador(self):
        html = self._html()
        self.assertNotIn('[[', html)
        self.assertNotIn(']]', html)

    def test_meta_description_y_json_ld_llevan_solo_el_anchor(self):
        html = self._html()
        meta = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
        self.assertNotIn('[[', meta)
        # La meta corta en 100 caracteres: llega el anchor, sin el marcador.
        self.assertIn('alternativas de parcelas en Cau', meta)
        bloque = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        datos = json.loads(bloque)
        producto = next(d for d in datos if d.get('@type') == 'Product')
        self.assertNotIn('[[', producto['description'])
        self.assertIn('parcelas en Cauquenes', producto['description'])
        faq = next(d for d in datos if d.get('@type') == 'FAQPage')
        respuesta = faq['mainEntity'][0]['acceptedAnswer']['text']
        self.assertEqual(respuesta, 'Sí, crédito directo desde pie $0.')

    def test_la_respuesta_de_la_faq_se_ve_sin_marcador(self):
        self.assertIn('<p class="pp-faq__r">Sí, crédito directo desde pie $0.</p>', self._html())

    def test_una_ficha_que_redirige_se_enlaza_directo_a_su_destino(self):
        _p('Canonica', slug='hacienda-don-bastian')
        html = _guias.descripcion_html(
            'Ver [[Don Bastián|/catalogo/hacienda-don-bastian-5000-m2-con-rol-propio-por-16990000-2/]]')
        self.assertIn('<a href="/catalogo/hacienda-don-bastian/">Don Bastián</a>', html)

    def test_las_fichas_citadas_se_buscan_en_una_sola_consulta(self):
        with CaptureQueriesContext(connection) as q:
            self.client.get(self.p.get_absolute_url())
        por_slug = [x['sql'] for x in q.captured_queries
                    if x['sql'].startswith('SELECT "core_parcela"."slug"')]
        self.assertEqual(len(por_slug), 1, por_slug)


@sin_manifiesto
class BusquedaIgnoraLasRutas(TestCase):

    def test_la_ruta_de_un_enlace_no_hace_calzar_la_busqueda(self):
        _p('Fundo del sur', 'Parcelas. Ver [[otras|/catalogo/zzzproyectoxyz/]]')
        r = self.client.get('/catalogo/?q=zzzproyectoxyz')
        self.assertEqual(r.context['total'], 0)

    def test_el_anchor_si_cuenta(self):
        _p('Fundo del sur', 'Parcelas. Ver [[vista volcanica|/catalogo/otra/]]')
        r = self.client.get('/catalogo/?q=volcanica')
        self.assertEqual(r.context['total'], 1)
