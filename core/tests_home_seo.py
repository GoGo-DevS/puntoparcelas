# -*- coding: utf-8 -*-
"""El contenido SEO de la home (Jorge Urzua, 05-10-2026).

Lo que se cuida aca es una sola cosa, y es la que costaba plata: el documento
propone enlazar a 11 regiones y CUATRO de ellas devuelven 404 por no tener
parcelas (medido el 06-10). Copiar la lista habria puesto cuatro enlaces rotos
en la pagina con mas autoridad del sitio.
"""
import json
import re

from django.test import TestCase, override_settings

from . import contenido_home as _ch
from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


@sin_manifiesto
class BloqueDeRegiones(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Dos regiones con parcelas. Las otras nueve, vacias.
        Parcela.objects.create(nombre='Junto al lago', region='los_lagos',
                               ciudad='Frutillar', precio=45000000,
                               moneda='CLP', estado='disponible')
        Parcela.objects.create(nombre='Costa del secano', region='ohiggins',
                               ciudad='Litueche', precio=20000000,
                               moneda='CLP', estado='disponible')

    def test_solo_aparecen_las_regiones_que_tienen_parcelas(self):
        html = self.client.get('/').content.decode()
        self.assertIn('/catalogo/los-lagos/', html)
        self.assertIn('/catalogo/ohiggins/', html)

    def test_NO_aparecen_las_cuatro_regiones_que_dan_404(self):
        """El punto entero de esta prueba. Araucania, Los Rios, Biobio y Aysen
        estan en la lista del documento y no existen en el sitio."""
        html = self.client.get('/').content.decode()
        for muerta in ['araucania', 'los-rios', 'biobio', 'aysen']:
            with self.subTest(region=muerta):
                self.assertNotIn('/catalogo/%s/' % muerta, html)

    def test_ningun_enlace_de_la_home_devuelve_404(self):
        """El barrido: se siguen TODOS los enlaces internos de la portada."""
        html = self.client.get('/').content.decode()
        rotos = []
        for ruta in set(re.findall(r'href="(/[^"#]*)"', html)):
            if self.client.get(ruta).status_code not in (200, 301, 302):
                rotos.append(ruta)
        self.assertEqual(rotos, [], 'enlaces rotos en la home: %s' % rotos)

    def test_la_region_aparece_sola_cuando_leonardo_carga_una_parcela(self):
        self.assertNotIn('/catalogo/araucania/', self.client.get('/').content.decode())
        Parcela.objects.create(nombre='Orilla del Villarrica', region='araucania',
                               ciudad='Villarrica', precio=30000000,
                               moneda='CLP', estado='disponible')
        self.assertIn('/catalogo/araucania/', self.client.get('/').content.decode())


@sin_manifiesto
class PreguntasFrecuentes(TestCase):

    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(nombre='Junto al lago', region='los_lagos',
                               ciudad='Frutillar', precio=45000000,
                               moneda='CLP', estado='disponible')

    def test_las_seis_preguntas_se_VEN_en_la_pagina(self):
        html = self.client.get('/').content.decode()
        for pregunta, _ in _ch.PREGUNTAS:
            with self.subTest(pregunta=pregunta):
                self.assertIn(pregunta, html)

    def test_el_FAQPage_declara_exactamente_las_preguntas_visibles(self):
        """Declarar una pregunta que el visitante no ve es marcado enganoso y
        Google lo sanciona a mano. Se PARSEA el JSON, no se busca como texto:
        un bloque mal formado se ve igual en pantalla y Google lo descarta."""
        html = self.client.get('/').content.decode()
        bloques = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        faq = None
        for b in bloques:
            datos = json.loads(b)
            for d in (datos if isinstance(datos, list) else [datos]):
                if d.get('@type') == 'FAQPage':
                    faq = d
        self.assertIsNotNone(faq, 'la home no declara FAQPage')
        declaradas = [q['name'] for q in faq['mainEntity']]
        self.assertEqual(declaradas, [p for p, _ in _ch.PREGUNTAS])
        for nombre in declaradas:
            self.assertIn(nombre, html, 'pregunta declarada y no visible: %s' % nombre)

    def test_el_schema_no_lleva_marcadores_crudos(self):
        """En el JSON va texto plano: un [[...]] ahi se publicaria tal cual."""
        for _, texto in _ch.preguntas_planas():
            self.assertNotIn('[[', texto)
            self.assertNotIn(']]', texto)

    def test_las_guias_que_citan_las_respuestas_existen(self):
        """Dos respuestas enlazan a una guia. Si la guia no existiera, serian
        404 en la portada."""
        html = self.client.get('/').content.decode()
        for ruta in set(re.findall(r'href="(/guias/[^"]*)"', html)):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 200)


@sin_manifiesto
class FichaSeoDeLaHome(TestCase):

    @classmethod
    def setUpTestData(cls):
        Parcela.objects.create(nombre='Junto al lago', region='los_lagos',
                               ciudad='Frutillar', precio=45000000,
                               moneda='CLP', estado='disponible')

    def test_title_y_meta_son_los_de_la_ficha(self):
        html = self.client.get('/').content.decode()
        self.assertIn('<title>Parcelas en venta en Chile | Punto Parcelas</title>', html)
        self.assertIn('Parcelas y terrenos en venta en todo Chile.', html)

    def test_la_home_sigue_teniendo_UN_solo_h1(self):
        """Se cuentan ETIQUETAS, no la palabra.

        El template trae un comentario CSS, dentro de un <style>, que menciona
        "<h1>" para explicar un arreglo del 04-09. Ese bloque viaja al navegador,
        asi que buscar el texto suelto lo contaba como un h1 de verdad y la
        prueba fallaba teniendo la pagina correcta.
        """
        html = self.client.get('/').content.decode()
        limpio = re.sub(r'<(style|script)\b.*?</\1>', '', html,
                        flags=re.S | re.I)
        limpio = re.sub(r'<!--.*?-->', '', limpio, flags=re.S)
        self.assertEqual(len(re.findall(r'<h1[\s>]', limpio)), 1)

    def test_no_se_imprime_marcado_de_django_en_la_pagina(self):
        html = self.client.get('/').content.decode()
        self.assertNotIn('{#', html)
        self.assertNotIn('{%', html)
        self.assertNotIn('[[', html)
