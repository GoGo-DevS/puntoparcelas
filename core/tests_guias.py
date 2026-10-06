# -*- coding: utf-8 -*-
"""Las 14 guias informacionales (Jorge Urzua, 05-10-2026).

LO QUE DE VERDAD SE PRUEBA ACA
------------------------------
No es que la pagina devuelva 200: eso lo haria igual con los enlaces rotos.
Lo que se prueba es la decision que se tomo al construirla.

El documento de Jorge afirma que las 12 comunas existen en el catalogo. Medido
el 06-10 contra el sitio en vivo, TRES destinos dan 404:

    /catalogo/araucania/villarrica/   404
    /catalogo/araucania/              404  (la region tampoco existe)
    /catalogo/valparaiso/algarrobo/   404

Y es correcto que den 404: una region o comuna sin parcelas no debe existir
(tests_regiones_vacias, 22-09). Por eso los enlaces se resuelven contra la base
al dibujar la pagina. Estas pruebas cuidan esa cascada en las dos direcciones:
que no se publique un 404, y que el enlace bueno SI aparezca cuando el dato
existe.
"""
from django.test import TestCase, override_settings

from . import guias as _guias
from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


@sin_manifiesto
class EnlacesSeResuelvenContraLaBase(TestCase):
    """La cascada comuna -> region -> catalogo."""

    @classmethod
    def setUpTestData(cls):
        # Los Lagos CON Puerto Varas. La Araucania y Valparaiso, sin nada:
        # son justo los casos que el documento da por existentes.
        Parcela.objects.create(
            nombre='Parcela junto al lago', region='los_lagos', ciudad='Puerto Varas',
            precio=45000000, moneda='CLP', estado='disponible')

    def test_comuna_con_parcelas_queda_tal_cual(self):
        self.assertEqual(
            _guias._ruta_viva('/catalogo/los-lagos/puerto-varas/'),
            '/catalogo/los-lagos/puerto-varas/')

    def test_comuna_sin_parcelas_baja_a_su_region(self):
        """Osorno no tiene parcelas, pero Los Lagos si: el enlace vale igual."""
        self.assertEqual(
            _guias._ruta_viva('/catalogo/los-lagos/osorno/'),
            '/catalogo/los-lagos/')

    def test_comuna_cuya_region_tampoco_existe_baja_al_catalogo(self):
        """El caso Villarrica: ni la comuna ni La Araucania existen hoy."""
        self.assertEqual(
            _guias._ruta_viva('/catalogo/araucania/villarrica/'),
            '/catalogo/')

    def test_region_vacia_baja_al_catalogo(self):
        self.assertEqual(_guias._ruta_viva('/catalogo/araucania/'), '/catalogo/')

    def test_region_con_parcelas_queda_tal_cual(self):
        self.assertEqual(_guias._ruta_viva('/catalogo/los-lagos/'), '/catalogo/los-lagos/')

    def test_la_home_y_las_guias_no_se_tocan(self):
        """Solo se verifican rutas de catalogo; el resto pasa sin consultar."""
        self.assertEqual(_guias._ruta_viva('/'), '/')
        self.assertEqual(_guias._ruta_viva('/guias/que-hacer-en-osorno/'),
                         '/guias/que-hacer-en-osorno/')

    def test_el_enlace_aparece_solo_cuando_leonardo_carga_la_parcela(self):
        """La razon de resolver contra la base y no cachear."""
        self.assertEqual(_guias._ruta_viva('/catalogo/araucania/villarrica/'), '/catalogo/')
        Parcela.objects.create(
            nombre='Parcela en el lago Villarrica', region='araucania', ciudad='Villarrica',
            precio=30000000, moneda='CLP', estado='disponible')
        self.assertEqual(_guias._ruta_viva('/catalogo/araucania/villarrica/'),
                         '/catalogo/araucania/villarrica/')


@sin_manifiesto
class NingunaGuiaPublicaUnEnlaceRoto(TestCase):
    """El barrido completo: las 14 guias, todos sus enlaces, contra la base real."""

    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(
            nombre='Parcela junto al lago', region='los_lagos', ciudad='Frutillar',
            precio=45000000, moneda='CLP', estado='disponible')

    def test_todos_los_destinos_resuelven_a_una_pagina_que_responde_200(self):
        rotas = []
        for slug in _guias.SLUGS:
            for _tipo, texto in _guias.GUIAS[slug]['cuerpo']:
                for m in _guias._ENLACE.finditer(texto):
                    destino = _guias._ruta_viva(m.group(2))
                    if self.client.get(destino).status_code != 200:
                        rotas.append('%s -> %s' % (slug, destino))
        self.assertEqual(rotas, [], 'enlaces que no responden 200: %s' % rotas)


