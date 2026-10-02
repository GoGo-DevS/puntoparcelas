# -*- coding: utf-8 -*-
"""Precarga las 4 caracteristicas que Leonardo dicto el 01-10-2026.

Las otras seis se calculan solas y no pasan por aca (ver core/caracteristicas.py).

ENSAYO POR DEFECTO. Escribe solo con --confirmar.

Es idempotente: marca la casilla y no la desmarca nunca. Si Leonardo despues
destilda una desde su panel, correr esto de nuevo NO se la vuelve a prender --
el panel manda sobre esta lista, que es una foto de lo que dijo un dia.

Los nombres que no calzan con ninguna parcela publicada se INFORMAN, no se
inventan: tres de las que nombro ("Hacienda don Danilo", "Jardines de Litueche",
"Fundo la Puntilla") no estan entre las publicadas, y eso es justamente lo que
Leonardo tiene que saber -- cree que las tiene en la web y no estan.
"""
from django.core.management.base import BaseCommand
from core.models import Parcela

# Textual de Leonardo en el grupo "Punto Parcelas SEO", 01-10-2026 18:09.
DICHO_POR_LEONARDO = {
    'cerca_playa': [
        'Vive Santo Domingo', 'Hacienda Don Felix', 'Parque Algarrobo',
        'Fundo la Quirigua', 'Hacienda Vichuquén', 'Valle los Cruceros',
        'Alto Pichilemu', 'Lomas de Puertecillo', 'Brisas de Vichuquén',
        'Matanzas', 'Fundo Santa Rosa de Bucalemu', 'Brisas del Arrayán',
        'Proyecto Arbol Grande', 'Almar', 'Costa Contao',
    ],
    'vista_mar': ['Vive Ovalle', 'Costa Contao', 'Parque Algarrobo'],
    'vista_lago': ['Vive Rupanco', 'Hacienda Vichuquén', 'Fundo la Quirigua',
                   'Vive Puerto Varas'],
    'credito_directo': [
        'Hacienda Don Danilo', 'Parque Algarrobo', 'Lomas de Constitución',
        'Proyecto Don Guillermo', 'Hacienda Vichuquén', 'Fundo la Quirigua',
        'Jardines de Litueche', 'Vive Longaví', 'Praderas de Cauquenes',
        'Fundo la Puntilla',
    ],
}


class Command(BaseCommand):
    help = 'Marca las 4 caracteristicas SEO con lo que dicto Leonardo. Ensayo por defecto.'

    def add_arguments(self, parser):
        parser.add_argument('--confirmar', action='store_true')

    def handle(self, *a, **o):
        confirmar = o['confirmar']
        publicadas = list(Parcela.objects.exclude(estado='vendida'))
        marcadas, sin_calzar = 0, []

        for campo, nombres in DICHO_POR_LEONARDO.items():
            for buscado in nombres:
                # Coincidencia por substring en los dos sentidos: el catalogo
                # tiene "Parcelas cerca del Mar (Matanzas)" y el dijo
                # "vive matanzas"; ninguno contiene al otro entero.
                clave = buscado.lower()
                calzan = [p for p in publicadas if clave in p.nombre.lower()]
                if not calzan:
                    sin_calzar.append((campo, buscado))
                    continue
                for p in calzan:
                    if getattr(p, campo):
                        continue          # ya estaba: no se toca
                    marcadas += 1
                    self.stdout.write(f'  {campo:16} <- {p.nombre}')
                    if confirmar:
                        setattr(p, campo, True)
                        p.save(update_fields=[campo])

        self.stdout.write(self.style.SUCCESS(
            f'\n{"MARCADAS" if confirmar else "ENSAYO"}: {marcadas} casillas'))

        if sin_calzar:
            # En ERROR y no en WARNING: es la linea que Diego tiene que leerle
            # a Leonardo. Son proyectos que el cree publicados y no lo estan.
            self.stdout.write(self.style.ERROR(
                f'\n{len(sin_calzar)} NO CALZAN con ninguna parcela publicada '
                f'(¿vendidas, o nunca se cargaron?):'))
            for campo, nombre in sin_calzar:
                self.stdout.write(self.style.ERROR(f'  {campo:16} <- "{nombre}"'))

        if not confirmar:
            self.stdout.write('\nRepetir con --confirmar para escribir.')
