# -*- coding: utf-8 -*-
"""Las paginas por caracteristica (hoja 04 de la planilla de Indexo, 02-10-2026)."""
import re

from django.test import TestCase, override_settings

# Mismo override que usan tests_seo_ciudades.py y el resto: el almacen de
# produccion exige el manifiesto de collectstatic y sin correrlo CUALQUIER
# pagina revienta en {% static %}, con un error que no dice nada del SEO.
sin_manifiesto = override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

from . import caracteristicas as car
from .models import Parcela


def _parcela(nombre, **kw):
    datos = dict(nombre=nombre, region='maule', precio=50_000_000, moneda='CLP',
                 superficie=5000, estado='disponible')
    datos.update(kw)
    return Parcela.objects.create(**datos)


@sin_manifiesto
class Base(TestCase):
    @classmethod
    def setUpTestData(cls):
        _parcela('Vive Rupanco', region='los_lagos', vista_lago=True)
        _parcela('Parque Algarrobo', vista_mar=True, cerca_playa=True, credito_directo=True)
        _parcela('Fundo Barato', precio=8_000_000, rol_propio=True)
        _parcela('Con Servicios', tiene_agua=True, tiene_luz=True)


@sin_manifiesto
class LasPaginasResponden(Base):

    def test_cada_caracteristica_con_parcelas_responde_200(self):
        for slug in car.SLUGS:
            if not Parcela.objects.exclude(estado='vendida').filter(car.filtro(slug)).exists():
                continue
            with self.subTest(slug=slug):
                self.assertEqual(self.client.get(f'/catalogo/{slug}/').status_code, 200)

    def test_el_h1_es_el_de_la_planilla(self):
        r = self.client.get('/catalogo/parcela-vista-al-lago/')
        self.assertEqual(r.context['seo_h1'], 'Parcelas con vista al lago')

    def test_solo_muestra_las_que_cumplen(self):
        r = self.client.get('/catalogo/parcela-vista-al-lago/')
        nombres = [p.nombre for p in r.context['page_obj']]
        self.assertEqual(nombres, ['Vive Rupanco'])


@sin_manifiesto
class LoQueNoSePublica(Base):

    def test_una_caracteristica_sin_parcelas_es_404_y_no_una_pagina_vacia(self):
        """Un 200 vacio lo indexa Google igual y compite contra las que si
        tienen contenido. Por eso la vista levanta Http404."""
        Parcela.objects.filter(vista_lago=True).delete()
        self.assertEqual(self.client.get('/catalogo/parcela-vista-al-lago/').status_code, 404)

    def test_las_que_leonardo_no_tiene_no_existen(self):
        # "parcela con casa": el dijo "nada por ahora" (01-10). "parcela rural":
        # Jorge la pide y el no la nombro.
        for slug in car.NO_PUBLICADAS:
            with self.subTest(slug=slug):
                self.assertEqual(self.client.get(f'/catalogo/{slug}/').status_code, 404)


@sin_manifiesto
class NoSeTragaLasFichas(Base):
    """La prueba cara.

    El patron nuevo vive en /catalogo/<algo>/, el MISMO espacio donde viven las
    43 fichas de parcela. Si el slug no fuera una lista acotada, este patron se
    comeria todas las fichas del sitio y nadie lo notaria hasta que un cliente
    abriera una.
    """

    def test_la_ficha_de_una_parcela_sigue_abriendo(self):
        p = Parcela.objects.get(nombre='Vive Rupanco')
        self.assertEqual(self.client.get(f'/catalogo/{p.slug}/').status_code, 200)

    def test_el_plano_geo_de_una_parcela_sigue_resolviendo(self):
        p = Parcela.objects.get(nombre='Vive Rupanco')
        # Sin plano cargado da 404, pero por el PLANO, no por la ruta: lo que
        # se comprueba es que resuelve a parcela_geo_pdf y no al patron nuevo.
        from django.urls import resolve
        self.assertEqual(resolve(f'/catalogo/{p.slug}/geo-pdf/').url_name, 'parcela_geo_pdf')

    def test_region_y_ciudad_siguen_resolviendo_a_lo_suyo(self):
        from django.urls import resolve
        self.assertEqual(resolve('/catalogo/los-lagos/').url_name, 'catalogo_region')
        self.assertEqual(resolve('/catalogo/los-lagos/puerto-varas/').url_name, 'catalogo_ciudad')


