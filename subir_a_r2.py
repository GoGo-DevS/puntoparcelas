r"""Sube los archivos rescatados a R2 con la MISMA clave que la base ya guarda.

21-08-2026, urgente: al poner las variables de R2 en Render el sitio empezo a
pedir las fotos a R2 y el bucket estaba VACIO. 404 en todas.

La gracia de este script es que NO necesita la base de datos. La clave de cada
objeto en R2 tiene que ser identica al `name` que el ImageField ya tiene
guardado (media/parcelas/IMG-20240221-WA01363_sdruo2, sin extension, como lo
dejo Cloudinary). Subiendo con esa clave exacta, el sitio funciona sin tocar un
solo registro.

Los archivos rescatados estan aplanados con '__' (media__parcelas__X.jpg), asi
que la clave se reconstruye al reves: se quita la extension que le pusimos al
bajar y se devuelven las barras.

    python subir_a_r2.py              # ensayo
    python subir_a_r2.py --confirmar
"""
import argparse
import mimetypes
import os
import sys

import boto3
from botocore.client import Config
from dotenv import load_dotenv

load_dotenv()
RAIZ = os.path.dirname(os.path.abspath(__file__))
ORIGEN = os.path.join(RAIZ, 'rescate', 'completo')


def s3():
    return boto3.client(
        's3', endpoint_url=os.environ['R2_ENDPOINT'],
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        config=Config(signature_version='s3v4', max_pool_connections=24),
        region_name='auto')


def clave_de(nombre):
    """media__parcelas__IMG-x_ab12cd.jpg -> media/parcelas/IMG-x_ab12cd

    La extension se la pusimos NOSOTROS al descargar; el public_id original no
    la tenia. Si se sube con extension, la clave no calza con lo que pide el
    sitio y sigue dando 404.
    """
    base = os.path.splitext(nombre)[0]
    return base.replace('__', '/')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--confirmar', action='store_true')
    op = ap.parse_args()

    archivos = [f for f in sorted(os.listdir(ORIGEN)) if not f.endswith('.json')]
    print(f'{len(archivos)} archivos en {ORIGEN}')
    for f in archivos[:3]:
        print(f'   {f[:52]:54} -> {clave_de(f)}')
    if not op.confirmar:
        print('\nENSAYO. Agrega --confirmar.')
        return

    cli = s3()
    bucket = os.environ['R2_BUCKET']
    ya = set()
    for page in cli.get_paginator('list_objects_v2').paginate(Bucket=bucket):
        ya |= {o['Key'] for o in page.get('Contents', [])}
    print(f'{len(ya)} objetos ya en el bucket')

    ok = saltados = 0
    fallidos = []
    for i, f in enumerate(archivos, 1):
        key = clave_de(f)
        if key in ya:
            saltados += 1
            continue
        tipo = mimetypes.guess_type(f)[0] or 'image/jpeg'
        try:
            cli.upload_file(os.path.join(ORIGEN, f), bucket, key,
                            ExtraArgs={'ContentType': tipo})
            ok += 1
            if ok % 50 == 0:
                print(f'  [{i}/{len(archivos)}] {ok} subidos', flush=True)
        except Exception as e:
            fallidos.append((key, str(e)[:60]))

    print(f'\n{ok} subidos · {saltados} ya estaban · {len(fallidos)} fallidos')
    for k, e in fallidos[:10]:
        print(f'  ! {k}: {e}')
    sys.exit(1 if fallidos else 0)


if __name__ == '__main__':
    main()
