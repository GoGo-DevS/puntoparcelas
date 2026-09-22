# -*- coding: utf-8 -*-
"""Una region sin parcelas no es una pagina: 404, fuera del sitemap y del menu.

22-09-2026. Al revisar la lista de Jorge en vivo aparecieron 4 regiones
(Araucania, Los Rios, Biobio y Aysen) con su pagina VACIA: estaban en el
sitemap, en los botones del catalogo, y respondian 200 con "0 parcelas".
Google las indexa igual y compiten contra las que si tienen contenido; quien
hace clic ve una pagina sin nada.

Las ciudades ya tenian esta regla desde el 17-09 (ciudad sin parcelas = 404).
Las regiones no, porque su lista es fija (REGIONES_SEO). Ahora la regla sale
de los DATOS: si Leonardo carga una parcela en la Araucania, la region vuelve
sola, sin tocar codigo.
"""
from django.test import TestCase, override_settings

from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


@sin_manifiesto
class RegionesSinParcelas(TestCase):
    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(nombre='Parcela junto al lago', region='los_lagos',
                               ciudad='Frutillar', precio=45000000, moneda='CLP',
                               superficie=5000, estado='disponible')
        # Una region con parcelas SOLO vendidas sigue teniendo contenido: la
        # pagina muestra lo vendido, que tambien es prueba de trayectoria.
        Parcela.objects.create(nombre='Parcela vendida', region='maule',
                               ciudad='Talca', precio=9000000, moneda='CLP',
                               superficie=5000, estado='vendida')

    def test_la_region_vacia_es_404(self):
        self.assertEqual(self.client.get('/catalogo/araucania/').status_code, 404)

    def test_la_region_con_parcelas_sigue_en_200(self):
        self.assertEqual(self.client.get('/catalogo/los-lagos/').status_code, 200)

    def test_la_region_con_solo_vendidas_sigue_en_200(self):
        self.assertEqual(self.client.get('/catalogo/maule/').status_code, 200)

    def test_el_sitemap_no_publica_regiones_vacias(self):
        xml = self.client.get('/sitemap.xml').content.decode('utf8')
        self.assertIn('/catalogo/los-lagos/', xml)
        for vacia in ('araucania', 'los-rios', 'biobio', 'aysen'):
            self.assertNotIn(f'/catalogo/{vacia}/', xml, vacia)

    def test_los_botones_del_catalogo_no_llevan_a_regiones_vacias(self):
        html = self.client.get('/catalogo/').content.decode('utf8')
        self.assertIn('href="/catalogo/los-lagos/"', html)
        self.assertNotIn('href="/catalogo/araucania/"', html)

    def test_si_se_carga_una_parcela_la_region_vuelve_sola(self):
        Parcela.objects.create(nombre='Nueva en Araucania', region='araucania',
                               ciudad='Pucon', precio=30000000, moneda='CLP',
                               superficie=5000, estado='disponible')
        self.assertEqual(self.client.get('/catalogo/araucania/').status_code, 200)
        self.assertIn('/catalogo/araucania/',
                      self.client.get('/sitemap.xml').content.decode('utf8'))

    def test_un_slug_inventado_sigue_siendo_404(self):
        self.assertEqual(self.client.get('/catalogo/region-inventada/').status_code, 404)
