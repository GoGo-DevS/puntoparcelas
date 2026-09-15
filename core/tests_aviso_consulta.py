"""El aviso de una consulta nueva tiene que llegarle a Leonardo, o decir por que no.

Reunion del 15-09-2026: Leonardo veia las consultas SOLO entrando al panel.
Causa: sin las variables de SMTP en Render, Django usa el backend de consola y
el correo se "envia" al log. Encima iba con `fail_silently=True`, asi que ni el
cliente ni nosotros nos enterabamos. Estas pruebas cuidan las dos ramas.
"""
from django.core import mail
from django.test import TestCase, override_settings

from core.models import Consulta
from core.views import _enviar_notificacion


def _consulta(email='interesado@ejemplo.cl'):
    return Consulta.objects.create(nombre='Juan Pérez', telefono='+56911111111',
                                   email=email, mensaje='Quiero la parcela 5')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   EMAIL_HOST_USER='no-responder@gogodevs.cl',
                   EMAIL_DESTINO='leo@ejemplo.cl')
class ConSmtpTests(TestCase):

    def test_avisa_y_se_puede_responder_al_interesado(self):
        self.assertTrue(_enviar_notificacion(_consulta()))
        self.assertEqual(len(mail.outbox), 1)
        aviso = mail.outbox[0]
        self.assertEqual(aviso.to, ['leo@ejemplo.cl'])
        self.assertIn('Juan Pérez', aviso.subject)
        # Responder el aviso le contesta al interesado, no a la casilla de envio.
        self.assertEqual(aviso.reply_to, ['interesado@ejemplo.cl'])

    def test_sin_correo_del_interesado_no_pone_reply_to(self):
        self.assertTrue(_enviar_notificacion(_consulta(email='')))
        self.assertFalse(mail.outbox[0].reply_to)

    @override_settings(EMAIL_DESTINO='leo@ejemplo.cl, diego@gogodevs.cl')
    def test_acepta_varios_destinatarios(self):
        _enviar_notificacion(_consulta())
        self.assertEqual(mail.outbox[0].to, ['leo@ejemplo.cl', 'diego@gogodevs.cl'])


@override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend',
                   EMAIL_HOST_USER='')
class SinSmtpTests(TestCase):

    def test_sin_smtp_no_finge_haber_avisado_y_lo_deja_en_el_log(self):
        with self.assertLogs('core.views', level='ERROR') as registro:
            self.assertFalse(_enviar_notificacion(_consulta()))
        self.assertIn('SIN AVISO POR CORREO', registro.output[0])
        self.assertEqual(len(mail.outbox), 0)
