r"""Baja TODO lo que hay en la cuenta de Cloudinary, no solo lo publicado.

    python bajar_todo_cloudinary.py                 # ensayo: cuenta y pesa
    python bajar_todo_cloudinary.py --confirmar

Por que existe aparte de bajar_fotos_cloudinary.py: ese baja los 324 archivos
que el sitio muestra HOY, leidos del HTML en vivo. Pero la cuenta tiene 948
archivos (884 en media/), o sea unos 560 que Leonardo subio y despues quito, o
versiones reemplazadas. Con la cuenta abierta se bajan todos: es la unica
ventana que hay, y despues de cancelar el plan no se recupera ninguno.

Usa la Admin API, que da el `secure_url` exacto de cada archivo con su formato
real — no hay que adivinar la extension.

Salta lo que ya este bajado, asi que se puede correr despues del otro y solo
trae lo que falta. Y se puede reanudar si se corta.
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.abspath(__file__))
LISTA = os.path.join(RAIZ, 'rescate', 'todo_cloudinary.json')
UA = {'User-Agent': 'GoGoDevS/1.0 (rescate de assets propios)'}

# Los "samples" son las imagenes de demostracion que Cloudinary crea en toda
# cuenta nueva. No son del cliente y no sirven para nada.
IGNORAR = ('samples/', 'sample', 'cld-sample', 'main-sample')


def util(items):
    return [x for x in items
            if not any(x['public_id'].startswith(p) or x['public_id'] == p
                       for p in IGNORAR)]


def destino_de(x, carpeta):
    """Conserva la ruta de Cloudinary: media/parcelas/foo -> media__parcelas__foo.jpg

    Se aplana con '__' en vez de crear subcarpetas para que restaurar_fotos
    encuentre todo con un solo os.walk y para no chocar con nombres repetidos
    en carpetas distintas.
    """
    plano = x['public_id'].replace('/', '__')
    ext = x.get('format') or 'jpg'
    return os.path.join(carpeta, f'{plano}.{ext}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--confirmar', action='store_true')
    ap.add_argument('--destino', default=os.path.join(RAIZ, 'rescate', 'completo'))
    op = ap.parse_args()

    with open(LISTA, encoding='utf-8') as fh:
        todos = util(json.load(fh))
    peso = sum(x['bytes'] for x in todos) / 1048576
    print(f'{len(todos)} archivos del cliente · {peso:.0f} MB (samples de Cloudinary excluidos)')

    if not op.confirmar:
        print('\nENSAYO. Agrega --confirmar para bajar.')
        return

    os.makedirs(op.destino, exist_ok=True)
    bien = saltados = 0
    mal = []
    total = 0
    for i, x in enumerate(todos, 1):
        ruta = destino_de(x, op.destino)
        if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
            saltados += 1
            continue
        url = x.get('url') or ''
        if not url:
            mal.append((x['public_id'], 'sin secure_url'))
            continue
        for intento in range(3):
            try:
                r = urllib.request.urlopen(
                    urllib.request.Request(url, headers=UA), timeout=120)
                datos = r.read()
                with open(ruta, 'wb') as fh:
                    fh.write(datos)
                bien += 1
                total += len(datos)
                if bien % 25 == 0:
                    print(f'  [{i:4}/{len(todos)}] {bien} bajadas · {total/1048576:.0f} MB')
                break
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    mal.append((x['public_id'], f'HTTP {e.code}'))
                    print(f'\n  CUENTA CERRADA de nuevo (HTTP {e.code}). Corto acá.')
                    intento = 99
                    break
                time.sleep(2 * (intento + 1))
            except Exception as e:
                if intento == 2:
                    mal.append((x['public_id'], str(e)[:50]))
                time.sleep(2 * (intento + 1))
        if intento == 99:
            break

    print(f'\n{bien} bajadas · {saltados} ya estaban · {len(mal)} fallidas · {total/1048576:.0f} MB')
    reg = os.path.join(op.destino, '_resultado.json')
    with open(reg, 'w', encoding='utf-8') as fh:
        json.dump({'bajadas': bien, 'saltados': saltados, 'fallidas': mal}, fh,
                  ensure_ascii=False, indent=1)
    print(f'Detalle en {reg}')
    if mal:
        print('REINTENTAR ANTES DE CANCELAR EL PLAN.')


if __name__ == '__main__':
    main()
