# -*- coding: utf-8 -*-
"""Documento "Prioridades Punto Parcelas" de Jorge (05-10-2026), la parte de plantilla.

Puntos 4, 5, 6, 12, 14 y 15. Cada prueba mira la pagina servida, no el codigo:
un ALT o un canonical que esta en la plantilla pero no sale en el HTML no le
sirve a Google.
"""
import re
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import FotoParcela, Parcela

MEDIA_TMP = tempfile.mkdtemp(prefix='pp-test-media-')

sin_manifiesto = override_settings(
    MEDIA_ROOT=MEDIA_TMP,
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    },
)

# Un GIF de 1x1: basta para que el ImageField acepte el archivo.
GIF = (b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x00'
       b'\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')


def _parcela(**extra):
    datos = dict(nombre='Fundo Santa Rosa', region='valparaiso', ciudad='Santo Domingo',
                 precio=45000000, moneda='CLP', superficie=5000, estado='disponible')
    datos.update(extra)
    return Parcela.objects.create(**datos)


@sin_manifiesto
class AltDeLasFotos(TestCase):
    """Punto 4: el ALT de cada foto es el H1 de la ficha, sin que nadie lo escriba."""

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def setUp(self):
        self.p = _parcela(seo_h1='Parcela en Santo Domingo con vista al mar')
        for i in range(3):
            FotoParcela.objects.create(parcela=self.p, orden=i, principal=(i == 0),
                                       imagen=SimpleUploadedFile(f'f{i}.gif', GIF, 'image/gif'))

    def _html(self):
        return self.client.get(self.p.get_absolute_url()).content.decode('utf8')

    def test_ninguna_foto_queda_con_alt_foto(self):
        self.assertNotIn('alt="foto"', self._html())

    def test_las_miniaturas_llevan_el_h1_numerado(self):
        html = self._html()
        for n in (1, 2, 3):
            self.assertIn(f'alt="Parcela en Santo Domingo con vista al mar — foto {n}"', html)

    def test_sin_h1_seo_cae_en_el_nombre(self):
        self.p.seo_h1 = ''
        self.p.save()
        self.assertIn('alt="Fundo Santa Rosa — foto 1"', self._html())


@sin_manifiesto
class MigasVisibles(TestCase):
    """Punto 5: la ficha muestra region y ciudad, con enlace, y termina en el H1."""

    def setUp(self):
        self.p = _parcela(seo_h1='Parcela en Santo Domingo con vista al mar')

    def test_las_migas_pasan_por_region_y_ciudad(self):
        html = self.client.get(self.p.get_absolute_url()).content.decode('utf8')
        nav = html[html.index('aria-label="Migas"'):]
        nav = nav[:nav.index('</nav>')]
        self.assertIn('href="/catalogo/valparaiso/"', nav)
        self.assertIn('href="/catalogo/valparaiso/santo-domingo/"', nav)
        self.assertIn('Parcela en Santo Domingo con vista al mar', nav)

    def test_cada_miga_es_el_h1_de_su_pagina(self):
        # Feedback de Jorge del 13-10: "Parcelas en Valparaíso", no "Valparaíso".
        # Se compara contra el H1 SERVIDO de cada pagina, no contra un texto fijo.
        html = self.client.get(self.p.get_absolute_url()).content.decode('utf8')
        nav = html[html.index('aria-label="Migas"'):]
        nav = nav[:nav.index('</nav>')]
        for ruta in ('/catalogo/valparaiso/', '/catalogo/valparaiso/santo-domingo/'):
            pagina = self.client.get(ruta).content.decode('utf8')
            h1 = pagina.split('<h1', 1)[1].split('>', 1)[1].split('<', 1)[0].strip()
            self.assertIn(f'href="{ruta}" style="color:var(--pp-muted); text-decoration:none;">{h1}</a>', nav)

    def test_los_enlaces_de_las_migas_no_dan_404(self):
        for ruta in ('/catalogo/valparaiso/', '/catalogo/valparaiso/santo-domingo/'):
            self.assertEqual(self.client.get(ruta).status_code, 200, ruta)

    def test_el_schema_dice_lo_mismo_que_la_pantalla(self):
        html = self.client.get(self.p.get_absolute_url()).content.decode('utf8')
        self.assertIn('"name": "Parcelas en Santo Domingo"', html)
        self.assertIn('"name": "Parcela en Santo Domingo con vista al mar"', html)

    def test_una_ficha_sin_ciudad_salta_ese_tramo(self):
        p = _parcela(nombre='Sin ciudad', ciudad='')
        html = self.client.get(p.get_absolute_url()).content.decode('utf8')
        nav = html[html.index('aria-label="Migas"'):html.index('</nav>', html.index('aria-label="Migas"'))]
        self.assertIn('href="/catalogo/valparaiso/"', nav)
        self.assertEqual(nav.count('href='), 3)  # Inicio, Catalogo, Region


