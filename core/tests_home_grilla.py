# -*- coding: utf-8 -*-
"""Grilla "Parcelas en venta" de la home (Jorge Urzua, 23-11-2026).

Todas las parcelas vigentes como tarjetas, en vez del prefooter de textos por
region. Lo que se protege: que esten todas y solo las vigentes, en el orden del
catalogo, y que 64 tarjetas no sean 64 consultas (G-04).
"""
import re

from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from . import views
from .models import FotoParcela, Parcela
from .redirecciones import REDIRECCIONES_301

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


def _p(nombre, foto=True, **extra):
    datos = dict(nombre=nombre, region='valparaiso', ciudad='Santo Domingo', precio=15_000_000,
                 moneda='CLP', superficie=5000, estado='disponible')
    datos.update(extra)
    p = Parcela.objects.create(**datos)
    if foto:
        # Una principal y una que no: la tarjeta tiene que mostrar la principal.
        FotoParcela.objects.create(parcela=p, imagen=f'parcelas/{p.slug}-2.webp', orden=0)
        FotoParcela.objects.create(parcela=p, imagen=f'parcelas/{p.slug}.webp', principal=True, orden=5)
    return p


def _grilla(html):
    return html[html.index('class="venta"'):html.index('<footer')]


def _consultas_home(client):
    # El primer pedido de la vida de la base crea el SiteConfig (get_or_create:
    # 3 consultas que pasan una sola vez). Se calienta antes de medir.
    client.get('/')
    with CaptureQueriesContext(connection) as q:
        r = client.get('/')
    assert r.status_code == 200
    return len(q.captured_queries)


@sin_manifiesto
class Contenido(TestCase):

    def setUp(self):
        self.disp = _p('Vive Santo Domingo', precio=14_990_000)
        self.res = _p('Reservada', estado='reservada', precio=9_000_000)
        self.uf = _p('En UF', moneda='UF', precio=2800, region='los_lagos', ciudad='Frutillar')
        self.vend = _p('Vendida', estado='vendida')
        self.dup = _p('Duplicada', slug=next(iter(REDIRECCIONES_301)))
        self.html = self.client.get('/').content.decode('utf8')

    def test_cada_vigente_tiene_su_tarjeta_enlazada(self):
        g = _grilla(self.html)
        for p in (self.disp, self.res, self.uf):
            self.assertIn(f'<a href="{p.get_absolute_url()}" class="parcela-card venta-card">', g)

    def test_la_vendida_y_la_redirigida_no_aparecen(self):
        self.assertNotIn(self.vend.get_absolute_url(), self.html)
        self.assertNotIn(self.dup.slug, self.html)

    def test_la_tarjeta_trae_rotulo_titulo_precio_superficie_y_foto_principal(self):
        g = _grilla(self.html)
        tarjeta = g[g.index(f'href="{self.disp.get_absolute_url()}"'):]
        tarjeta = tarjeta[:tarjeta.index('</a>')]
        self.assertIn('Venta Parcela Santo Domingo', tarjeta)
        self.assertIn('<h3 class="venta-card__titulo">Vive Santo Domingo</h3>', tarjeta)
        self.assertIn('$14.990.000', tarjeta)
        self.assertIn('5.000 m²', tarjeta)
        self.assertIn(f'parcelas/{self.disp.slug}.webp', tarjeta)          # la principal
        self.assertNotIn(f'parcelas/{self.disp.slug}-2.webp', tarjeta)
        for attr in ('loading="lazy"', 'decoding="async"', 'width="480"', 'height="300"'):
            self.assertIn(attr, tarjeta)

    def test_el_precio_en_uf_sale_en_uf(self):
        self.assertIn('UF 2.800', _grilla(self.html))

    def test_la_reservada_lleva_su_rotulo(self):
        g = _grilla(self.html)
        tarjeta = g[g.index(f'href="{self.res.get_absolute_url()}"'):]
        self.assertIn('Reservada', tarjeta[:tarjeta.index('</a>')])

    def test_h2_sin_emojis(self):
        self.assertIn('<h2 class="venta__h2" id="venta-h2">Parcelas en venta</h2>', self.html)

    def test_parcelas_por_comuna_se_mantiene_antes_de_la_grilla(self):
        _p('Prados', slug='prados-de-frutillar', region='los_lagos', ciudad='Frutillar')
        html = self.client.get('/').content.decode('utf8')
        self.assertLess(html.index('class="home-comunas"'), html.index('class="venta"'))


@sin_manifiesto
class Orden(TestCase):

    def test_mismo_orden_que_el_catalogo(self):
        _p('Cara', precio=50_000_000)
        _p('Barata', precio=5_000_000)
        _p('Destacada cara', precio=90_000_000, destacada=True)
        _p('Reservada barata', precio=1_000_000, estado='reservada')
        html = self.client.get('/').content.decode('utf8')
        en_home = re.findall(r'<h3 class="venta-card__titulo">([^<]+)</h3>', _grilla(html))
        catalogo = [p.nombre for p in self.client.get('/catalogo/').context['page_obj']]
        self.assertEqual(en_home, catalogo)
        self.assertEqual(en_home, ['Destacada cara', 'Barata', 'Cara', 'Reservada barata'])


@sin_manifiesto
class Consultas(TestCase):
    """G-04: el numero de consultas de la home no crece con las tarjetas."""

    def test_la_grilla_es_una_sola_consulta_con_la_foto_incluida(self):
        for i in range(5):
            _p(f'Parcela {i}')
        with self.assertNumQueries(1):
            parcelas = views._parcelas_en_venta()
            self.assertTrue(all(p.foto_url for p in parcelas))

    def test_la_home_no_suma_consultas_por_tarjeta(self):
        # Misma region y comuna en las dos tandas: lo unico que cambia es la
        # cantidad de tarjetas (otra region cambiaria que enlaces se resuelven).
        for i in range(3):
            _p(f'Primera tanda {i}', destacada=(i == 0))
        con_3 = _consultas_home(self.client)
        for i in range(30):
            _p(f'Segunda tanda {i}', destacada=(i < 3))
        con_33 = _consultas_home(self.client)
        self.assertEqual(con_33, con_3, f'3 parcelas: {con_3} consultas; 33 parcelas: {con_33}')

    def test_sin_foto_dibuja_el_marcador_y_no_consulta(self):
        _p('Sin foto', foto=False)
        parcelas = views._parcelas_en_venta()
        self.assertEqual(parcelas[0].foto_url, '')
        self.assertIn('parcela-card-img-placeholder', _grilla(self.client.get('/').content.decode('utf8')))
