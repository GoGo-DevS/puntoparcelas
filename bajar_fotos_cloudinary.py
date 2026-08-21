r"""Baja las 324 fotos de Cloudinary apenas la cuenta vuelva a responder.

    python bajar_fotos_cloudinary.py                       # prueba con 3
    python bajar_fotos_cloudinary.py --todas               # baja las 324
    python bajar_fotos_cloudinary.py --todas --destino D:\fotos-leo

NO NECESITA Django, ni la base de datos, ni credenciales. Solo internet.

Por que asi: los 324 public_id salieron de leer el HTML del sitio EN VIVO
(rescate/inventario.json), no de la base. La base de produccion vive en Render y
no la tenemos a mano; el inventario si. Y con la cuenta reactivada las URL de
entrega publica vuelven a funcionar, asi que no hace falta la Admin API.

Contexto (20-08-2026): la cuenta dd1ps0y8f quedo deshabilitada por pasarse del
cupo gratis. Ni la entrega ni la Admin API dejaban sacar nada. Leonardo, que era
el otro camino, borro las fotos de su telefono despues de subirlas. Cloudinary
quedo como UNICA fuente.

El reloj corre desde que se paga: baja TODO primero y despues se decide que
hacer con cada archivo. Guarda tambien un registro de que se bajo y que no.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
INVENTARIO = os.path.join(RAIZ, 'rescate', 'inventario.json')
CLOUD = 'dd1ps0y8f'
# Sin transformaciones: se quiere el ORIGINAL. Achicar se hace despues, en
# restaurar_fotos, que ademas lo deja en WebP bajo 100 KB como pidio el SEO.
BASE = f'https://res.cloudinary.com/{CLOUD}/image/upload/v1/'
UA = {'User-Agent': 'GoGoDevS/1.0 (rescate de assets propios)'}


def public_ids():
    """Los public_id unicos del inventario, en orden estable."""
    with open(INVENTARIO, encoding='utf-8') as fh:
        inv = json.load(fh)
    vistos, orden = set(), []
    for ids in inv['paginas'].values():
        for pid in ids:
            if pid not in vistos:
                vistos.add(pid)
                orden.append(pid)
    return orden


def bajar(pid, destino, intentos=3):
    """Devuelve (ok, bytes_o_error). Prueba las extensiones habituales.

    El public_id NO trae extension y Cloudinary sirve el original con la suya.
    Pedir sin extension suele funcionar, pero no siempre: si no, se prueban las
    comunes antes de darlo por perdido.
    """
    ultimo = ''
    for ext in ('', '.jpg', '.jpeg', '.png', '.webp'):
        url = BASE + pid + ext
        for intento in range(intentos):
            try:
                r = urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=90)
                datos = r.read()
                if not datos:
                    ultimo = 'respuesta vacia'
                    break
                real = ext or os.path.splitext(
                    r.headers.get('Content-Disposition', '') or '.jpg')[-1] or '.jpg'
                if real not in ('.jpg', '.jpeg', '.png', '.webp'):
                    real = '.jpg'
                nombre = pid.rsplit('/', 1)[-1] + real
                with open(os.path.join(destino, nombre), 'wb') as fh:
                    fh.write(datos)
                return True, len(datos)
            except urllib.error.HTTPError as e:
                ultimo = f'HTTP {e.code}'
                if e.code in (401, 403):
                    return False, ultimo      # cuenta cerrada: no insistir
                if e.code == 404:
                    break                     # esta extension no es: probar otra
                time.sleep(2 * (intento + 1))
            except Exception as e:
                ultimo = str(e)[:60]
                time.sleep(2 * (intento + 1))
    return False, ultimo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--todas', action='store_true',
                    help='Sin esto solo prueba con 3, para no gastar al pedo si sigue cerrada.')
    ap.add_argument('--destino', default=os.path.join(RAIZ, 'rescate', 'originales'))
    op = ap.parse_args()

    if not os.path.exists(INVENTARIO):
        sys.exit(f'Falta {INVENTARIO}')
    os.makedirs(op.destino, exist_ok=True)

    ids = public_ids()
    print(f'Inventario: {len(ids)} archivos · destino: {op.destino}\n')

    # SIEMPRE se prueba con uno antes de lanzar los 324: si la cuenta sigue
    # cerrada devuelve 401 y no tiene sentido seguir.
    ok, det = bajar(ids[0], op.destino)
    if not ok:
        print(f'La cuenta NO responde ({det}).')
        print('Si acabas de pagar, espera unos minutos y vuelve a correr esto.')
        sys.exit(1)
    print(f'Cuenta REACTIVADA: la primera bajo bien ({det/1024:.0f} KB).\n')

    objetivo = ids if op.todas else ids[:3]
    if not op.todas:
        print('MODO PRUEBA — solo 3. Agrega --todas para bajar las 324.\n')

    bien, mal, total = 1, [], det
    for i, pid in enumerate(objetivo[1:], start=2):
        ok, det = bajar(pid, op.destino)
        if ok:
            bien += 1
            total += det
            print(f'  [{i:3}/{len(objetivo)}] {pid.rsplit("/",1)[-1][:44]:46} {det/1024:>6.0f} KB')
        else:
            mal.append((pid, det))
            print(f'  [{i:3}/{len(objetivo)}] {pid.rsplit("/",1)[-1][:44]:46} FALLO: {det}')

    print(f'\n{bien} bajadas · {len(mal)} fallidas · {total/1048576:.1f} MB')
    registro = os.path.join(op.destino, '_resultado.json')
    with open(registro, 'w', encoding='utf-8') as fh:
        json.dump({'bajadas': bien, 'fallidas': mal, 'bytes': total}, fh,
                  ensure_ascii=False, indent=2)
    print(f'Detalle en {registro}')
    if mal:
        print('\nLas fallidas hay que reintentarlas ANTES de cancelar el plan.')


if __name__ == '__main__':
    main()
