# -*- coding: utf-8 -*-
"""Credito del pie (02-11-2026, consejo SEO de Jorge Urzua).

El enlace a GoGoDevS lleva la palabra clave como texto ("Desarrollo web en
Chile") y no la marca, apunta a https://www.gogodevs.cl/ (con www, sin utm ni
nofollow) y la marca queda fuera del enlace: "<a>Desarrollo web en Chile</a>
por GoGoDevS". Va en el pie de base.html y en el Tree (/links/).
"""
import re

from django.test import TestCase, override_settings

ANCLA = 'Desarrollo web en Chile'

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


@sin_manifiesto
class CreditoDelPie(TestCase):
    def _revisar(self, url):
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200, f'{url} no respondio 200')
        html = r.content.decode('utf8')

        self.assertRegex(
            html,
            r'<a href="https://www\.gogodevs\.cl/" target="_blank" rel="noopener"[^>]*>'
            + re.escape(ANCLA) + r'</a> por GoGoDevS',
            f'{url}: el credito no usa la palabra clave como ancla',
        )
        enlaces = re.findall(r'<a [^>]*href="https?://[^"]*gogodevs\.cl[^"]*"[^>]*>', html)
        self.assertTrue(enlaces, f'{url}: no enlaza a gogodevs.cl')
        for a in enlaces:
            self.assertIn('href="https://www.gogodevs.cl/"', a)
            self.assertNotIn('utm_', a)
            self.assertNotIn('nofollow', a)
        # El texto antiguo usaba la marca como ancla.
        self.assertNotIn('>GoGoDevS</a>', html)
        self.assertNotIn('Diseñado y desarrollado por', html)

    def test_pie_del_sitio(self):
        self._revisar('/')

    def test_pie_del_tree(self):
        self._revisar('/links/')
