# -*- coding: utf-8 -*-
"""Pasa las fotos de parcela que YA estan arriba a WebP bajo 100 KB (punto 8 de Jorge).

Las fotos nuevas se convierten solas al subirlas (FotoParcela.save). Esto es
para las que ya estaban: medidas el 13-10, pesan entre 1,3 y 2 MB cada una.

ENSAYO POR DEFECTO: lista lo que haria y no escribe nada. Escribe solo con
--aplicar, y --aplicar exige --respaldo.

LO QUE NUNCA HACE (regla 12: ningun archivo de un cliente vive en una sola copia)
  - No borra ni pisa el original en el bucket: la version WebP se sube como
    archivo NUEVO y la ficha pasa a apuntar a ella. Volver atras es devolver
    el nombre viejo en la base.
  - No convierte una foto sin antes haber escrito su original en --respaldo
    y comprobado que el archivo en disco pesa lo mismo que lo que se bajo.

Es idempotente: una foto que ya es .webp se omite, asi que cortarlo a la mitad
y correrlo de nuevo sigue donde quedo.

El reporte separa completadas / omitidas / fallidas con su motivo, y dice
contra que base y que almacenamiento corrio.
"""
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from core.imagenes import LIMITE, a_webp, nombre_webp
from core.models import FotoParcela


class Command(BaseCommand):
    help = 'Convierte las fotos de parcela existentes a WebP bajo 100 KB (ensayo por defecto).'

    def add_arguments(self, parser):
        parser.add_argument('--aplicar', action='store_true',
                            help='Escribe de verdad. Sin esto es un ensayo.')
        parser.add_argument('--respaldo', help='Carpeta donde se guarda cada original ANTES de convertirlo.')
        parser.add_argument('--limite', type=int, default=0, help='Procesar como mucho N fotos.')
        parser.add_argument('--parcela', help='Solo las fotos de esta parcela (slug).')

    def handle(self, *args, **opts):
        aplicar = opts['aplicar']
        respaldo = opts['respaldo']
        if aplicar and not respaldo:
            raise CommandError('--aplicar exige --respaldo: ningun original se toca sin copia en disco.')

        db = connection.settings_dict
        self.stdout.write(f"Base: {db['ENGINE'].rsplit('.', 1)[-1]} {db.get('HOST') or db['NAME']}")
        self.stdout.write(f"Almacenamiento: {default_storage.__class__.__name__}")
        self.stdout.write('MODO: ' + ('APLICAR (escribe)' if aplicar else 'ENSAYO (no escribe nada)'))

        fotos = FotoParcela.objects.select_related('parcela').order_by('parcela__nombre', 'orden', 'pk')
        if opts['parcela']:
            fotos = fotos.filter(parcela__slug=opts['parcela'])

        completadas, omitidas, fallidas = [], [], []
        antes = despues = 0
        pendientes = []
        for foto in fotos:
            if not foto.imagen:
                omitidas.append((foto, 'sin archivo'))
            elif foto.imagen.name.lower().endswith('.webp'):
                omitidas.append((foto, 'ya es WebP'))
            else:
                pendientes.append(foto)
        if opts['limite']:
            pendientes = pendientes[:opts['limite']]

        if not aplicar:
            for foto in pendientes:
                self.stdout.write(f'  convertiria  {foto.parcela.nombre[:40]:40}  {foto.imagen.name}')
            self._resumen(len(pendientes), [], omitidas, [], 0, 0, ensayo=True)
            return

        for foto in pendientes:
            nombre_viejo = foto.imagen.name
            try:
                with default_storage.open(nombre_viejo, 'rb') as f:
                    original = f.read()

                # 1. El original a disco, y comprobado, ANTES de cualquier otra cosa.
                destino = os.path.join(respaldo, *nombre_viejo.split('/'))
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                with open(destino, 'wb') as f:
                    f.write(original)
                if os.path.getsize(destino) != len(original):
                    raise IOError('el respaldo en disco no pesa lo mismo que el original')

                # 2. La version chica, como archivo NUEVO en el bucket.
                webp = a_webp(original)
                carpeta = nombre_viejo.rsplit('/', 1)[0] if '/' in nombre_viejo else ''
                nombre_nuevo = default_storage.save(
                    f'{carpeta}/{nombre_webp(nombre_viejo)}' if carpeta else nombre_webp(nombre_viejo),
                    ContentFile(webp))

                # 3. La ficha apunta a la nueva. update() y no save(): save()
                # volveria a convertir, y no hay archivo nuevo que convertir.
                FotoParcela.objects.filter(pk=foto.pk).update(imagen=nombre_nuevo)

                antes += len(original)
                despues += len(webp)
                completadas.append((foto, nombre_viejo, nombre_nuevo, len(original), len(webp)))
                aviso = '' if len(webp) <= LIMITE else '  (sobre 100 KB)'
                self.stdout.write(f'  OK  {foto.parcela.nombre[:36]:36}  {len(original)//1024:>5} KB -> '
                                  f'{len(webp)//1024:>3} KB  {nombre_nuevo}{aviso}')
            except Exception as e:
                fallidas.append((foto, f'{type(e).__name__}: {e}'))
                self.stdout.write(self.style.ERROR(f'  FALLO  {nombre_viejo}: {e}'))

        self._resumen(len(pendientes), completadas, omitidas, fallidas, antes, despues)

    def _resumen(self, n, completadas, omitidas, fallidas, antes, despues, ensayo=False):
        self.stdout.write('')
        if ensayo:
            self.stdout.write(f'Se convertirian: {n}')
        else:
            self.stdout.write(f'Completadas: {len(completadas)} de {n}')
            sobre = sum(1 for c in completadas if c[4] > LIMITE)
            if completadas:
                self.stdout.write(f'Peso: {antes/1048576:.1f} MB -> {despues/1048576:.1f} MB'
                                  f'  ({sobre} quedaron sobre 100 KB)')
        motivos = {}
        for _f, motivo in omitidas:
            motivos[motivo] = motivos.get(motivo, 0) + 1
        for motivo, cuantas in motivos.items():
            self.stdout.write(f'Omitidas ({motivo}): {cuantas}')
        if fallidas:
            self.stdout.write(self.style.ERROR(f'Fallidas: {len(fallidas)}'))
            for foto, motivo in fallidas:
                self.stdout.write(f'  {foto.pk} {foto.imagen.name}: {motivo}')
