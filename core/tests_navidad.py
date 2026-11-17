# -*- coding: utf-8 -*-
"""Navidad 2026 (16-11-2026): la decoracion nace OCULTA.

Lo que se cuida: fuera de fecha o sin JS el sitio se ve exactamente como
siempre. Eso depende de dos cosas que se comprueban sin navegador:
  1. todo el CSS de la decoracion cuelga de html.pp-navidad (o del lienzo de
     nieve, que solo existe si el script lo crea);
  2. el script pone esa clase solo despues de revisar las dos fechas.
Que se encienda y se apague con el reloj del navegador se probo aparte con
Playwright (reloj simulado al 15-11, al 16-11 y al 27-12).
Ademas: no agrega texto visible y no llega al panel de Leonardo.
"""
import re

from django.template.loader import render_to_string
from django.test import TestCase, override_settings

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

INICIO = 'new Date("2026-11-16T00:00:00-03:00")'
FIN = 'new Date("2026-12-26T23:59:59-03:00")'


def _parcial():
    return render_to_string('core/_navidad.html')


@sin_manifiesto
class NavidadNaceOculta(TestCase):

    def test_las_paginas_publicas_la_traen(self):
        for url in ('/', '/catalogo/', '/contacto/', '/guias/'):
            with self.subTest(url=url):
                html = self.client.get(url).content.decode('utf8')
                self.assertIn(INICIO, html)
                self.assertIn(FIN, html)

    def test_el_panel_de_leonardo_no_la_trae(self):
        html = self.client.get('/admin-panel/login/').content.decode('utf8')
        self.assertNotIn('pp-navidad', html)

    def test_todo_el_css_cuelga_de_la_clase_que_pone_el_script(self):
        css = re.search(r'<style>(.*?)</style>', _parcial(), re.S).group(1)
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        selectores = [s.strip() for bloque in re.findall(r'([^{};]+)\{', css)
                      for s in bloque.split(',')]
        revisados = 0
        for sel in selectores:
            if sel.startswith('@') or sel in ('from', 'to') or sel.endswith('%'):
                continue
            revisados += 1
            with self.subTest(selector=sel):
                self.assertTrue(sel.startswith('html.pp-navidad ') or sel == '.pp-nieve',
                                'esta regla se veria fuera de fecha o sin JS: %s' % sel)
        self.assertGreaterEqual(revisados, 4)

    def test_la_clase_se_pone_solo_despues_de_mirar_las_fechas(self):
        js = re.search(r'<script>(.*?)</script>', _parcial(), re.S).group(1)
        guarda = js.index('if (!(ahora >= INICIO && ahora <= FIN)) return;')
        self.assertEqual(js.count('classList.add('), 1)
        self.assertLess(js.index(INICIO), guarda)
        self.assertLess(js.index(FIN), guarda)
        self.assertLess(guarda, js.index('classList.add("pp-navidad")'))

    def test_sin_nieve_si_se_pidio_menos_movimiento(self):
        p = _parcial()
        self.assertIn('prefers-reduced-motion: reduce', p)
        self.assertRegex(p, r'if \(quieto && quieto\.matches\) return;')

    def test_no_agrega_texto_visible(self):
        resto = re.sub(r'<(style|script)>.*?</\1>', '', _parcial(), flags=re.S)
        self.assertEqual(resto.strip(), '')
