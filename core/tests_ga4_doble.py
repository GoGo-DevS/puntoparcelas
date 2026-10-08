"""08-10-2026: el GA4 del panel es de Leonardo y el CRM no lo puede leer.
Se suma el de GoGoDevS por variable de entorno, AL LADO, sin pisar el suyo."""
from django.test import TestCase, override_settings

from core.models import SiteConfig


class Ga4DobleTests(TestCase):
    def _html(self):
        return self.client.get('/').content.decode()

    def _cfg(self, ga4):
        cfg = SiteConfig.get()
        cfg.ga4_id = ga4
        cfg.save()

    @override_settings(GA4_GOGODEVS_ID='')
    def test_solo_el_de_leonardo_queda_igual_que_antes(self):
        self._cfg('G-LEO11111')
        html = self._html()
        self.assertEqual(html.count('googletagmanager.com/gtag/js'), 1)
        self.assertIn("gtag('config', 'G-LEO11111')", html)

    @override_settings(GA4_GOGODEVS_ID='G-GOGO2222')
    def test_los_dos_codigos_con_un_solo_script(self):
        self._cfg('G-LEO11111')
        html = self._html()
        self.assertEqual(html.count('googletagmanager.com/gtag/js'), 1)
        self.assertIn("gtag('config', 'G-LEO11111')", html)
        self.assertIn("gtag('config', 'G-GOGO2222')", html)

    @override_settings(GA4_GOGODEVS_ID='G-GOGO2222')
    def test_sin_el_de_leonardo_igual_mide_el_nuestro(self):
        self._cfg('')
        html = self._html()
        self.assertIn("gtag('config', 'G-GOGO2222')", html)

    @override_settings(GA4_GOGODEVS_ID='G-LEO11111')
    def test_el_mismo_codigo_no_se_configura_dos_veces(self):
        self._cfg('G-LEO11111')
        self.assertEqual(self._html().count("gtag('config', 'G-LEO11111')"), 1)

    @override_settings(GA4_GOGODEVS_ID='G-GOGO2222')
    def test_el_tree_tambien_mide_con_el_nuestro(self):
        self._cfg('')
        html = self.client.get('/links/').content.decode()
        self.assertIn("gtag('config', 'G-GOGO2222')", html)
        self.assertIn('tree_click', html)
