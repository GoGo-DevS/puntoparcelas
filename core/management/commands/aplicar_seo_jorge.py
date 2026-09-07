"""Aplica el título/H1 nuevo y la ciudad a cada parcela, segun la auditoría
SEO de Jorge Urzúa (reunión 04/05-09-2026, hoja "Arquitectura SEO | PUNTO
PARCELAS", pestaña "01 Mapping parcelas" — 42 filas).

POR QUÉ UN JSON BUNDLEADO Y NO EL XLSX
El Excel vive en el Downloads de Diego, no en el repo ni en Render. Se
extrajo una sola vez a JSON (data/seo_arquitectura_jorge.json) para que este
comando corra igual en local y en el Shell de Render sin depender de subir
la planilla ni de instalar openpyxl como dependencia de producción.

CÓMO SE UBICA LA PARCELA
La planilla trae "URL Actual" (ej. https://puntoparcelas.cl/catalogo/
altavista-frutillar/); el slug es el último segmento del path. Se busca por
slug exacto. Una fila que no calza con ningún slug real se reporta y se
salta -- no se inventa ni se crea una parcela nueva.

USO
    python manage.py aplicar_seo_jorge
    python manage.py aplicar_seo_jorge --confirmar
"""
import json
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Parcela

DATA_PATH = Path(__file__).parent / 'data' / 'seo_arquitectura_jorge.json'


def _slug_de_url(url):
    partes = [p for p in urlparse(url).path.split('/') if p]
    return partes[-1] if partes else ''


class Command(BaseCommand):
    help = 'Aplica título/H1 SEO nuevo + ciudad a las parcelas, desde la auditoría de Jorge Urzúa.'

    def add_arguments(self, parser):
        parser.add_argument('--confirmar', action='store_true',
                            help='Escribe los cambios. Sin esto es solo un ensayo.')

    def handle(self, *args, **opts):
        confirmar = opts['confirmar']
        data = json.loads(DATA_PATH.read_text(encoding='utf-8'))
        filas = data['mapping']

        self.stdout.write('MODO: ' + ('APLICANDO' if confirmar else 'ENSAYO (no escribe)'))
        self.stdout.write(f'Filas en la planilla: {len(filas)}')
        self.stdout.write('')

        aplicados, sin_match = [], []

        with transaction.atomic():
            for fila in filas:
                slug = _slug_de_url(fila['URL Actual'])
                parcela = Parcela.objects.filter(slug=slug).first()
                if not parcela:
                    sin_match.append(slug)
                    continue

                cambios = []
                if parcela.seo_title != fila['Title Nuevo']:
                    cambios.append('title')
                    parcela.seo_title = fila['Title Nuevo']
                if parcela.seo_h1 != fila['H1 Nuevo']:
                    cambios.append('h1')
                    parcela.seo_h1 = fila['H1 Nuevo']
                ciudad = fila.get('Ciudad') or ''
                if parcela.ciudad != ciudad:
                    cambios.append('ciudad')
                    parcela.ciudad = ciudad

                if cambios and confirmar:
                    parcela.save(update_fields=['seo_title', 'seo_h1', 'ciudad'])
                if cambios:
                    aplicados.append((slug, cambios))

            if not confirmar:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f'=== {len(aplicados)} parcelas con cambios ==='))
        for slug, cambios in aplicados:
            self.stdout.write(f"   {slug:<45} {', '.join(cambios)}")

        if sin_match:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(
                f'=== {len(sin_match)} filas sin match (slug no existe en la base) ==='))
            for slug in sin_match:
                self.stdout.write(f'   {slug}')

        self.stdout.write('')
        if confirmar:
            self.stdout.write(self.style.SUCCESS('Aplicado.'))
        else:
            self.stdout.write(self.style.WARNING('Ensayo. Repetir con --confirmar.'))