@sin_manifiesto
class FooterConRegionesYGuias(TestCase):
    """Puntos 6 y 14."""

    def setUp(self):
        _parcela()

    def _footer(self, ruta='/'):
        html = self.client.get(ruta).content.decode('utf8')
        return html[html.index('<footer'):]

    def test_las_regiones_con_parcelas_estan_enlazadas_con_su_h1(self):
        self.assertIn('<a href="/catalogo/valparaiso/">Parcelas en Valparaíso</a>', self._footer())

    def test_una_region_sin_parcelas_no_sale_en_el_footer(self):
        footer = self._footer()
        self.assertNotIn('/catalogo/biobio/', footer)
        self.assertNotIn('Biobío', footer)

    def test_el_footer_va_en_todas_las_paginas(self):
        self.assertIn('/catalogo/valparaiso/', self._footer('/catalogo/'))
        self.assertIn('/catalogo/valparaiso/', self._footer('/guias/'))

    def test_el_footer_enlaza_a_las_guias(self):
        self.assertIn('href="/guias/"', self._footer())


@sin_manifiesto
class Paginacion(TestCase):
    """Punto 12: cada pagina se declara a si misma y su title dice que pagina es."""

    @classmethod
    def setUpTestData(cls):
        for i in range(20):  # 15 por pagina: quedan 2
            _parcela(nombre=f'Parcela {i:02d}', ciudad='Santo Domingo')

    def _head(self, ruta):
        html = self.client.get(ruta).content.decode('utf8')
        title = re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip()
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html).group(1)
        return title, canonical

    def test_la_pagina_1_no_cambia(self):
        title, canonical = self._head('/catalogo/valparaiso/')
        self.assertTrue(canonical.endswith('/catalogo/valparaiso/'), canonical)
        self.assertNotIn('Página', title)

    def test_la_pagina_2_tiene_su_propio_canonical(self):
        title, canonical = self._head('/catalogo/valparaiso/?page=2')
        self.assertTrue(canonical.endswith('/catalogo/valparaiso/?page=2'), canonical)
        self.assertTrue(title.endswith('– Página 2'), title)

    def test_el_canonical_no_arrastra_otros_parametros(self):
        _title, canonical = self._head('/catalogo/valparaiso/?page=2&utm_source=x')
        self.assertTrue(canonical.endswith('/catalogo/valparaiso/?page=2'), canonical)

    def test_page_1_explicita_canonicaliza_a_la_limpia(self):
        _title, canonical = self._head('/catalogo/valparaiso/?page=1')
        self.assertTrue(canonical.endswith('/catalogo/valparaiso/'), canonical)

    def test_los_enlaces_no_repiten_la_region_que_ya_esta_en_la_ruta(self):
        html = self.client.get('/catalogo/valparaiso/').content.decode('utf8')
        self.assertIn('href="?page=2"', html)
        self.assertNotIn('region=valparaiso&', html)

    def test_la_busqueda_se_conserva_al_pasar_de_pagina(self):
        html = self.client.get('/catalogo/?q=Parcela').content.decode('utf8')
        self.assertIn('href="?q=Parcela&amp;page=2"', html)


@sin_manifiesto
class NombresComoH2(TestCase):
    """Punto 15: en las paginas de categoria el nombre de cada parcela es un H2."""

    def setUp(self):
        _parcela(nombre='Fundo Santa Rosa')

    def test_region_ciudad_y_catalogo(self):
        for ruta in ('/catalogo/', '/catalogo/valparaiso/', '/catalogo/valparaiso/santo-domingo/'):
            html = self.client.get(ruta).content.decode('utf8')
            self.assertIn('<h2 class="parcela-card-nombre">Fundo Santa Rosa</h2>', html, ruta)
