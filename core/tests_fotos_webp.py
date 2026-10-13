# -*- coding: utf-8 -*-
"""Fotos en WebP bajo 100 KB (punto 8 de Jorge): al subirlas y las que ya estaban."""
import io
import os
import random
import shutil
import tempfile
from io import StringIO

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image

from . import imagenes
from .models import FotoParcela, Parcela


def _foto(ancho=3000, alto=4000, formato='JPEG', exif_orientacion=None):
    """Una foto 'dificil': ruido, que comprime mal, como el pasto de las fotos reales."""
    random.seed(7)
    img = Image.effect_noise((ancho // 4, alto // 4), 90).convert('RGB').resize((ancho, alto))
    buf = io.BytesIO()
    if exif_orientacion:
        exif = Image.Exif()
        exif[0x0112] = exif_orientacion
        img.save(buf, formato, quality=95, exif=exif)
    else:
        img.save(buf, formato, quality=95)
    return buf.getvalue()


class Conversion(SimpleTestCase):

    def test_una_foto_de_celular_queda_bajo_100_kb_en_webp(self):
        salida = imagenes.a_webp(_foto())
        self.assertLessEqual(len(salida), imagenes.LIMITE)
        self.assertEqual(Image.open(io.BytesIO(salida)).format, 'WEBP')

    def test_no_baja_de_640_px_aunque_no_entre(self):
        salida = imagenes.a_webp(_foto(), limite=5 * 1024)  # limite imposible
        self.assertGreaterEqual(max(Image.open(io.BytesIO(salida)).size), 640)

    def test_nunca_agranda_una_foto_chica(self):
        salida = imagenes.a_webp(_foto(400, 300))
        self.assertEqual(Image.open(io.BytesIO(salida)).size, (400, 300))

    def test_respeta_la_orientacion_del_celular(self):
        # Orientacion 6 = la camara la guardo acostada: en pantalla va parada.
        salida = imagenes.a_webp(_foto(1200, 900, exif_orientacion=6))
        ancho, alto = Image.open(io.BytesIO(salida)).size
        self.assertGreater(alto, ancho)

    def test_nombre(self):
        self.assertEqual(imagenes.nombre_webp('parcelas/290142.jpg'), '290142.webp')
        self.assertEqual(imagenes.nombre_webp('parcelas/a.b.JPEG'), 'a.b.webp')


class _ConMedia(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp(prefix='pp-fotos-')
        self.respaldo = tempfile.mkdtemp(prefix='pp-respaldo-')
        self.ajuste = override_settings(MEDIA_ROOT=self.media, STORAGES={
            'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
            'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
        })
        self.ajuste.enable()
        self.parcela = Parcela.objects.create(nombre='Rauco', region='maule', precio=1,
                                              superficie=5000, estado='disponible')

    def tearDown(self):
        self.ajuste.disable()
        shutil.rmtree(self.media, ignore_errors=True)
        shutil.rmtree(self.respaldo, ignore_errors=True)


class AlSubir(_ConMedia):

    def test_la_foto_subida_se_guarda_en_webp_chica(self):
        f = FotoParcela.objects.create(parcela=self.parcela,
                                       imagen=SimpleUploadedFile('IMG_001.jpg', _foto(), 'image/jpeg'))
        self.assertTrue(f.imagen.name.endswith('.webp'), f.imagen.name)
        self.assertLessEqual(f.imagen.size, imagenes.LIMITE)

    def test_cambiar_la_principal_no_vuelve_a_convertir(self):
        f = FotoParcela.objects.create(parcela=self.parcela,
                                       imagen=SimpleUploadedFile('a.jpg', _foto(800, 600), 'image/jpeg'))
        nombre = f.imagen.name
        f.principal = True
        f.save()
        self.assertEqual(f.imagen.name, nombre)

    def test_un_archivo_que_no_es_imagen_se_guarda_igual(self):
        # Mejor una foto pesada que perder lo que subio Leonardo.
        f = FotoParcela(parcela=self.parcela)
        f.imagen = SimpleUploadedFile('raro.jpg', b'no soy una imagen', 'image/jpeg')
        f.save()
        self.assertTrue(f.imagen.name.endswith('.jpg'))
        self.assertEqual(f.imagen.read(), b'no soy una imagen')


class ComandoOptimizarFotos(_ConMedia):

    def setUp(self):
        super().setUp()
        # Fotos "viejas": se escriben directo al storage, sin pasar por save().
        self.original = _foto()
        nombre = default_storage.save('parcelas/290142.jpg', io.BytesIO(self.original))
        self.foto = FotoParcela.objects.create(parcela=self.parcela, imagen='placeholder')
        FotoParcela.objects.filter(pk=self.foto.pk).update(imagen=nombre)
        self.nombre_viejo = nombre

    def _correr(self, *args):
        out = StringIO()
        call_command('optimizar_fotos', *args, stdout=out)
        return out.getvalue()

    def test_el_ensayo_no_escribe_nada(self):
        salida = self._correr()
        self.assertIn('ENSAYO', salida)
        self.foto.refresh_from_db()
        self.assertEqual(self.foto.imagen.name, self.nombre_viejo)
        self.assertEqual(os.listdir(self.respaldo), [])

    def test_aplicar_sin_respaldo_se_niega(self):
        with self.assertRaises(CommandError):
            self._correr('--aplicar')

    def test_aplicar_respalda_convierte_y_no_borra_el_original(self):
        self._correr('--aplicar', '--respaldo', self.respaldo)
        # respaldo en disco, byte por byte
        with open(os.path.join(self.respaldo, 'parcelas', '290142.jpg'), 'rb') as f:
            self.assertEqual(f.read(), self.original)
        # la ficha apunta a la WebP, que pesa menos de 100 KB
        self.foto.refresh_from_db()
        self.assertTrue(self.foto.imagen.name.endswith('.webp'))
        self.assertLessEqual(self.foto.imagen.size, imagenes.LIMITE)
        # y el original SIGUE en el bucket
        self.assertTrue(default_storage.exists(self.nombre_viejo))

    def test_correrlo_dos_veces_no_hace_nada_la_segunda(self):
        self._correr('--aplicar', '--respaldo', self.respaldo)
        segunda = self._correr('--aplicar', '--respaldo', self.respaldo)
        self.assertIn('Completadas: 0 de 0', segunda)
        self.assertIn('ya es WebP', segunda)

    def test_el_reporte_dice_que_base_uso(self):
        self.assertIn('Base: sqlite3', self._correr())


class MiniaturaAlCompartir(_ConMedia):
    """13-10: WhatsApp no muestra og:image en WebP (iPhone y Android). Va un JPEG aparte."""

    def setUp(self):
        super().setUp()
        self.foto = FotoParcela.objects.create(
            parcela=self.parcela, principal=True,
            imagen=SimpleUploadedFile('a.jpg', _foto(3000, 4000), 'image/jpeg'))

    def test_la_foto_guardada_es_webp_pero_og_image_no(self):
        self.assertTrue(self.foto.imagen.name.endswith('.webp'))
        html = self.client.get(self.parcela.get_absolute_url()).content.decode('utf8')
        og = html.split('property="og:image"', 1)[1].split('content="', 1)[1].split('"', 1)[0]
        self.assertTrue(og.endswith(f'/catalogo/{self.parcela.slug}/compartir.jpg'), og)
        self.assertTrue(og.startswith('http'), og)  # absoluta: WhatsApp la lee desde afuera

    def test_compartir_jpg_es_jpeg_1200x630_bajo_300_kb(self):
        r = self.client.get(f'/catalogo/{self.parcela.slug}/compartir.jpg')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'image/jpeg')
        img = Image.open(io.BytesIO(r.content))
        self.assertEqual((img.format, img.size), ('JPEG', (1200, 630)))
        self.assertLessEqual(len(r.content), 300 * 1024)

    def test_sin_fotos_no_revienta(self):
        sin = Parcela.objects.create(nombre='Sin fotos', region='maule', precio=1,
                                     superficie=5000, estado='disponible')
        r = self.client.get(f'/catalogo/{sin.slug}/compartir.jpg')
        self.assertEqual(r.status_code, 302)

    def test_slug_inexistente_es_404(self):
        self.assertEqual(self.client.get('/catalogo/no-existe/compartir.jpg').status_code, 404)
