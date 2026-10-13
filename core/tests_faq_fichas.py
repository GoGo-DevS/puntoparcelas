# -*- coding: utf-8 -*-
"""Las preguntas que Leonardo escribe en la descripcion: H3 + FAQPage (punto 10 de Jorge).

Los casos del parser son los de analizar_faq_fichas.py (06-10-2026), pasados
a texto plano, que es como Leonardo los guarda. Cada uno salio de una ficha
real que lo rompia.
"""
import json
import re

from django.test import SimpleTestCase, TestCase, override_settings

from . import faq
from .models import Parcela

Q = faq.ABRE
EMOJI = faq.INTERROGA
MOVIL = faq.MOVIL


class Parser(SimpleTestCase):

    def test_parrafos_con_cierre_comercial(self):
        texto = (f'Linda parcela.\n\n{EMOJI} PREGUNTAS FRECUENTES\n\n'
                 f'{Q}Cual es el valor?\nEs de $30.000.000.\n\n'
                 f'{Q}Tiene rol?\nSi. Tiene rol propio.\n\n'
                 f'{MOVIL} AGENDA TU VISITA\nVen a conocerla.')
        arriba, preguntas, abajo = faq.partir(texto)
        self.assertEqual(arriba, 'Linda parcela.')
        self.assertEqual(preguntas, [(f'{Q}Cual es el valor?', 'Es de $30.000.000.'),
                                     (f'{Q}Tiene rol?', 'Si. Tiene rol propio.')])
        # El cierre no entra en la ultima respuesta, pero tampoco se pierde.
        self.assertIn('AGENDA TU VISITA', abajo)
        self.assertIn('Ven a conocerla.', abajo)

    def test_un_bloque_pegado(self):
        texto = (f'BRISASNuevo proyecto. {EMOJI} PREGUNTAS FRECUENTES '
                 f'{Q}Desde que valor? Desde $29.990.000. '
                 f'{Q}Hay financiamiento? Si, con pie y cuotas.')
        arriba, preguntas, _ = faq.partir(texto)
        self.assertEqual(len(preguntas), 2)
        self.assertEqual(preguntas[0][1], 'Desde $29.990.000.')
        self.assertEqual(arriba, 'BRISASNuevo proyecto.')

    def test_el_gancho_antes_del_marcador_no_es_una_pregunta(self):
        texto = (f'{Q}POR QUE ELEGIR ESTE FUNDO?\nPorque combina tres cosas.\n\n'
                 f'{EMOJI} PREGUNTAS FRECUENTES\n{Q}Cuanto mide?\nSon 5.000 m2.')
        arriba, preguntas, _ = faq.partir(texto)
        self.assertEqual(len(preguntas), 1)
        self.assertIn('POR QUE ELEGIR', arriba)

    def test_una_sola_pregunta_con_cierre_pegado(self):
        texto = (f'Hola. {EMOJI} PREGUNTAS FRECUENTES {Q}Puedo visitar? Si, claro. '
                 f'{MOVIL} AGENDA TU VISITA Ven a verla.')
        arriba, preguntas, abajo = faq.partir(texto)
        self.assertEqual(preguntas, [(f'{Q}Puedo visitar?', 'Si, claro.')])
        self.assertEqual(arriba, 'Hola.')
        self.assertTrue(abajo.startswith(MOVIL))

    def test_sin_marcador_la_descripcion_queda_igual(self):
        texto = f'Solo descripcion.\n{Q}Y esto?\nNo es FAQ.'
        self.assertEqual(faq.partir(texto), (texto, [], ''))

    def test_pregunta_sin_respuesta_no_se_declara(self):
        texto = f'Algo.\n{EMOJI} PREGUNTAS FRECUENTES\n{Q}Y esta?'
        # Sin ninguna pregunta valida, se muestra todo como antes.
        self.assertEqual(faq.partir(texto), (texto, [], ''))

    def test_el_texto_entre_el_titulo_y_la_primera_pregunta_no_se_pierde(self):
        texto = f'Arriba.\n{EMOJI} PREGUNTAS FRECUENTES\nTe respondemos:\n{Q}Mide?\nSi.'
        arriba, preguntas, _ = faq.partir(texto)
        self.assertIn('Te respondemos:', arriba)
        self.assertEqual(len(preguntas), 1)

    def test_vacia_o_none(self):
        self.assertEqual(faq.partir(''), ('', [], ''))
        self.assertEqual(faq.partir(None), ('', [], ''))


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class EnLaFicha(TestCase):

    def setUp(self):
        self.p = Parcela.objects.create(
            nombre='Fundo Santa Rosa', region='valparaiso', ciudad='Santo Domingo',
            precio=45000000, moneda='CLP', superficie=5000, estado='disponible',
            descripcion=(f'Parcelas frente al mar.\n\n{EMOJI} PREGUNTAS FRECUENTES\n\n'
                         f'{Q}Tiene rol propio?\nSi, cada lote tiene su rol.\n\n'
                         f'{Q}Hay credito?\nSi, con pie desde $3.000.000.\n\n'
                         f'{MOVIL} AGENDA TU VISITA'))

    def _html(self):
        return self.client.get(self.p.get_absolute_url()).content.decode('utf8')

    def _schemas(self, html):
        bloque = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        datos = json.loads(bloque)
        return datos if isinstance(datos, list) else [datos]

    def test_cada_pregunta_es_un_h3(self):
        html = self._html()
        self.assertIn(f'<h3 class="pp-faq__q">{Q}Tiene rol propio?</h3>', html)
        self.assertIn(f'<h3 class="pp-faq__q">{Q}Hay credito?</h3>', html)

    def test_declara_faqpage_solo_con_lo_que_se_ve(self):
        html = self._html()
        faqs = [s for s in self._schemas(html) if s.get('@type') == 'FAQPage']
        self.assertEqual(len(faqs), 1)
        nombres = [q['name'] for q in faqs[0]['mainEntity']]
        self.assertEqual(nombres, [f'{Q}Tiene rol propio?', f'{Q}Hay credito?'])
        for n in nombres:
            self.assertIn(f'>{n}</h3>', html)

    def test_el_resto_de_la_descripcion_sigue_visible(self):
        html = self._html()
        self.assertIn('Parcelas frente al mar.', html)
        self.assertIn('AGENDA TU VISITA', html)

    def test_una_ficha_sin_preguntas_no_declara_faqpage(self):
        self.p.descripcion = 'Solo texto.'
        self.p.save()
        html = self._html()
        self.assertFalse([s for s in self._schemas(html) if s.get('@type') == 'FAQPage'])
        self.assertNotIn('class="pp-faq__q"', html)
