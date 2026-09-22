"""La migracion 0014 aplica el ajuste de ciudades de Jorge (22-09) sin pisar
lo que Leonardo edito a mano desde su panel."""
import importlib

from django.apps import apps
from django.test import TestCase

from .models import Parcela

mig = importlib.import_module('core.migrations.0014_seo_ciudades_jorge_22_09')
BRISAS = next(c for c in mig.CAMBIOS if c['slug'] == 'brisas-del-arrayan')
PUNTILLA = next(c for c in mig.CAMBIOS if c['slug'] == 'fundo-la-puntilla')


def _parcela(c, **cambios):
    datos = dict(nombre=c['slug'], slug=c['slug'], region='ohiggins', precio=1,
                 moneda='CLP', superficie=5000, estado='disponible',
                 seo_title=c['old_title'], seo_h1=c['old_h1'], ciudad=c['old_ciudad'])
    datos.update(cambios)
    return Parcela.objects.create(**datos)


class AjusteCiudadesJorge(TestCase):
    def test_aplica_cuando_nadie_toco_la_ficha(self):
        _parcela(BRISAS)
        mig.aplicar(apps, None)
        p = Parcela.objects.get(slug='brisas-del-arrayan')
        self.assertEqual(p.ciudad, 'Pichilemu')
        self.assertIn('Pichilemu', p.seo_title)
        self.assertEqual(p.seo_h1, BRISAS['h1'])

    def test_no_pisa_lo_que_edito_leonardo(self):
        _parcela(BRISAS, seo_h1='Mi titulo propio', ciudad='Litueche / el cuzco')
        mig.aplicar(apps, None)
        p = Parcela.objects.get(slug='brisas-del-arrayan')
        self.assertEqual(p.seo_h1, 'Mi titulo propio')
        self.assertEqual(p.ciudad, 'Litueche / el cuzco')
        self.assertEqual(p.seo_title, BRISAS['title'])  # este si estaba intacto

    def test_se_puede_revertir(self):
        _parcela(BRISAS)
        mig.aplicar(apps, None)
        mig.revertir(apps, None)
        p = Parcela.objects.get(slug='brisas-del-arrayan')
        self.assertEqual((p.seo_title, p.seo_h1, p.ciudad),
                         (BRISAS['old_title'], BRISAS['old_h1'], BRISAS['old_ciudad']))

    def test_la_puntilla_no_se_llama_quirigua(self):
        # La planilla le copio el nombre de otra parcela
        self.assertNotIn('Quirigua', PUNTILLA['title'] + PUNTILLA['h1'])
        self.assertIn('Puntilla', PUNTILLA['title'])

    def test_todos_los_titles_llevan_la_marca(self):
        for c in mig.CAMBIOS:
            self.assertTrue(c['title'].endswith('| Punto Parcelas'), c['slug'])