@sin_manifiesto
class PaginasDeGuia(TestCase):

    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(
            nombre='Parcela junto al lago', region='los_lagos', ciudad='Puerto Varas',
            precio=45000000, moneda='CLP', estado='disponible')

    def test_las_14_responden_200(self):
        for slug in _guias.SLUGS:
            with self.subTest(slug=slug):
                self.assertEqual(self.client.get('/guias/%s/' % slug).status_code, 200)

    def test_el_indice_responde_y_lista_las_14(self):
        html = self.client.get('/guias/').content.decode()
        self.assertEqual(self.client.get('/guias/').status_code, 200)
        for slug in _guias.SLUGS:
            self.assertIn('/guias/%s/' % slug, html)

    def test_una_guia_inventada_es_404(self):
        self.assertEqual(self.client.get('/guias/que-hacer-en-marte/').status_code, 404)

    def test_el_h1_y_el_title_salen_del_documento(self):
        html = self.client.get('/guias/que-hacer-en-puerto-varas/').content.decode()
        self.assertIn('Qué hacer en Puerto Varas', html)
        self.assertIn('<title>Qué hacer en Puerto Varas | Punto Parcelas</title>', html)

    def test_los_marcadores_no_se_imprimen_en_la_pagina(self):
        """Si la plantilla no resolviera los [[...]], se verian crudos."""
        for slug in _guias.SLUGS:
            with self.subTest(slug=slug):
                html = self.client.get('/guias/%s/' % slug).content.decode()
                self.assertNotIn('[[', html)

    def test_el_enlace_se_dibuja_como_etiqueta_a(self):
        html = self.client.get('/guias/que-hacer-en-puerto-varas/').content.decode()
        self.assertIn('<a href="/catalogo/los-lagos/puerto-varas/">', html)

    def test_no_hay_comentarios_de_django_impresos(self):
        """Un {# #} de varias lineas se imprime entero: el bug mas repetido
        de estos repos (8 veces). Se mide en la pagina, no en la plantilla."""
        for ruta in ['/guias/', '/guias/que-hacer-en-osorno/']:
            with self.subTest(ruta=ruta):
                html = self.client.get(ruta).content.decode()
                self.assertNotIn('{#', html)
                self.assertNotIn('{%', html)


@sin_manifiesto
class SitemapYSchema(TestCase):

    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(
            nombre='Parcela junto al lago', region='los_lagos', ciudad='Puerto Varas',
            precio=45000000, moneda='CLP', estado='disponible')

    def test_el_sitemap_publica_las_14_y_el_indice(self):
        sm = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('https://puntoparcelas.cl/guias/</loc>', sm)
        for slug in _guias.SLUGS:
            self.assertIn('https://puntoparcelas.cl/guias/%s/' % slug, sm)

    def test_el_sitemap_no_publica_una_guia_que_no_existe(self):
        sm = self.client.get('/sitemap.xml').content.decode()
        self.assertNotIn('/guias/que-hacer-en-marte/', sm)

    def test_el_schema_de_la_guia_es_json_valido(self):
        """Se PARSEA, no se busca como texto: un bloque mal formado se ve igual
        en pantalla y Google lo descarta entero sin avisar."""
        import json
        import re
        html = self.client.get('/guias/que-hacer-en-osorno/').content.decode()
        bloques = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        self.assertTrue(bloques, 'la guía no declara ningún schema')
        tipos = set()
        for b in bloques:
            for d in (json.loads(b) if b.strip().startswith('[') else [json.loads(b)]):
                tipos.add(d.get('@type'))
        self.assertIn('BreadcrumbList', tipos)


@sin_manifiesto
class ElTextoSeEscapa(TestCase):
    """El contenido viene de un .docx y pasa por |safe en la plantilla.

    Hoy ningun texto de Jorge trae un `<` ni un `&`, asi que quitar el escape
    no rompe nada visible -- y por eso la mutacion que lo quitaba pasaba todas
    las demas pruebas. El dia que una guia nueva traiga "cabanas & quinchos" o
    un "<" suelto, sin esto se rompe la pagina o se inyecta marcado.
    """

    def test_el_texto_plano_se_escapa(self):
        html = _guias.con_enlaces('cabañas & quinchos <b>en oferta</b>')
        self.assertIn('&amp;', html)
        self.assertIn('&lt;b&gt;', html)
        self.assertNotIn('<b>', html)

    def test_se_escapa_el_texto_que_va_ANTES_de_un_enlace(self):
        """Son DOS tramos distintos y cada uno se escapa por su lado: el de
        antes de cada enlace y el que queda al final. Probar solo un texto sin
        enlaces deja el primero sin cubrir -- y asi fue: la mutacion que le
        quitaba el escape pasaba la prueba de arriba sin problema."""
        html = _guias.con_enlaces('<b>ojo</b> ver [[el catálogo|/catalogo/]] ahora')
        self.assertNotIn('<b>', html)
        self.assertIn('&lt;b&gt;ojo&lt;/b&gt;', html)

    def test_se_escapa_el_texto_ENTRE_dos_enlaces(self):
        html = _guias.con_enlaces(
            'ver [[uno|/catalogo/]] <i>y</i> [[dos|/catalogo/]] fin')
        self.assertNotIn('<i>', html)
        self.assertIn('&lt;i&gt;y&lt;/i&gt;', html)

    def test_el_anchor_tambien_se_escapa(self):
        html = _guias.con_enlaces('ver [[<script>x</script>|/catalogo/]] ahora')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_el_enlace_legitimo_sigue_siendo_html(self):
        """El escape no puede llevarse por delante el <a> que si queremos."""
        html = _guias.con_enlaces('ver [[el catálogo|/catalogo/]] ahora')
        self.assertIn('<a href="/catalogo/">el catálogo</a>', html)
