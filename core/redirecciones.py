# -*- coding: utf-8 -*-
"""Fichas duplicadas que responden 301 hacia la ficha canonica.

Jorge Urzua, planilla de enlazado interno del 23-11-2026 (Indexo), filas 37,
41 y 42. Se verifico cada una contra el sitio en vivo ANTES de redirigir,
porque una 301 esconde para siempre la pagina de origen:

    /catalogo/hacienda-don-bastian-5000-m2-con-rol-propio-por-16990000-2/
        mismo proyecto, mismo precio ($16.990.000) que /catalogo/hacienda-don-bastian/
        y rankeaba en pos. 8 para "hacienda don bastian" compitiendo con la buena.
        -> DUPLICADA: se redirige.

    /catalogo/hacienda-don-bastian-parcela-i381-3/
        NO es duplicada: es UNA parcela dentro del proyecto (pozo entubado, 2
        terrazas, cerrada) a $29.990.000, disponible. Redirigirla borraria del
        sitio un aviso que Leonardo esta vendiendo. Queda como esta.

    /catalogo/bosques-de-frutillar-parcela-r50/
        NO es duplicada: es un lote VENDIDO a $20.990.000, distinto del proyecto
        (desde $14.990.000). Queda como esta.

Se hace en codigo y no borrando la fila: la ficha duplicada sigue en la base
(y en el panel de Leonardo) hasta que el decida borrarla. Mientras tanto la
URL responde 301 y el manager `Parcela.publicas` la saca de todo listado
publico, para que el sitio no enlace a una URL que redirige.

Regla: 301 directas, sin cadenas. Un destino nunca puede ser a su vez origen
(lo comprueba tests_enlazado_23_11).
"""

REDIRECCIONES_301 = {
    'hacienda-don-bastian-5000-m2-con-rol-propio-por-16990000-2': 'hacienda-don-bastian',
}
