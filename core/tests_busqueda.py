# -*- coding: utf-8 -*-
"""El buscador del catalogo (Leonardo, 30-10-2026): sin tildes, sin puntos y con errores de tipeo."""
from django.test import TestCase, override_settings

from . import busqueda
from .models import Parcela

sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})


def _p(nombre, **extra):
    datos = dict(nombre=nombre, region='ohiggins', ciudad='Marchigüe', precio=17_990_000,
                 moneda='CLP', superficie=5000, estado='disponible')
    datos.update(extra)
    return Parcela.objects.create(**datos)


class Normalizar(TestCase):

    def test_quita_tildes_dieresis_y_puntuacion(self):
        self.assertEqual(busqueda.normalizar("San José de Marchigüe, O'Higgins."),
                         'san jose de marchigue o higgins')

    def test_texto_vacio(self):
        self.assertEqual(busqueda.normalizar(None), '')


class Coincide(TestCase):

    def test_sin_tilde_encuentra_con_tilde(self):
        self.assertTrue(busqueda.coincide('marchigue', 'San José de Marchigüe'))

    def test_sin_el_punto_del_titulo(self):
        self.assertTrue(busqueda.coincide('alma rapel parcelas con marina',
                                          'Alma Rapel: parcelas con marina.'))

    def test_error_de_tipeo(self):
        self.assertTrue(busqueda.coincide('panguipuli', 'Reserva Panguipulli'))

    def test_todas_las_palabras_tienen_que_estar(self):
        self.assertFalse(busqueda.coincide('rapel ovalle', 'Alma Rapel'))

    def test_una_palabra_distinta_no_se_cuela(self):
        # "rupanco" y "rapel" se parecen poco: corregir eso traeria basura.
        self.assertFalse(busqueda.coincide('rupanco', 'Alma Rapel'))

    def test_palabras_cortas_no_se_corrigen(self):
        self.assertFalse(busqueda.coincide('lo', 'Alma Rapel'))


@sin_manifiesto
class CatalogoBusca(TestCase):

    def setUp(self):
        _p('San José de Marchigüe')
        _p('Reserva Panguipulli', region='los_rios', ciudad='Panguipulli')
        _p('Vive Ovalle', region='coquimbo', ciudad='Ovalle')

    def _nombres(self, q):
        html = self.client.get('/catalogo/', {'q': q}).content.decode('utf8')
        return {n for n in ('San José de Marchigüe', 'Reserva Panguipulli', 'Vive Ovalle') if n in html}

    def test_sin_tilde(self):
        self.assertEqual(self._nombres('san jose de marchigue'), {'San José de Marchigüe'})

    def test_mal_escrito(self):
        self.assertEqual(self._nombres('panguipuli'), {'Reserva Panguipulli'})

    def test_mayusculas_y_puntos(self):
        self.assertEqual(self._nombres('VIVE. OVALLE'), {'Vive Ovalle'})

    def test_sin_resultados(self):
        self.assertEqual(self._nombres('rupanco'), set())
