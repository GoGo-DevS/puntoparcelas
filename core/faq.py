# -*- coding: utf-8 -*-
"""Las preguntas frecuentes que Leonardo escribe DENTRO de la descripcion.

Punto 10 del documento de Jorge (05-10-2026): que cada pregunta sea un H3 y
que la ficha declare su FAQPage. El contenido ya existia -- 574 preguntas en
47 de 48 fichas, medido el 06-10 con analizar_faq_fichas.py -- pero vivia como
texto corrido y Google lo leia como parrafo.

POR QUE SE PARTE AL MOSTRAR Y NO SE MUEVE A UN CAMPO NUEVO
Moverlas era una migracion de datos sobre la base de produccion, y Leonardo
tendria que aprender a escribir las preguntas en otro lado. Asi no cambia nada
para el: sigue escribiendo "❓ PREGUNTAS FRECUENTES" en la descripcion como lo
hace hoy, y una ficha nueva sale marcada sola. La descripcion guardada no se
toca nunca.

Lo que hay ANTES del marcador se muestra tal cual; lo que hay DESPUES del
cierre comercial ("AGENDA TU VISITA", el pie) tambien. Solo el tramo entre
los dos se convierte en preguntas. Nada del texto de Leonardo desaparece.

Las trampas son las de analizar_faq_fichas.py, que siguen probadas en
tests_faq_fichas.py: dos formatos (parrafos y "un bloque" pegado), la
pregunta de gancho antes del marcador, el cierre comercial pegado a la ultima
respuesta y el punto final que un strip(' .') se comia.
"""
import re

ABRE = chr(191)         # ¿
INTERROGA = chr(10067)  # ❓, el emoji que Leonardo pone antes del titulo
MOVIL = chr(128242)     # 📲, el del cierre comercial

MARCA = re.compile(r'PREGUNTAS\s+FRECUENTES', re.I)
CIERRE = re.compile(
    '(AGENDA TU VISITA|Contacta a tu asesor|Tu inversi' + chr(243) + 'n hoy'
    '|Estamos en todo Chile|' + MOVIL + ')', re.I)


def _pares(texto):
    """[(pregunta, respuesta)]: la pregunta va de '¿' a '?', la respuesta hasta el siguiente '¿'."""
    salida = []
    posiciones = [m.start() for m in re.finditer(ABRE, texto)]
    for i, inicio in enumerate(posiciones):
        cierra = texto.find('?', inicio)
        if cierra == -1:
            continue
        fin = posiciones[i + 1] if i + 1 < len(posiciones) else len(texto)
        if cierra > fin:
            # El '?' es de la pregunta siguiente: esta no cerro nunca.
            continue
        pregunta = ' '.join(texto[inicio:cierra + 1].split())
        # Solo espacios: el punto final de la respuesta SE CONSERVA.
        respuesta = ' '.join(texto[cierra + 1:fin].split())
        # Una pregunta sin respuesta no se declara: ese FAQPage es invalido.
        if pregunta and respuesta:
            salida.append((pregunta, respuesta))
    return salida


def partir(descripcion):
    """(arriba, preguntas, abajo) de una descripcion de ficha.

    Sin marcador devuelve (descripcion, [], ''): la ficha se ve igual que antes.
    """
    texto = descripcion or ''
    m = MARCA.search(texto)
    if not m:
        return texto, [], ''

    # El emoji del titulo va antes del marcador: sin quitarlo, la descripcion
    # termina en un "❓" suelto.
    arriba = texto[:m.start()].rstrip().rstrip(INTERROGA).rstrip()
    resto = texto[m.end():]

    corte = CIERRE.search(resto)
    tramo = resto[:corte.start()] if corte else resto
    abajo = resto[corte.start():].strip() if corte else ''

    preguntas = _pares(tramo)
    if not preguntas:
        # Marcador sin preguntas reconocibles: se muestra todo como estaba
        # antes que perder texto.
        return texto, [], ''

    # Lo que Leonardo escriba entre el titulo y la primera pregunta no es de
    # ninguna pregunta: se queda arriba en vez de perderse. Al 13-10 ninguna
    # de las 54 fichas tiene, pero nada impide que la proxima si.
    intro = tramo[:tramo.find(ABRE)].strip()
    if intro:
        arriba = f'{arriba}\n\n{intro}' if arriba else intro
    return arriba, preguntas, abajo
