# -*- coding: utf-8 -*-
"""Mide las preguntas frecuentes que Leonardo escribio DENTRO de cada ficha.

POR QUE EXISTE
--------------
Las fichas de proyecto traen preguntas frecuentes de verdad -- 574 repartidas
en 47 de las 48 fichas -- pero viven dentro de `Parcela.descripcion` como texto
corrido. Google las lee como parrafo, asi que no las puede mostrar desplegables
en el resultado de busqueda. El contenido ya esta hecho; lo que falta es
declararlo (FAQPage), y para eso hay que darle un campo propio.

Este script NO migra nada. Mide si ese movimiento se puede hacer solo, que es
lo que decide si el trabajo son horas o son 574 copiar-y-pegar.

LO MEDIDO EL 06-10-2026 (sobre el sitio en vivo, 48 fichas)
-----------------------------------------------------------
    fichas con preguntas .......... 47 de 48
    preguntas totales ............. 574
    preguntas sin respuesta ....... 0
    las FAQ son el ................ 49% de la descripcion

HAY DOS FORMATOS, Y MEDIR UNO SOLO DA UN NUMERO FALSO
-----------------------------------------------------
    33 fichas  "parrafos"   el texto trae saltos de linea, asi que cada
                            pregunta y cada respuesta es su propio parrafo.
    14 fichas  "un bloque"  Leonardo pego el texto SIN saltos de linea: la
                            ficha entera es un parrafo y las preguntas van
                            pegadas adentro ("...VICHUQUENNuevo proyecto...").

La primera version de esta medicion solo entendia el formato de parrafos y
reportaba CERO preguntas para esas 14 fichas, teniendolas. Por eso el corte se
hace por el MARCADOR que escribe Leonardo y no por la estructura del HTML.

DOS TRAMPAS MAS, las dos encontradas mirando el contenido extraido
------------------------------------------------------------------
 1. Despues de la ultima pregunta viene el cierre comercial ("AGENDA TU
    VISITA", el pie de pagina). Sin cortar ahi, esos 7 parrafos se pegaban
    DENTRO de la respuesta a "Puedo visitar la propiedad?".
 2. Limpiar la respuesta con strip(' .') se come el punto final y deja
    "El precio informado es de $30.000.000" sin su punto. Se limpian solo
    espacios y el marcador de union.
"""
import os
import re
import sys

ABRE = chr(191)        # signo de apertura de pregunta
UNION = chr(182)       # marcador interno para unir parrafos
INTERROGA = chr(10067) # el emoji que Leonardo pone antes del titulo
MOVIL = chr(128242)    # el emoji del cierre comercial

MARCA = re.compile(r'PREGUNTAS\s+FRECUENTES', re.I)
PARRAFO = re.compile(r'<p[^>]*>(.*?)</p>', re.S | re.I)
TAG = re.compile(r'<[^>]+>')

# Donde DEJA de ser FAQ: los cierres comerciales que Leonardo escribe despues.
CIERRE = re.compile(
    '(AGENDA TU VISITA|Contacta a tu asesor|Tu inversi' + chr(243) + 'n hoy'
    '|Estamos en todo Chile|' + MOVIL + ')', re.I)


