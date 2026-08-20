"""Saca las fotos de la cuenta Cloudinary CAIDA y las deja en R2, achicadas.

20-08-2026. La cuenta `dd1ps0y8f` quedo deshabilitada por pasarse del cupo
gratis y el sitio de Leonardo, en produccion y con dominio propio, quedo sin
UNA sola foto. Medido en vivo:

    HTTP 401 · X-Cld-Error: cloud_name dd1ps0y8f is disabled

La ENTREGA esta bloqueada, pero la Admin API usa otra ruta y otra autenticacion
(api_key/api_secret en vez de acceso publico). Este comando lo comprueba antes
de tocar nada y lo dice derecho si tampoco funciona: sin eso, la unica salida
seria que Leonardo vuelva a subir todo a mano.

    python manage.py rescatar_cloudinary                # ensayo, no escribe
    python manage.py rescatar_cloudinary --confirmar
    python manage.py rescatar_cloudinary --confirmar --ancho 1600

POR QUE SE ACHICAN AL MIGRAR Y NO AL ENTREGAR
Cloudinary permitia achicar en la URL (f_auto,q_auto,w_1200), y eso fue el
parche del 17-08. R2 no transforma nada: sirve el archivo tal cual. Si se
migraran las fotos originales sin tocar, el sitio volveria a mandar 29,6 MB por
visita — que es exactamente lo que reviento la cuenta. R2 no cobra egreso, asi
que no costaria plata, pero se lo comeria el celular de quien entra. Se achican
UNA vez, aca.

ES IDEMPOTENTE: lo ya migrado (URL que no es de Cloudinary) se salta. Se puede
correr de nuevo si se corta a la mitad.
"""
import io
import os
import urllib.error
import urllib.parse
import urllib.request

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from core.models import FotoParcela, Parcela

ADMIN = 'https://api.cloudinary.com/v1_1/{cloud}/resources/image'


def _credenciales():
    """(cloud, key, secret) desde CLOUDINARY_URL: cloudinary://key:secret@cloud"""
    url = os.environ.get('CLOUDINARY_URL', '')
    if not url.startswith('cloudinary://'):
        return None
    p = urllib.parse.urlparse(url)
    if not (p.username and p.password and p.hostname):
        return None
    return p.hostname, p.username, p.password


def _pedir(url, key, secret):
    req = urllib.request.Request(url)
    import base64
    cred = base64.b64encode(f'{key}:{secret}'.encode()).decode()
    req.add_header('Authorization', f'Basic {cred}')
    return urllib.request.urlopen(req, timeout=60)


def _achicar(datos, ancho):
    """Devuelve (bytes, extension). Sin Pillow devuelve el original tal cual."""
    try:
        from PIL import Image
    except ImportError:
        return datos, None
    try:
        im = Image.open(io.BytesIO(datos))
        im.load()
    except Exception:
        return datos, None
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGB')
    if im.width > ancho:
        alto = round(im.height * ancho / im.width)
        im = im.resize((ancho, alto), Image.LANCZOS)
    salida = io.BytesIO()
    im.save(salida, format='JPEG', quality=82, optimize=True, progressive=True)
    return salida.getvalue(), '.jpg'


