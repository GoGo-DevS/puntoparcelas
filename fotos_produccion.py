# -*- coding: utf-8 -*-
"""Corre `optimizar_fotos` contra PRODUCCION con las variables de .env.produccion.

Uso (desde esta carpeta, con el venv de GoGoCRM):

    ..\\venv\\Scripts\\python.exe fotos_produccion.py                      ensayo, no escribe
    ..\\venv\\Scripts\\python.exe fotos_produccion.py --parcela <slug>     una sola parcela
    ..\\venv\\Scripts\\python.exe fotos_produccion.py --todas              todas

Las dos ultimas escriben: suben la WebP a R2 y cambian la ficha en Neon. El
original de cada foto queda en respaldos/fotos-<fecha>/ ANTES de convertirla, y
nunca se borra del bucket.

Por que existe: settings.py lee `.env`, que en esta carpeta apunta a la base
local. Las variables de produccion viven aparte para que ninguna prueba ni
runserver toque Neon o R2 por accidente; esto las carga solo para esta corrida
y se niega si falta alguna (con R2 a medias, Django guardaria en disco local
y la ficha quedaria apuntando a un archivo que el sitio no tiene).
"""
import datetime
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
NECESARIAS = ('DATABASE_URL', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY',
              'R2_BUCKET', 'R2_ENDPOINT', 'R2_PUBLIC_URL')


def main(argv):
    from dotenv import dotenv_values

    archivo = os.path.join(AQUI, '.env.produccion')
    if not os.path.exists(archivo):
        sys.exit('Falta .env.produccion')
    valores = dotenv_values(archivo)
    faltan = [n for n in NECESARIAS if not (valores.get(n) or '').strip()]
    if faltan:
        sys.exit('Faltan en .env.produccion: ' + ', '.join(faltan))
    for n in NECESARIAS:
        os.environ[n] = valores[n].strip()
    # settings.py hace load_dotenv() sin override: lo de arriba manda sobre .env.

    sys.path.insert(0, AQUI)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()

    from django.conf import settings
    if settings.STORAGES['default']['BACKEND'] != 'storages.backends.s3.S3Storage':
        sys.exit('El almacenamiento NO quedo en R2: no se corre nada.')
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        sys.exit('La base quedo en SQLite, no en produccion: no se corre nada.')

    args = []
    if '--todas' in argv or '--parcela' in argv:
        respaldo = os.path.join(AQUI, 'respaldos', f'fotos-{datetime.date.today():%Y-%m-%d}')
        args += ['--aplicar', '--respaldo', respaldo]
    if '--parcela' in argv:
        args += ['--parcela', argv[argv.index('--parcela') + 1]]

    from django.core.management import call_command
    call_command('optimizar_fotos', *args)


if __name__ == '__main__':
    main(sys.argv[1:])
