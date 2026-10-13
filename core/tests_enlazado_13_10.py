# -*- coding: utf-8 -*-
"""Documento de Jorge del 05-10-2026, la parte de enlazado interno: puntos 1, 7 y 9."""
from django.test import TestCase, override_settings

from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


def _p(nombre, region='valparaiso', ciudad='Santo Domingo', precio=30_000_000, **extra):
    datos = dict(nombre=nombre, region=region, ciudad=ciudad, precio=precio,
                 moneda='CLP', superficie=5000, estado='disponible')
    datos.update(extra)
    return Parcela.objects.create(**datos)


@sin_manifiesto
class HomeEnlazaCaracteristicas(TestCase):
    """Punto 1: la portada enlaza a cada pagina por caracteristica que tenga parcelas."""

    def setUp(self):
        _p('Con credito', credito_directo=True)
        _p('Sin nada')

    def test_la_caracteristica_con_parcelas_esta_enlazada(self):
        html = self.client.get('/').content.decode('utf8')
        self.assertIn('href="/catalogo/parcela-con-credito-directo/"', html)

    def test_la_vacia_no_se_enlaza(self):
        html = self.client.get('/').content.decode('utf8')
        self.assertNotIn('href="/catalogo/parcela-vista-al-lago/"', html)


@sin_manifiesto
class Prefooter(TestCase):
    """Punto 7: todo el catalogo vigente en la home, agrupado por region."""

    def setUp(self):
        self.a = _p('Fundo Santa Rosa')
        self.b = _p('Vive Puerto Varas', region='los_lagos', ciudad='Puerto Varas')
        self.v = _p('Ya vendida', estado='vendida')
        self.r = _p('Reservada', estado='reservada')

    def _prefooter(self):
        html = self.client.get('/').content.decode('utf8')
        return html[html.index('class="prefooter"'):html.index('<footer')]

    def test_estan_todas_las_vigentes(self):
        pf = self._prefooter()
        for p in (self.a, self.b, self.r):
            self.assertIn(f'href="{p.get_absolute_url()}"', pf, p.nombre)

    def test_la_vendida_no_entra(self):
        self.assertNotIn(self.v.get_absolute_url(), self._prefooter())

    def test_cada_grupo_enlaza_a_su_region_con_su_h1(self):
        pf = self._prefooter()
        self.assertIn('<a href="/catalogo/valparaiso/">Parcelas en Valparaíso</a>', pf)
        self.assertIn('<a href="/catalogo/los-lagos/">Parcelas en Los Lagos</a>', pf)

    def test_una_parcela_nueva_aparece_sola(self):
        n = _p('Recien cargada', region='maule', ciudad='Rauco')
        self.assertIn(n.get_absolute_url(), self._prefooter())


@sin_manifiesto
class FichaEnlazaArribaYAlLado(TestCase):
    """Punto 9."""

    def setUp(self):
        self.p = _p('La ficha', precio=30_000_000)
        # misma region, otra comuna, MAS barata: sin priorizar la comuna saldria primero
        self.otra_comuna = _p('Otra comuna', ciudad='Algarrobo', precio=1_000_000)
        self.misma_comuna = _p('Misma comuna', precio=90_000_000)
        # otras regiones: la de precio parecido tiene que ganarle a la lejana
        self.parecida = _p('Precio parecido', region='maule', ciudad='Rauco', precio=29_000_000)
        self.lejana = _p('Precio lejano', region='maule', ciudad='Talca', precio=200_000_000)
        self.en_uf = _p('En UF', region='los_lagos', ciudad='Frutillar', precio=29_500_000, moneda='UF')
        self.vendida = _p('Vendida', ciudad='Santo Domingo', estado='vendida')

    def _html(self):
        return self.client.get(self.p.get_absolute_url()).content.decode('utf8')

    def test_la_misma_comuna_va_primero(self):
        zona = self.client.get(self.p.get_absolute_url()).context['relacionadas']
        self.assertEqual(zona[0], self.misma_comuna)

    def test_similares_son_de_otra_region_y_precio_cercano(self):
        similares = self.client.get(self.p.get_absolute_url()).context['similares']
        self.assertEqual(similares[0], self.parecida)
        self.assertTrue(all(s.region != self.p.region for s in similares))

    def test_similares_no_mezcla_monedas(self):
        similares = self.client.get(self.p.get_absolute_url()).context['similares']
        self.assertNotIn(self.en_uf, similares)

    def test_no_recomienda_vendidas_ni_a_si_misma(self):
        ctx = self.client.get(self.p.get_absolute_url()).context
        todas = list(ctx['relacionadas']) + list(ctx['similares'])
        self.assertNotIn(self.vendida, todas)
        self.assertNotIn(self.p, todas)

    def test_enlaza_hacia_su_comuna_y_su_region(self):
        html = self._html()
        self.assertIn('href="/catalogo/valparaiso/santo-domingo/"', html)
        self.assertIn('Parcelas en Santo Domingo', html)
        self.assertIn('href="/catalogo/valparaiso/"', html)

    def test_los_enlaces_hacia_arriba_no_dan_404(self):
        for _texto, ruta in self.client.get(self.p.get_absolute_url()).context['enlaces_arriba']:
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)
