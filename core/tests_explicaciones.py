# -*- coding: utf-8 -*-
"""El texto propio de cada pagina de caracteristica.

POR QUE EXISTE
--------------
Medido contra el sitio en vivo el 04-10:

    parcela-de-campo  vs  parcela-de-agrado        96% identicas
    parcela-de-campo  vs  parcela-con-rol-propio   87%

Las tres muestran las MISMAS 116 parcelas (el catalogo completo, porque
Leonardo dijo "todas") y solo cambiaba el H1 y una linea de bajada. Google eso
lo lee como la misma pagina publicada tres veces: elige una, degrada las otras
dos y de paso compiten entre ellas por la misma busqueda.

Lo que estas pruebas cuidan es que cada pagina tenga contenido que la
diferencie de verdad, y que el FAQPage declare SOLO lo que se ve.
"""
import difflib
import json
import re

from django.test import TestCase

from core import caracteristicas as car
from core.models import Parcela


def _texto(html):
    html = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', html, flags=re.S)
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', html)).strip()


class ExplicacionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # VEINTE parcelas, no una. Con una sola la grilla es tan corta que la
        # bajada de dos lineas ya hace bajar el parecido entre las paginas, y
        # el test pasaba aunque se quitara el texto propio -- justo lo que
        # tiene que cazar. En produccion son 116: la grilla domina el HTML y
        # dos paginas sin texto propio quedan 96% iguales.
        cls.parcelas = [
            Parcela.objects.create(
                nombre=f"Hacienda de prueba {i}", region="los_lagos", ciudad="Osorno",
                superficie=5000, precio=8_000_000, moneda="CLP",
                rol_propio=True, tiene_agua=True, tiene_luz=True,
                estado="disponible",
            )
            for i in range(20)
        ]
        cls.parcela = cls.parcelas[0]

    # --- lo que motivo todo esto ------------------------------------------

    def test_campo_y_agrado_dejan_de_ser_la_misma_pagina(self):
        a = _texto(self.client.get("/catalogo/parcela-de-campo/").content.decode())
        b = _texto(self.client.get("/catalogo/parcela-de-agrado/").content.decode())
        parecido = difflib.SequenceMatcher(None, a, b).ratio()
        self.assertLess(parecido, 0.90,
                        f"siguen {parecido:.0%} parecidas: Google las lee como duplicado")

    def test_campo_y_rol_propio_tampoco(self):
        a = _texto(self.client.get("/catalogo/parcela-de-campo/").content.decode())
        b = _texto(self.client.get("/catalogo/parcela-con-rol-propio/").content.decode())
        self.assertLess(difflib.SequenceMatcher(None, a, b).ratio(), 0.90)

    # --- el texto esta de verdad en la pagina ------------------------------

    def test_cada_pagina_trae_su_propio_texto_y_no_el_de_la_otra(self):
        """Directo, sin depender del parecido: cada una dice lo suyo."""
        campo = self.client.get("/catalogo/parcela-de-campo/").content.decode()
        agrado = self.client.get("/catalogo/parcela-de-agrado/").content.decode()
        self.assertIn("¿Qué es una parcela de campo?", campo)
        self.assertNotIn("¿Qué es una parcela de campo?", agrado)
        self.assertIn("¿Qué es una parcela de agrado?", agrado)
        self.assertNotIn("¿Qué es una parcela de agrado?", campo)

    def test_la_explicacion_se_dibuja(self):
        html = self.client.get("/catalogo/parcela-de-agrado/").content.decode()
        self.assertIn("¿Qué es una parcela de agrado?", html)
        self.assertIn("3.516", html)   # el decreto ley, que es el dato duro

    def test_cada_pagina_dice_algo_distinto(self):
        vistos = {}
        for slug in car.SLUGS:
            bloques = car.explicacion(slug)
            if not bloques:
                continue
            for titulo, texto in bloques:
                self.assertNotIn(titulo, vistos,
                                 f"'{titulo}' se repite en {slug} y en {vistos.get(titulo)}")
                vistos[titulo] = slug
                self.assertGreater(len(texto), 120, f"{slug}: '{titulo}' es muy corto")

    def test_el_catalogo_normal_no_lleva_explicacion(self):
        """Es texto por caracteristica: en /catalogo/ no corresponde."""
        html = self.client.get("/catalogo/").content.decode()
        self.assertNotIn("car-explica__item", html)

    # --- el schema no puede prometer lo que no se ve -----------------------

    def _schemas(self, ruta):
        html = self.client.get(ruta).content.decode()
        fuera = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            d = json.loads(m.group(1))
            fuera.extend(d if isinstance(d, list) else [d])
        return fuera, html

    def test_el_faqpage_declara_solo_preguntas_visibles(self):
        schemas, html = self._schemas("/catalogo/parcela-de-agrado/")
        faq = [s for s in schemas if s.get("@type") == "FAQPage"]
        self.assertEqual(len(faq), 1, "falta el FAQPage")
        for q in faq[0]["mainEntity"]:
            # declarar una pregunta que el visitante no ve es marcado engañoso
            self.assertIn(q["name"], html, q["name"])

    def test_la_pagina_de_caracteristica_declara_su_listado(self):
        """Antes solo las de region declaraban la coleccion."""
        schemas, _ = self._schemas("/catalogo/parcela-de-campo/")
        tipos = [s.get("@type") for s in schemas]
        self.assertIn("CollectionPage", tipos, tipos)

    def test_sin_explicacion_no_se_declara_un_faqpage_vacio(self):
        """Las caracteristicas marcadas a mano no tienen texto propio todavia.
        Un FAQPage sin preguntas es marcado invalido."""
        self.parcela.vista_lago = True
        self.parcela.save(update_fields=["vista_lago"])
        schemas, _ = self._schemas("/catalogo/parcela-vista-al-lago/")
        for s in schemas:
            if s.get("@type") == "FAQPage":
                self.fail("declara un FAQPage sin preguntas visibles")