def _plano(s):
    s = TAG.sub('', s)
    for a, b in (('&amp;', '&'), ('&quot;', '"'), ('&#x27;', "'"),
                 ('&#39;', "'"), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')):
        s = s.replace(a, b)
    return ' '.join(s.split())


def pares(texto):
    """[(pregunta, respuesta)] de un texto corrido.

    La pregunta abre en el signo de apertura y cierra en '?'. La respuesta es
    lo que sigue hasta la pregunta siguiente, o hasta el cierre comercial.
    """
    salida = []
    posiciones = [m.start() for m in re.finditer(ABRE, texto)]
    for i, inicio in enumerate(posiciones):
        cierra = texto.find('?', inicio)
        if cierra == -1:
            continue
        pregunta = texto[inicio:cierra + 1].strip()
        fin = posiciones[i + 1] if i + 1 < len(posiciones) else len(texto)
        resp = texto[cierra + 1:fin]
        corte = CIERRE.search(resp)
        if corte:
            resp = resp[:corte.start()]
        # Solo espacios y el marcador de union: el punto final SE CONSERVA.
        resp = resp.strip().strip(UNION + ' ').strip()
        if pregunta and resp:
            salida.append((pregunta, resp))
    return salida


def partir_descripcion(texto, es_html=True):
    """Devuelve (lo_que_queda, [(pregunta, respuesta)]).

    `lo_que_queda` es la descripcion sin las FAQ: es lo que seguiria viviendo
    en el campo actual el dia que las preguntas se muevan a uno propio.
    """
    if es_html:
        trozos = [p for p in (_plano(x) for x in PARRAFO.findall(texto)) if p]
    else:
        trozos = [p for p in (' '.join(l.split()) for l in texto.split(chr(10))) if p]

    idx = [i for i, p in enumerate(trozos) if MARCA.search(p)]
    if not idx:
        return ((' ' + UNION + ' ').join(trozos).strip(), [])
    i = idx[0]

    # Formato "un bloque": las preguntas van pegadas en el mismo parrafo.
    # Basta UNA. Con el umbral en dos, una ficha de una sola pregunta caia a la
    # rama de parrafos -- donde no hay parrafos siguientes -- y se perdia entera,
    # sin error ni aviso.
    if ABRE in trozos[i]:
        m = MARCA.search(trozos[i])
        # El emoji que Leonardo pone antes del titulo va ANTES de m.start(), asi
        # que sin quitarlo la descripcion termina en un "?" suelto.
        queda = trozos[i][:m.start()].rstrip().rstrip(INTERROGA).rstrip()
        return (queda, pares(trozos[i][m.end():]))

    # Formato "parrafos": el marcador es su propio parrafo.
    queda = (' ' + UNION + ' ').join(trozos[:i]).strip()
    bloque = trozos[i + 1:]
    limite = len(bloque)
    for j, p in enumerate(bloque):
        if CIERRE.search(p) and not p.startswith(ABRE):
            limite = j
            break
    return (queda, pares((' ' + UNION + ' ').join(bloque[:limite])))


def autoprueba():
    """Los casos que costaron encontrar, fijos, para que no vuelvan."""
    fallos = []

    def revisar(nombre, condicion):
        if not condicion:
            fallos.append(nombre)

    # formato "parrafos", con cierre comercial detras
    html = ('<p>Linda parcela.</p><p>' + INTERROGA + ' PREGUNTAS FRECUENTES</p>'
            '<p>' + ABRE + 'Cual es el valor?</p><p>Es de $30.000.000.</p>'
            '<p>' + ABRE + 'Tiene rol?</p><p>Si. Tiene rol propio.</p>'
            '<p>' + MOVIL + ' AGENDA TU VISITA</p><p>Ven a conocerla.</p>')
    queda, faq = partir_descripcion(html)
    revisar('parrafos: 2 preguntas', len(faq) == 2)
    revisar('parrafos: conserva el punto final',
            faq and faq[0][1] == 'Es de $30.000.000.')
    revisar('parrafos: el cierre comercial NO entra en la respuesta',
            len(faq) == 2 and 'AGENDA' not in faq[1][1]
            and 'conocerla' not in faq[1][1])
    revisar('parrafos: lo que queda es la descripcion', queda == 'Linda parcela.')

    # formato "un bloque": todo pegado, sin saltos de linea
    pegado = ('<p>BRISASNuevo proyecto. ' + INTERROGA + ' PREGUNTAS FRECUENTES '
              + ABRE + 'Desde que valor? Desde $29.990.000. '
              + ABRE + 'Hay financiamiento? Si, con pie y cuotas.</p>')
    queda, faq = partir_descripcion(pegado)
    revisar('un bloque: 2 preguntas', len(faq) == 2)
    revisar('un bloque: respuesta limpia',
            faq and faq[0][1] == 'Desde $29.990.000.')
    revisar('un bloque: queda la descripcion', 'BRISAS' in queda)
    revisar('un bloque: la descripcion NO se lleva las preguntas',
            ABRE not in queda)

    # 10 fichas reales ABREN con una pregunta de gancho ("POR QUE ELEGIR
    # FUNDO CAUQUENES?") antes del marcador. Sin cortar en el marcador, esas
    # diez entrarian al FAQPage como preguntas con una respuesta inventada.
    gancho = ('<p>' + ABRE + 'POR QUE ELEGIR ESTE FUNDO?</p>'
              '<p>Porque combina tres cosas.</p>'
              '<p>' + INTERROGA + ' PREGUNTAS FRECUENTES</p>'
              '<p>' + ABRE + 'Cuanto mide?</p><p>Son 5.000 m2.</p>')
    queda, faq = partir_descripcion(gancho)
    revisar('el gancho de la descripcion NO entra al FAQPage', len(faq) == 1)
    revisar('el gancho se queda en la descripcion', 'POR QUE ELEGIR' in queda)

    # lo mismo en el formato de un bloque, donde el gancho va pegado
    gancho2 = ('<p>' + ABRE + 'POR QUE ELEGIR? Porque si. '
               + INTERROGA + ' PREGUNTAS FRECUENTES '
               + ABRE + 'Cuanto mide? Son 5.000 m2.</p>')
    queda, faq = partir_descripcion(gancho2)
    revisar('un bloque: el gancho NO entra al FAQPage', len(faq) == 1)

    # un bloque con UNA sola pregunta: antes se perdia entera (umbral >= 2)
    una = ('<p>Hola. ' + INTERROGA + ' PREGUNTAS FRECUENTES '
           + ABRE + 'Puedo visitar? Si, claro. '
           + MOVIL + ' AGENDA TU VISITA Ven a verla.</p>')
    queda, faq = partir_descripcion(una)
    revisar('un bloque de UNA pregunta: no se pierde', len(faq) == 1)
    revisar('un bloque de UNA pregunta: corta el cierre pegado',
            faq and faq[0][1] == 'Si, claro.')
    revisar('un bloque: el emoji del titulo NO queda en la descripcion',
            queda == 'Hola.')

    # una ficha sin preguntas no debe inventar ninguna
    queda, faq = partir_descripcion('<p>Solo descripcion, sin preguntas.</p>')
    revisar('sin faq: 0 preguntas', faq == [])
    revisar('sin faq: la descripcion queda entera', 'Solo descripcion' in queda)

    # una pregunta sin respuesta no se declara: un FAQPage asi es invalido
    queda, faq = partir_descripcion(
        '<p>' + INTERROGA + ' PREGUNTAS FRECUENTES</p><p>' + ABRE + 'Y esta?</p>')
    revisar('pregunta sin respuesta: no se declara', faq == [])

    for f in fallos:
        print('   FALLA: ' + f)
    print('autoprueba: OK' if not fallos else 'autoprueba: %d FALLAS' % len(fallos))
    return 0 if not fallos else 1


def informe(carpeta):
    """Barre HTML ya descargado (una ficha por archivo) y resume."""
    filas, total = [], 0
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.endswith('.html'):
            continue
        html = open(os.path.join(carpeta, nombre), encoding='utf-8').read()
        queda, faq = partir_descripcion(html)
        filas.append((nombre[:-5], len(faq), len(queda),
                      len(''.join(q + r for q, r in faq))))
        total += len(faq)
    print('%-38s %5s %9s %9s' % ('ficha', 'faq', 'queda', 'faq car.'))
    for slug, n, q, c in filas:
        print('%-38s %5d %9d %9d' % (slug[:38], n, q, c))
    print('')
    print('fichas ............ %d' % len(filas))
    print('con preguntas ..... %d' % sum(1 for _, n, _, _ in filas if n))
    print('preguntas totales . %d' % total)
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--autoprueba':
        sys.exit(autoprueba())
    if len(sys.argv) > 2 and sys.argv[1] == '--informe':
        sys.exit(informe(sys.argv[2]))
    print(__doc__)
    print('uso:  python analizar_faq_fichas.py --autoprueba')
    print('      python analizar_faq_fichas.py --informe <carpeta-con-html>')