@sin_manifiesto
class LasDerivadasSeRecalculanSolas(Base):
    """Las 6 derivadas NO son una casilla: salen del dato que Leonardo ya edita.

    Si fueran manuales, el dia que el baje un precio la pagina quedaria
    mintiendo sin que nada avise.
    """

    def test_bajarle_el_precio_a_una_parcela_la_mete_en_baratas(self):
        p = Parcela.objects.get(nombre='Vive Rupanco')
        self.assertNotIn(p, self.client.get('/catalogo/parcelas-baratas/').context['page_obj'])
        p.precio = 9_000_000
        p.save(update_fields=['precio'])
        self.assertIn(p.nombre, [x.nombre for x in
                                 self.client.get('/catalogo/parcelas-baratas/').context['page_obj']])

    def test_una_parcela_en_UF_no_entra_en_baratas(self):
        """Leonardo: Algarrobo y Puerto Varas estan en UF y valen mas de 100
        millones. Comparar 2.800 UF contra 10.000.000 las haria 'baratas'."""
        _parcela('En UF', precio=2800, moneda='UF')
        self.assertNotIn('En UF', [p.nombre for p in
                                   self.client.get('/catalogo/parcelas-baratas/').context['page_obj']])


@sin_manifiesto
class ElSitemap(Base):

    def test_publica_las_caracteristicas_con_contenido(self):
        sm = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('/catalogo/parcela-vista-al-lago/</loc>', sm)

    def test_NO_publica_una_caracteristica_vacia(self):
        """Mismo error que tenia /reserva/: una URL muerta en el sitemap."""
        Parcela.objects.filter(vista_lago=True).delete()
        sm = self.client.get('/sitemap.xml').content.decode()
        self.assertNotIn('/catalogo/parcela-vista-al-lago/</loc>', sm)

    def test_NO_publica_las_que_no_se_publican(self):
        sm = self.client.get('/sitemap.xml').content.decode()
        for slug in car.NO_PUBLICADAS:
            self.assertNotIn(f'/catalogo/{slug}/</loc>', sm)


@sin_manifiesto
class LaPlayaNoPrometeLoQueNoHay(Base):
    """Leonardo: "parcelas en la playa NO TENGO, pero hay algunas cerca".

    El slug es el que pide Jorge, pero el H1 y el texto no pueden decir que la
    parcela esta en la playa.
    """

    def test_el_h1_dice_cerca_y_no_en_la_playa(self):
        h1 = self.client.get('/catalogo/parcela-en-la-playa/').context['seo_h1']
        self.assertIn('cerca', h1.lower())
        self.assertNotIn('en la playa', h1.lower())

    def test_la_bajada_lo_dice_explicito(self):
        bajada = self.client.get('/catalogo/parcela-en-la-playa/').context['bajada_caracteristica']
        self.assertIn('no vendemos', bajada.lower())


@sin_manifiesto
class ElPanelGuardaLasCasillas(Base):
    """Probar el camino de LEONARDO, no el del servidor.

    El formulario del panel lista sus campos a mano y la plantilla los dibuja
    uno por uno: un campo nuevo no aparece solo, y si falta en `fields` la
    casilla se dibuja igual, el la marca, aprieta Guardar y no se guarda nada
    -- sin un solo error en pantalla. Paso tres veces en el panel de Medina.
    """

    def setUp(self):
        from django.contrib.auth.models import User
        User.objects.create_user('leo', password='clave-de-prueba-123', is_staff=True)
        self.client.login(username='leo', password='clave-de-prueba-123')

    def test_la_casilla_viaja_desde_el_formulario(self):
        from panel.forms import ParcelaForm
        for campo in car.CAMPOS_MARCADOS:
            with self.subTest(campo=campo):
                self.assertIn(campo, ParcelaForm().fields)

    def test_la_casilla_se_DIBUJA_en_la_pantalla(self):
        p = Parcela.objects.get(nombre='Vive Rupanco')
        html = self.client.get(f'/admin-panel/parcelas/{p.pk}/editar/').content.decode('utf8', 'replace')
        for campo in car.CAMPOS_MARCADOS:
            with self.subTest(campo=campo):
                self.assertIn(f'name="{campo}"', html)


class NingunComentarioDeDjangoSeImprime(TestCase):
    """El {# #} de Django NO es multilinea: lo que sigue al primer salto SE
    IMPRIME en la pagina.

    Va la decima vez en estos repos, y la del 02-10 la escribi yo -- dentro del
    comentario que avisaba de este mismo bug. Las mediciones de desborde daban
    "0 desbordes, 0 errores" con el texto publicado en pantalla: solo se vio
    MIRANDO la captura. Esta prueba lo caza sin mirar.
    """

    def test_ninguna_plantilla_abre_un_comentario_que_no_cierra_en_su_linea(self):
        import pathlib
        malas = []
        for f in pathlib.Path('core/templates').rglob('*.html'):
            for n, linea in enumerate(f.read_text(encoding='utf-8').splitlines(), 1):
                if '{#' in linea and '#}' not in linea.split('{#', 1)[1]:
                    malas.append(f'{f}:{n}')
        self.assertEqual(malas, [], f'Comentarios {{# #}} sin cerrar en su linea '
                                    f'(usar {{% comment %}}): {malas}')
