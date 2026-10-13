# -*- coding: utf-8 -*-
"""Fotos de parcela en WebP de menos de 100 KB (punto 8 de Jorge, 05-10-2026).

POR QUE
Medido en vivo el 13-10: cada foto de una ficha pesaba entre 1,3 y 2 MB, y
las 13 miniaturas de 80 px de la galeria bajaban el original completo. El
filtro `achicar` achicaba al vuelo, pero solo sabe hacerlo con Cloudinary: desde
que las fotos se mudaron a R2 (20-08) devuelve la URL tal cual y no achica nada.
R2 no transforma imagenes, asi que el archivo guardado tiene que venir chico.

QUE HACE
Lado mayor a 1600 px como mucho, y lo achica hasta entrar en 100 KB (la foto
grande de la ficha se ve a ~700 px de ancho). Bajo 640 px deja de achicar y
cede calidad. Nunca agranda.
"""
import io

from PIL import Image, ImageOps

LIMITE = 100 * 1024
LADO_MAXIMO = 1600
LADO_MINIMO = 640
CALIDAD = 60
CALIDAD_MINIMA = 30


def a_webp(origen, limite=LIMITE):
    """Bytes WebP de la imagen `origen` (bytes o archivo abierto), bajo `limite`.

    Respeta la orientacion EXIF: las fotos de celular vienen giradas "de
    palabra" y sin esto quedarian de lado. Devuelve la mejor version
    conseguida aunque no entre en el limite (una foto un poco mas pesada es
    mejor que ninguna foto).
    """
    datos = origen if isinstance(origen, (bytes, bytearray)) else origen.read()
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(datos)))
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')

    # Una foto de campo de 3000x4000 no entra en 100 KB a 1600 px sin
    # destrozarla. En vez de probar decenas de combinaciones (20 s por foto
    # en la primera version: subir 10 desde el panel cortaba la conexion), se
    # ESTIMA el lado que entra: el peso crece con la cantidad de pixeles, asi
    # que el lado se corrige por la raiz de lo que sobra. Entra en 2 o 3 vueltas.
    lado = min(LADO_MAXIMO, max(img.size))
    calidad = CALIDAD
    mejor = None
    for _ in range(8):
        copia = img.copy()
        copia.thumbnail((lado, lado), Image.LANCZOS)  # nunca agranda
        buf = io.BytesIO()
        copia.save(buf, 'WEBP', quality=calidad, method=4)
        salida = buf.getvalue()
        if mejor is None or len(salida) < len(mejor):
            mejor = salida
        if len(salida) <= limite:
            return salida
        if lado <= LADO_MINIMO and calidad <= CALIDAD_MINIMA:
            break
        nuevo = int(lado * (limite / len(salida)) ** 0.5 * 0.95)
        if nuevo < LADO_MINIMO:
            # Bajo 640 px la foto ya no sirve en la ficha: se cede calidad.
            nuevo = LADO_MINIMO
            calidad = max(CALIDAD_MINIMA, calidad - 10)
        lado = nuevo
    return mejor


def nombre_webp(nombre):
    """'parcelas/290142.jpg' -> '290142.webp' (el upload_to pone la carpeta)."""
    base = nombre.rsplit('/', 1)[-1]
    return (base.rsplit('.', 1)[0] if '.' in base else base) + '.webp'


# ---------------------------------------------------------------------------
# La miniatura al compartir el link (og:image)
#
# 13-10-2026, probado por Diego en iPhone y Android: WhatsApp NO muestra la
# miniatura cuando og:image es WebP. Ese link es la publicidad de Leonardo:
# lo comparte por WhatsApp, Instagram y Facebook. La foto de la ficha se queda
# en WebP (pesa la mitad) y la miniatura se arma aparte, en JPEG, al tamaño que
# piden WhatsApp y Facebook: 1200x630, recortada al centro, bajo 300 KB.
# ---------------------------------------------------------------------------
COMPARTIR = (1200, 630)
LIMITE_COMPARTIR = 300 * 1024


def a_jpeg_compartir(origen):
    """Bytes JPEG de 1200x630 para og:image, recortado al centro y bajo 300 KB."""
    datos = origen if isinstance(origen, (bytes, bytearray)) else origen.read()
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(datos))).convert('RGB')
    img = ImageOps.fit(img, COMPARTIR, Image.LANCZOS, centering=(0.5, 0.5))
    for calidad in (85, 75, 65, 55):
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=calidad, optimize=True, progressive=True)
        if buf.tell() <= LIMITE_COMPARTIR:
            break
    return buf.getvalue()
