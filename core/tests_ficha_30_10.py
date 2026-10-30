# -*- coding: utf-8 -*-
"""Minuta de la reunion del 27-10-2026 y pedido de Leonardo del 30-10: la ficha empuja a agendar visita."""
from urllib.parse import unquote

from django.test import TestCase, override_settings

from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

DESCRIPCION = ('Parcelas de 5.000 m2 en Panguipulli.\n\n'
               '❓ PREGUNTAS FRECUENTES\n\n'
               '¿Tienen luz y agua?\nSí, cada parcela.\n\n'
               '¿Cuánto mide cada parcela?\n5.000 m².')


@sin_manifiesto
class FichaAgendar(TestCase):

    def setUp(self):
        self.p = Parcela.objects.create(
            nombre='Reserva Panguipulli', region='los_rios', ciudad='Panguipulli',
            precio=29_990_000, moneda='CLP', superficie=5000, estado='disponible',
            descripcion=DESCRIPCION, video_url='https://youtu.be/abcdefghijk')
        self.html = self.client.get(self.p.get_absolute_url()).content.decode('utf8')

    def test_las_preguntas_van_despues_del_video(self):
        self.assertLess(self.html.index('Video del proyecto'), self.html.index('Preguntas frecuentes'))

    def test_cada_pregunta_es_un_desplegable_con_h3(self):
        self.assertEqual(self.html.count('<details class="pp-faq__item">'), 2)
        self.assertIn('<summary><h3 class="pp-faq__q">¿Tienen luz y agua?</h3></summary>', self.html)

    def test_el_faqpage_sigue_declarando_las_preguntas(self):
        self.assertIn('"FAQPage"', self.html)
        self.assertIn('¿Cuánto mide cada parcela?', self.html.split('"FAQPage"', 1)[1])

    def test_el_whatsapp_de_agendar_nombra_la_parcela_y_su_link(self):
        enlaces = [unquote(a) for a in self.html.split('href="https://wa.me/56964090173?text=')[1:]]
        agendar = [e for e in enlaces if e.startswith('Hola Leonardo, quiero agendar una visita a Reserva Panguipulli.')]
        # el de la barra lateral y el fijo del celular
        self.assertEqual(len(agendar), 2)
        self.assertIn(self.p.get_absolute_url(), agendar[0].split('"', 1)[0])

    def test_el_formulario_sigue_mandando_a_reserva(self):
        self.assertIn('name="telefono"', self.html)
        self.assertIn('Quiero que me llamen', self.html)
