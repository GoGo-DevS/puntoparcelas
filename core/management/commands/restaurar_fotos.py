r"""Vuelve a enganchar las fotos desde una carpeta, sin que el cliente rehaga nada.

20-08-2026. La cuenta de Cloudinary quedo deshabilitada y ni la entrega ni la
Admin API dejan sacar los archivos ("disabled customer"). Los 324 archivos no
estan en ninguna maquina nuestra: los subio LEONARDO desde su panel, uno por
uno, parcela por parcela.

Pedirle que rehaga eso seria pedirle un dia de trabajo por un problema nuestro.

LO QUE SALVA LA SITUACION: la base de datos NO se perdio. Sigue sabiendo
exactamente que archivo va en que parcela y en que orden, y el nombre ORIGINAL
esta dentro del public_id de Cloudinary:

    media/parcelas/IMG-20240221-WA01363_sdruo2
                   \________________/ \____/
                    lo que mando Leo   sufijo que le puso Cloudinary

Asi que basta con volver a TENER los archivos —da lo mismo de donde: del chat de
WhatsApp, de su computador, de su telefono— y este comando los reengancha solo,
comparando por nombre. Para Leonardo son cinco minutos: mandar la carpeta.

    python manage.py restaurar_fotos ~/fotos-de-leo              # ensayo
    python manage.py restaurar_fotos ~/fotos-de-leo --confirmar
    python manage.py restaurar_fotos ~/fotos-de-leo --faltantes  # que falta

Corre contra el storage que este configurado (R2 en produccion). Achica a 1600 px
al subir, porque R2 sirve el archivo tal cual y las originales pesaban 3 MB cada
una — 29,6 MB por visita fue justo lo que reviento la cuenta de Cloudinary.

ES IDEMPOTENTE: lo que ya quedo fuera de Cloudinary se salta.
"""
import io
import os
import re
import unicodedata

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from core.models import FotoParcela, Parcela

# Sufijo aleatorio que Cloudinary agrega al public_id: "_sdruo2", "_kfhble".
SUFIJO_CLOUDINARY = re.compile(r'_[a-z0-9]{6}$')

CAMPOS = [(FotoParcela, 'imagen'), (Parcela, 'imagen_principal'),
          (Parcela, 'imagen_credito')]


def clave(nombre):
    """Nombre comparable: sin carpeta, sin extension, sin tildes, en minuscula.

    WhatsApp, Windows y el navegador renombran distinto el mismo archivo
    ("IMG-20240221-WA01363.jpg", "IMG-20240221-WA01363 (1).jpeg"), asi que se
    compara por lo unico que se mantiene.
    """
    base = os.path.basename(str(nombre or ''))
    base = base.rsplit('.', 1)[0]
    base = re.sub(r'\s*\(\d+\)$', '', base)          # "foo (1)" -> "foo"
    base = SUFIJO_CLOUDINARY.sub('', base)
    base = unicodedata.normalize('NFKD', base)
    base = ''.join(c for c in base if not unicodedata.combining(c))
    return base.lower().strip()


def achicar(datos, ancho=1600):
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
        im = im.resize((ancho, round(im.height * ancho / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, format='JPEG', quality=82, optimize=True, progressive=True)
    return out.getvalue(), '.jpg'


class Command(BaseCommand):
    help = 'Reengancha las fotos desde una carpeta, comparando por nombre original.'

    def add_arguments(self, parser):
        parser.add_argument('carpeta', help='Carpeta con las fotos (se busca recursivo).')
        parser.add_argument('--confirmar', action='store_true',
                            help='Sin esto es un ensayo y no escribe nada.')
        parser.add_argument('--faltantes', action='store_true',
                            help='Solo lista lo que la carpeta NO trae, por parcela.')
        parser.add_argument('--ancho', type=int, default=1600)

    def handle(self, *a, **op):
        for s in (self.stdout, self.stderr):
            try:
                s._out.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass

        carpeta, escribir = op['carpeta'], op['confirmar']
        if not os.path.isdir(carpeta):
            self.stderr.write(self.style.ERROR(f'No existe la carpeta {carpeta}'))
            return

        # Indice de lo que trae la carpeta. Si hay dos archivos con el mismo
        # nombre en subcarpetas distintas gana el mas pesado: la version chica
        # suele ser una miniatura o una copia de WhatsApp ya comprimida.
        disponibles = {}
        for raiz, _, archivos in os.walk(carpeta):
            for nombre in archivos:
                if not nombre.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic')):
                    continue
                ruta = os.path.join(raiz, nombre)
                k = clave(nombre)
                if k not in disponibles or os.path.getsize(ruta) > os.path.getsize(disponibles[k]):
                    disponibles[k] = ruta
        self.stdout.write(f'La carpeta trae {len(disponibles)} archivos distintos.\n')

        pendientes, faltan, listos = [], [], 0
        for modelo, campo in CAMPOS:
            if not hasattr(modelo, campo):
                continue
            qs = modelo.objects.exclude(**{campo: ''}).exclude(**{f'{campo}__isnull': True})
            for obj in qs.order_by('pk'):
                actual = str(getattr(obj, campo) or '')
                if not actual:
                    continue
                try:
                    url = getattr(obj, campo).url
                except Exception:
                    url = ''
                if url and 'res.cloudinary.com' not in url:
                    listos += 1          # ya migrado
                    continue
                k = clave(actual)
                (pendientes if k in disponibles else faltan).append((modelo, campo, obj, k, actual))

        if op['faltantes'] or not escribir:
            self.stdout.write(self.style.SUCCESS(
                f'{len(pendientes)} se pueden reenganchar · {len(faltan)} faltan en la carpeta · '
                f'{listos} ya estaban fuera de Cloudinary\n'))

        if faltan:
            self.stdout.write(self.style.WARNING('FALTAN (pedirselas al cliente):'))
            por_parcela = {}
            for modelo, campo, obj, k, actual in faltan:
                p = getattr(obj, 'parcela', None) or obj
                por_parcela.setdefault(str(p)[:44], []).append(clave(actual))
            for parcela, nombres in sorted(por_parcela.items()):
                self.stdout.write(f'  {parcela}  ({len(nombres)})')
                for n in nombres[:4]:
                    self.stdout.write(f'      {n}')
                if len(nombres) > 4:
                    self.stdout.write(f'      ... y {len(nombres)-4} mas')
        if op['faltantes']:
            return
        if not escribir:
            self.stdout.write('\nENSAYO — nada se escribio. Agrega --confirmar.')
            return

        ok = 0
        antes = despues = 0
        for modelo, campo, obj, k, actual in pendientes:
            with open(disponibles[k], 'rb') as fh:
                datos = fh.read()
            antes += len(datos)
            chico, ext = achicar(datos, op['ancho'])
            despues += len(chico)
            destino = f'parcelas/{k}{ext or ".jpg"}'
            ruta = default_storage.save(destino, ContentFile(chico))
            setattr(obj, campo, ruta)
            obj.save(update_fields=[campo])
            ok += 1
            self.stdout.write(f'  + {modelo.__name__}#{obj.pk}.{campo}  {k[:40]:42} '
                              f'{len(datos)/1024:.0f} KB -> {len(chico)/1024:.0f} KB')

        self.stdout.write(self.style.SUCCESS(f'\n{ok} fotos reenganchadas · {len(faltan)} siguen faltando'))
        if antes:
            self.stdout.write(f'Peso: {antes/1048576:.1f} MB -> {despues/1048576:.1f} MB '
                              f'({100 - despues*100/antes:.1f}% menos)')