class Command(BaseCommand):
    help = 'Baja las fotos de la cuenta Cloudinary caida, las achica y las sube al storage actual (R2).'

    def add_arguments(self, parser):
        parser.add_argument('--confirmar', action='store_true',
                            help='Sin esto es un ensayo y no escribe nada.')
        parser.add_argument('--ancho', type=int, default=1600,
                            help='Ancho maximo en pixeles (default 1600).')
        # PRIMERO SE RESCATA, DESPUES SE MIGRA. Bajar los archivos a disco es lo
        # unico irreversible que hay que apurar: la cuenta esta caida y no hay
        # respaldo en ninguna parte. Subir a R2 puede esperar a que exista el
        # bucket. Y hacerlo en un solo paso seria PELIGROSO: sin R2 configurado
        # el storage por defecto es el disco local, asi que reescribir la base
        # dejaria a produccion apuntando a archivos que en Render no existen.
        parser.add_argument('--solo-descargar', metavar='CARPETA',
                            help='Baja los originales a esa carpeta y NO toca la base de datos.')

    def handle(self, *args, **op):
        for s in (self.stdout, self.stderr):
            try:
                s._out.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass

        escribir, ancho = op['confirmar'], op['ancho']
        carpeta = op.get('solo_descargar')
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
            self.stdout.write(self.style.WARNING(
                f'MODO RESCATE: bajo los originales a {carpeta} y NO toco la base.\n'))
        elif not escribir:
            self.stdout.write(self.style.WARNING('ENSAYO — no se escribe nada. Usa --confirmar.\n'))

        cred = _credenciales()
        if not cred:
            self.stderr.write(self.style.ERROR(
                'Falta CLOUDINARY_URL (formato cloudinary://api_key:api_secret@cloud_name).\n'
                'Sale de Render -> servicio puntoparcelas -> Environment, o del panel de\n'
                'Cloudinary. Sin eso no hay como sacar las fotos de la cuenta caida.'))
            return
        cloud, key, secret = cred

        # PRIMERO: comprobar que la Admin API responde. Si tambien esta cerrada,
        # decirlo ahora y no despues de fallar 200 veces seguidas.
        self.stdout.write(f'Probando la Admin API de "{cloud}"...')
        try:
            _pedir(ADMIN.format(cloud=cloud) + '?max_results=1', key, secret).read()
        except urllib.error.HTTPError as e:
            self.stderr.write(self.style.ERROR(
                f'La Admin API respondio {e.code}. La cuenta no deja sacar los archivos.\n'
                f'Detalle: {e.read()[:200].decode(errors="replace")}\n'
                f'Camino alternativo: entrar al panel de Cloudinary, Media Library, y\n'
                f'descargar la carpeta media/parcelas a mano; o pedirle las fotos a\n'
                f'Leonardo, que las tiene.'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'No pude conectar: {e}'))
            return
        self.stdout.write(self.style.SUCCESS('  Admin API OK: se pueden recuperar.\n'))

        campos = [(FotoParcela, 'imagen'), (Parcela, 'imagen_principal'),
                  (Parcela, 'imagen_credito')]
        ok = saltados = fallidos = 0
        bytes_antes = bytes_despues = 0

        for modelo, campo in campos:
            if not hasattr(modelo, campo):
                continue
            for obj in modelo.objects.exclude(**{campo: ''}).exclude(**{f'{campo}__isnull': True}):
                f = getattr(obj, campo)
                try:
                    url = f.url
                except Exception:
                    continue
                if 'res.cloudinary.com' not in url:
                    saltados += 1
                    continue

                nombre = os.path.basename(f.name)
                if not escribir and not carpeta:
                    self.stdout.write(f'  {modelo.__name__}#{obj.pk}.{campo}  {nombre[:44]}')
                    ok += 1
                    continue

                # La entrega publica esta bloqueada (401); el archivo se baja por
                # la ruta autenticada de la Admin API.
                directo = url.split('/upload/')[-1]
                origen = (f'https://api.cloudinary.com/v1_1/{cloud}/resources/image/'
                          f'upload/{urllib.parse.quote(directo.split("/", 1)[-1].rsplit(".", 1)[0])}')
                try:
                    meta = _pedir(origen, key, secret).read()
                    import json
                    secure = json.loads(meta).get('secure_url') or url
                    datos = urllib.request.urlopen(secure, timeout=90).read()
                except Exception as e:
                    self.stderr.write(self.style.WARNING(
                        f'  ! {modelo.__name__}#{obj.pk}.{campo}: {str(e)[:70]}'))
                    fallidos += 1
                    continue

                bytes_antes += len(datos)

                if carpeta:
                    # Rescate puro: el original tal cual, sin achicar ni tocar la
                    # base. El nombre lleva el pk para poder reconstruir despues
                    # que archivo era de quien.
                    destino = os.path.join(
                        carpeta, f'{modelo.__name__}-{obj.pk}-{campo}-{nombre}')
                    with open(destino, 'wb') as fh:
                        fh.write(datos)
                    bytes_despues += len(datos)
                    ok += 1
                    self.stdout.write(f'  v {modelo.__name__}#{obj.pk}.{campo}  '
                                      f'{len(datos)/1024:.0f} KB  {nombre[:38]}')
                    continue

                chico, ext = _achicar(datos, ancho)
                bytes_despues += len(chico)
                base = nombre.rsplit('.', 1)[0]
                destino = f'parcelas/{base}{ext or os.path.splitext(nombre)[1] or ".jpg"}'
                ruta = default_storage.save(destino, ContentFile(chico))
                setattr(obj, campo, ruta)
                obj.save(update_fields=[campo])
                ok += 1
                self.stdout.write(f'  + {modelo.__name__}#{obj.pk}.{campo}  '
                                  f'{len(datos)/1024:.0f} KB -> {len(chico)/1024:.0f} KB')

        self.stdout.write(self.style.SUCCESS(
            f'\n{ok} recuperadas · {saltados} ya estaban fuera de Cloudinary · {fallidos} fallidas'
            + ('' if escribir else '   (ENSAYO)')))
        if bytes_antes:
            self.stdout.write(
                f'Peso: {bytes_antes/1048576:.1f} MB -> {bytes_despues/1048576:.1f} MB '
                f'({100 - bytes_despues * 100 / bytes_antes:.1f}% menos)')
        if fallidos:
            self.stderr.write(self.style.WARNING(
                'Las fallidas hay que bajarlas a mano del panel de Cloudinary, o pedirselas '
                'a Leonardo. NO se borro nada: sus registros siguen apuntando a Cloudinary.'))
