# -*- coding: utf-8 -*-
"""Navidad 2026, v2 (17-11-2026): la decide el SERVIDOR por fecha.

Lo que se cuida:
  - Fuera de la ventana (16-11-2026 00:00 al 26-12-2026 23:59:59, hora de
    Chile) no llega NADA de la Navidad al navegador: ni la franja, ni la
    guirnalda, ni el CSS o el JS. Dentro, llega en el HTML (sin JS).
  - La franja dice el saludo y nada mas: sin precios ni ofertas.
  - El panel de Leonardo y el Tree (/links/) no la cargan.
  - El CSS solo actua bajo html.pp-navidad (para que el script la pueda apagar
    con la pestana abierta) y lo animado se apaga con reducir movimiento.
Que se vea bien, no tape nada y responda al toque se probo con Playwright.
"""
import re
from datetime import datetime
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

from django.conf import settings
from django.test import TestCase, override_settings

from . import context_processors as cp

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

CL = ZoneInfo('America/Santiago')
DENTRO = datetime(2026, 11, 20, 12, 0, tzinfo=CL)
ESTATICOS = Path(settings.BASE_DIR) / 'core' / 'static' / 'navidad'
SALUDO = '<strong>¡Felices Fiestas!</strong> les desea Punto Parcelas'


def _con_fecha(cuando):
    return mock.patch.object(cp, '_ahora', return_value=cuando)


@sin_manifiesto
class LaDecideElServidorPorFecha(TestCase):

    def _html(self, cuando, url='/'):
        with _con_fecha(cuando):
            return self.client.get(url).content.decode('utf8')

    def _hay_navidad(self, html):
        piezas = ('class="pp-navidad"', 'pp-franja-navidad', 'pp-guirnalda',
                  'navidad/navidad-2026.css', 'navidad/navidad-2026.js')
        return [p for p in piezas if p in html]

    def test_bordes_de_la_ventana(self):
        casos = [
            (datetime(2026, 11, 15, 23, 59, 59, tzinfo=CL), False),
            (datetime(2026, 11, 16, 0, 0, 0, tzinfo=CL), True),
            (datetime(2026, 12, 26, 23, 59, 59, tzinfo=CL), True),
            (datetime(2026, 12, 27, 0, 0, 0, tzinfo=CL), False),
        ]
        for cuando, debe in casos:
            with self.subTest(cuando=cuando.isoformat()):
                presentes = self._hay_navidad(self._html(cuando))
                if debe:
                    self.assertEqual(len(presentes), 5, presentes)
                else:
                    self.assertEqual(presentes, [])

    def test_la_hora_es_la_de_chile(self):
        # 27-12 00:30 en Chile son las 03:30 UTC: ya no corresponde.
        utc = datetime(2026, 12, 27, 3, 30, tzinfo=ZoneInfo('UTC'))
        self.assertEqual(self._hay_navidad(self._html(utc)), [])
        # 26-12 23:00 en Chile son las 02:00 UTC del 27: todavia si.
        utc = datetime(2026, 12, 27, 2, 0, tzinfo=ZoneInfo('UTC'))
        self.assertEqual(len(self._hay_navidad(self._html(utc))), 5)

    def test_las_paginas_publicas_traen_saludo_y_guirnalda_en_el_menu(self):
        for url in ('/', '/catalogo/', '/contacto/', '/guias/'):
            with self.subTest(url=url):
                html = self._html(DENTRO, url)
                self.assertIn(SALUDO, html)
                menu = re.search(r'<nav class="pp-nav" id="ppNav">(.*?)</nav>\s*<!-- MESSAGES -->', html, re.S).group(1)
                self.assertIn('class="pp-guirnalda"', menu)
                # La franja va antes que el menu (arriba del todo).
                self.assertLess(html.index('pp-franja-navidad'), html.index('id="ppNav"'))

    def test_el_saludo_no_ofrece_nada(self):
        html = self._html(DENTRO)
        franja = re.search(r'<div class="pp-franja-navidad".*?</div>', html, re.S).group(0)
        texto = re.sub(r'<[^>]+>', ' ', franja)
        for prohibido in ('$', 'UF', '%', 'oferta', 'descuento', 'precio', 'cuota'):
            self.assertNotIn(prohibido.lower(), texto.lower())

    def test_la_cuenta_regresiva_viene_del_servidor(self):
        html = self._html(datetime(2026, 12, 26, 23, 59, 0, tzinfo=CL))
        falta = int(re.search(r'data-navidad-falta="(\d+)"', html).group(1))
        self.assertEqual(falta, 59000)

    def test_el_panel_y_el_tree_no_la_cargan(self):
        for url in ('/admin-panel/login/', '/links/'):
            with self.subTest(url=url):
                html = self._html(DENTRO, url)
                self.assertNotIn('pp-navidad', html)
                self.assertNotIn('navidad-2026', html)
                self.assertNotIn('Felices Fiestas', html)


class ElCssYElJs(TestCase):

    def test_todo_el_css_cuelga_de_la_clase(self):
        css = (ESTATICOS / 'navidad-2026.css').read_text(encoding='utf8')
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        css = re.sub(r'url\("[^"]*"\)', 'url()', css)      # los SVG en linea no son selectores
        reglas = re.findall(r'([^{};]+)\{([^{}]*)\}', css)
        revisadas = 0
        for selector, cuerpo in reglas:
            for sel in (s.strip() for s in selector.split(',')):
                if sel.startswith('@') or sel in ('from', 'to') or sel.endswith('%') or sel == 'html.pp-navidad':
                    continue
                revisadas += 1
                with self.subTest(selector=sel):
                    if sel.startswith('html.pp-navidad '):
                        continue
                    # Lo unico permitido fuera de la clase: ESCONDER la franja y
                    # la guirnalda si el script quita la clase al terminar.
                    self.assertIn(sel, ('.pp-franja-navidad', '.pp-guirnalda'), sel)
                    self.assertEqual(cuerpo.strip(), 'display: none;')
        self.assertGreater(revisadas, 20)

    def test_lo_animado_se_apaga_con_menos_movimiento(self):
        css = (ESTATICOS / 'navidad-2026.css').read_text(encoding='utf8')
        bloque = css[css.index('@media (prefers-reduced-motion: reduce)'):]
        self.assertIn('.pp-guirnalda__luces { animation: none; }', bloque)
        self.assertIn('.pp-nieve { display: none; }', bloque)
        js = (ESTATICOS / 'navidad-2026.js').read_text(encoding='utf8')
        guarda = js.index('if (quieto && quieto.matches) return;')
        self.assertLess(guarda, js.index('nevar(portadas[p])'))

    def test_nada_decorativo_recibe_clics(self):
        css = (ESTATICOS / 'navidad-2026.css').read_text(encoding='utf8')
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        for regla in ('.pp-franja-navidad {', '.pp-guirnalda {', '.pp-nav::after {',
                      '.pp-nav .pp-logo-wrap::before {', '.wa-float::before {',
                      '.hero-ctas .btn-gold::after {', '.pp-nieve {'):
            with self.subTest(regla=regla):
                cuerpo = css[css.index('html.pp-navidad ' + regla):]
                self.assertIn('pointer-events: none', cuerpo[:cuerpo.index('}')])
