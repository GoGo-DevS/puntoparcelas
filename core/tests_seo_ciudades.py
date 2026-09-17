# -*- coding: utf-8 -*-
"""Lo que pidio Jorge Urzua el 17-09-2026, con una prueba por punto.

Se prueba el HTML y el JSON-LD que de verdad salen, no el codigo que los arma:
un JSON-LD mal formado se ve igual en pantalla y Google descarta el bloque
entero sin avisar.
"""
import json
import re

from django.test import TestCase, override_settings

from .models import Parcela

# El almacen de produccion exige el manifiesto de collectstatic; sin correrlo,
# CUALQUIER pagina revienta en {% static %} y el fallo no dice nada del SEO.
sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


def _schemas(respuesta):
    """Los schemas de la pagina, PARSEADOS. Si el JSON esta roto, falla aca."""
    html = respuesta.content.decode('utf8')
    salida = []
    for bloque in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        dato = json.loads(bloque)          # revienta si el JSON esta mal
        salida += dato if isinstance(dato, list) else [dato]
    return salida


def _tipos(respuesta):
    return {s.get('@type') for s in _schemas(respuesta)}


@sin_manifiesto
class CiudadesYSchemas(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.frutillar = Parcela.objects.create(
            nombre='Parcela junto al lago', region='los_lagos', ciudad='Frutillar',
            precio=45000000, moneda='CLP', superficie=5000, estado='disponible')
        Parcela.objects.create(
            nombre='Parcela con vista', region='los_lagos', ciudad='Puerto Varas',
            precio=60000000, moneda='CLP', superficie=5000, estado='disponible')
        # Sin ciudad: no puede inventar una pagina ni romper el listado.
        Parcela.objects.create(
            nombre='Parcela sin ciudad', region='los_lagos', ciudad='',
            precio=30000000, moneda='CLP', superficie=5000, estado='disponible')

    # --- punto 1: enlazado interno ---------------------------------------
    def test_la_region_enlaza_a_sus_ciudades(self):
        html = self.client.get('/catalogo/los-lagos/').content.decode('utf8')
        self.assertIn('/catalogo/los-lagos/frutillar/', html)
        self.assertIn('/catalogo/los-lagos/puerto-varas/', html)

    def test_la_pagina_de_ciudad_muestra_solo_sus_parcelas(self):
        html = self.client.get('/catalogo/los-lagos/frutillar/').content.decode('utf8')
        self.assertIn('Parcela junto al lago', html)
        self.assertNotIn('Parcela con vista', html)

    def test_una_ciudad_sin_parcelas_es_404_y_no_una_pagina_vacia(self):
        """Un 200 vacío lo indexa Google igual y compite con las que sí tienen.

        Se comprueba contra la ciudad que SÍ existe: sin ella, el 404 de una
        ciudad inventada también ocurre —porque no hay ruta— y el test pasaría
        sin que la funcionalidad exista.
        """
        self.assertEqual(self.client.get('/catalogo/los-lagos/frutillar/').status_code, 200)
        self.assertEqual(self.client.get('/catalogo/los-lagos/pucon/').status_code, 404)

    def test_una_region_sin_ciudades_no_dibuja_el_bloque(self):
        """Un encabezado seguido de nada se lee como que el sitio está roto.

        Se mide contra la región que sí lo dibuja, por lo mismo de arriba.
        """
        con = self.client.get('/catalogo/los-lagos/').content.decode('utf8')
        sin = self.client.get('/catalogo/aysen/').content.decode('utf8')
        self.assertIn('Parcelas por ciudad', con)
        self.assertNotIn('Parcelas por ciudad', sin)

    def test_la_ruta_de_ciudad_no_se_come_el_pdf_del_plano(self):
        """/catalogo/<slug>/geo-pdf/ y /catalogo/<region>/<ciudad>/ compiten.

        Guardia de regresión: pasa también sin la ruta nueva, y de eso se trata
        — falla el día que alguien afloje el patrón de la región.
        """
        from django.urls import resolve
        self.assertEqual(
            resolve(f'/catalogo/{self.frutillar.slug}/geo-pdf/').url_name, 'parcela_geo_pdf')

    # --- punto 2: migas ----------------------------------------------------
    def test_migas_en_region_ciudad_y_parcela(self):
        for ruta in ['/catalogo/', '/catalogo/los-lagos/', '/catalogo/los-lagos/frutillar/',
                     self.frutillar.get_absolute_url()]:
            with self.subTest(ruta=ruta):
                self.assertIn('BreadcrumbList', _tipos(self.client.get(ruta)))

    def test_la_miga_de_la_parcela_pasa_por_region_y_ciudad(self):
        """Antes era Inicio > Catálogo > Parcela: saltaba justo los dos niveles
        a los que Jorge quiere traspasar autoridad."""
        migas = [s for s in _schemas(self.client.get(self.frutillar.get_absolute_url()))
                 if s['@type'] == 'BreadcrumbList'][0]
        nombres = [i['name'] for i in migas['itemListElement']]
        self.assertEqual(nombres, ['Inicio', 'Catálogo', 'Los Lagos', 'Frutillar',
                                   'Parcela junto al lago'])

    # --- punto 2.2: el negocio SOLO en la home -----------------------------
    def test_el_negocio_se_declara_en_la_home(self):
        self.assertIn('RealEstateAgent', _tipos(self.client.get('/')))

    def test_el_negocio_NO_se_repite_en_el_resto_del_sitio(self):
        for ruta in ['/catalogo/', '/catalogo/los-lagos/', '/contacto/']:
            with self.subTest(ruta=ruta):
                self.assertNotIn('RealEstateAgent', _tipos(self.client.get(ruta)))

    # --- punto 2.3: RealEstateAgent en la ficha ----------------------------
    def test_la_parcela_referencia_al_negocio_por_id(self):
        """Por @id y no repitiendo sus datos: si no, Google ve una agencia
        distinta por cada parcela en vez de una sola."""
        agentes = [s for s in _schemas(self.client.get(self.frutillar.get_absolute_url()))
                   if s['@type'] == 'RealEstateAgent']
        self.assertEqual(len(agentes), 1)
        self.assertTrue(agentes[0]['@id'].endswith('#negocio'))

    # --- punto 2.5: CollectionPage ----------------------------------------
    def test_coleccion_en_region_y_en_ciudad(self):
        for ruta in ['/catalogo/los-lagos/', '/catalogo/los-lagos/frutillar/']:
            with self.subTest(ruta=ruta):
                coleccion = [s for s in _schemas(self.client.get(ruta))
                             if s['@type'] == 'CollectionPage'][0]
                self.assertGreater(coleccion['mainEntity']['numberOfItems'], 0)

    # --- sitemap -----------------------------------------------------------
    def test_el_sitemap_trae_regiones_y_ciudades(self):
        xml = self.client.get('/sitemap.xml').content.decode('utf8')
        self.assertIn('/catalogo/los-lagos/', xml)
        self.assertIn('/catalogo/los-lagos/frutillar/', xml)

    def test_el_sitemap_no_publica_una_url_muerta(self):
        """Publicaba /reserva/, que es 404: la ruta real es /contacto/."""
        xml = self.client.get('/sitemap.xml').content.decode('utf8')
        self.assertNotIn('/reserva/', xml)
        self.assertIn('/contacto/', xml)


class ComentariosDePlantilla(TestCase):
    def test_ningun_comentario_de_django_es_multilinea(self):
        """`{# #}` solo vale en UNA línea: multilínea se IMPRIME en la página.

        Pasó ocho veces en estos repos, y las mediciones de desborde y de
        errores de consola dan verde igual. Por eso se comprueba con una prueba
        y no con el ojo.
        """
        from pathlib import Path
        base = Path(__file__).resolve().parent / 'templates'
        malos = []
        for archivo in base.rglob('*.html'):
            texto = archivo.read_text(encoding='utf-8')
            for m in re.finditer(r'\{#(.*?)#\}', texto, re.S):
                if '\n' in m.group(1):
                    malos.append(f'{archivo.name}:{texto[:m.start()].count(chr(10)) + 1}')
        self.assertEqual(malos, [], f'comentarios multilínea (usar {{% comment %}}): {malos}')
