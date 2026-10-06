# -*- coding: utf-8 -*-
"""El contenido SEO de la home (Jorge Urzua, 05-10-2026).

POR QUE
-------
La home captaba solo la marca. No tenia una sola linea apuntando a las head
terms genericas que la competencia si trabaja en su portada: "parcelas en
venta", "terrenos en venta", "comprar parcela", "parcelas baratas". Son las
consultas de mas volumen del rubro y entraban por cualquier pagina menos por
la que tiene mas autoridad del sitio.

EL BLOQUE DE REGIONES SALE DE LOS DATOS, NO DE LA LISTA DEL DOCUMENTO
---------------------------------------------------------------------
El documento propone enlazar a 11 regiones. Medido el 06-10 en vivo, CUATRO de
esas 11 devuelven 404:

    /catalogo/araucania/   404     /catalogo/biobio/   404
    /catalogo/los-rios/    404     /catalogo/aysen/    404

No es un error del documento ni del sitio: una region sin parcelas es 404 a
proposito desde el 22-09 (tests_regiones_vacias). Pero copiar la lista tal cual
habria puesto CUATRO enlaces rotos en la portada, que es justo donde mas
cuestan.

Por eso el bloque se arma con `_regiones_con_parcelas()`, igual que los botones
del catalogo: aparecen las que tienen contenido y se suman solas cuando
Leonardo cargue una parcela en una region nueva.

LAS PREGUNTAS SON LAS DEL DOCUMENTO, Y SE MUESTRAN
--------------------------------------------------
El FAQPage se declara SOLO con preguntas visibles en la pagina -- declarar una
que el visitante no ve es marcado enganoso y Google lo sanciona a mano. Las
seis se dibujan al pie de la home.

Los enlaces usan el mismo marcador [[anchor|/ruta/]] que las guias y se
resuelven igual. Las dos guias que citan estas respuestas existen desde el
commit anterior.
"""

# (pregunta, respuesta). El texto es el del documento.
PREGUNTAS = [
    ('¿Qué es una parcela de agrado?',
     'Es un lote rural subdividido bajo el Decreto Ley 3.516 para vivir, descansar o '
     'invertir, no para producir. Lo explicamos en detalle en la guía sobre '
     '[[qué es una parcela de agrado|/guias/que-es-una-parcela-de-agrado/]].'),
    ('¿Qué significa que una parcela tenga rol propio?',
     'Significa que el Servicio de Impuestos Internos la reconoce como propiedad '
     'independiente, con su propio avalúo y contribuciones. Es el documento clave '
     'para dar seguridad a la compra.'),
    ('¿Cómo compro una parcela en Chile?',
     'El proceso parte por visitar el terreno, pedir el certificado de dominio, '
     'verificar el rol propio y la factibilidad de agua, y cerrar con escritura '
     'inscrita en el Conservador. Revisa la guía de '
     '[[qué revisar antes de comprar una parcela|/guias/que-revisar-antes-de-comprar-una-parcela/]].'),
    ('¿Cómo sé si una parcela tiene agua?',
     'Hay que pedir el informe del pozo ejecutado, con su caudal medido en litros por '
     'segundo, y el derecho de aprovechamiento de aguas inscrito cuando exista. En '
     'zonas de secano, el agua define el valor del terreno.'),
    ('¿Cómo funciona el crédito directo en parcelas?',
     'El vendedor financia el saldo en cuotas, sin banco. Lo habitual es un pie y '
     'mensualidades a plazo, con la propiedad inscrita según lo pactado. Siempre '
     'conviene dejarlo por escrito ante notario.'),
    ('¿Conviene invertir en parcelas?',
     'Depende de tres factores: la consolidación del sector, el acceso al agua y la '
     'distancia real a servicios. Un terreno bien ubicado y con agua tiende a '
     'mantener y subir su valor.'),
]

# Los bloques de texto de la home. (titulo, [parrafos]).
# El titulo vacio significa que el bloque va sin H2 propio.
BLOQUES = [
    ('Parcelas en venta en todo Chile', [
        'El interés por dejar la ciudad y tener terreno propio sigue firme en Chile. '
        'Cada vez más familias buscan espacio, naturaleza y una inversión que mantenga '
        'su valor.',
        'En este portal reunimos parcelas y terrenos en venta de distintas regiones del '
        'país, en un solo lugar y con la información que de verdad importa antes de '
        'comprar.',
        'Puedes comparar proyectos por zona, superficie, acceso a agua y forma de pago. '
        'Así encuentras la parcela que calza con lo que buscas, sin dar vueltas.',
    ]),
    ('Comprar una parcela de forma segura', [
        'Comprar una parcela es una decisión grande y conviene hacerla con los papeles '
        'claros. Revisa el rol propio, el acceso al agua y la forma de pago antes de '
        'firmar.',
        'Si recién estás partiendo, nuestra guía explica '
        '[[cómo comprar una parcela en Chile paso a paso|/guias/que-revisar-antes-de-comprar-una-parcela/]] '
        'y qué revisar antes de firmar en cada etapa.',
    ]),
    ('Parcelas baratas y cerca de Santiago', [
        'Si buscas [[parcelas baratas|/catalogo/parcelas-baratas/]], el valor por metro '
        'cuadrado baja fuerte al alejarse de los centros turísticos. El secano costero y '
        'las zonas de valle ofrecen más superficie por el mismo presupuesto.',
        'Para quienes viven en la capital, hay parcelas cerca de Santiago en la costa de '
        '[[O\'Higgins|/catalogo/ohiggins/]] y [[Valparaíso|/catalogo/valparaiso/]], a '
        'pocas horas de viaje y con buena conectividad.',
    ]),
]

# Las vinetas de "Parcelas y terrenos en venta por todo el pais".
VINETAS = [
    'Parcelas de agrado con rol propio y plano aprobado',
    'Terrenos en venta con factibilidad de agua y luz',
    'Proyectos con crédito directo, sin pasar por el banco',
    'Superficies desde 5.000 m² en adelante',
]


def preguntas_visibles():
    """[(pregunta, html)] con los enlaces ya resueltos, para dibujar."""
    from . import guias as _guias
    return [(p, _guias.con_enlaces(r)) for p, r in PREGUNTAS]


def preguntas_planas():
    """[(pregunta, texto)] sin marcado, para el FAQPage.

    El schema lleva texto plano: el marcador [[...]] ahi se publicaria crudo.
    """
    from . import guias as _guias
    return [(p, _guias.sin_marcadores(r)) for p, r in PREGUNTAS]


def bloques_visibles(caracteristicas_vivas=None):
    """[(titulo, [html])] con los enlaces resueltos.

    `caracteristicas_vivas` son las paginas por caracteristica que HOY tienen
    al menos una parcela (lo que devuelve `_caracteristicas_con_parcelas`). El
    texto enlaza a "parcelas baratas", y esa pagina devuelve 404 cuando ninguna
    parcela cumple el filtro: si no esta viva, el enlace baja al catalogo en vez
    de publicarse roto. Es la misma regla que el bloque de regiones.
    """
    from . import guias as _guias

    vivas = {c['slug'] for c in (caracteristicas_vivas or [])}

    def arreglar(texto):
        for slug in ('parcelas-baratas',):
            if slug not in vivas:
                texto = texto.replace('|/catalogo/%s/]]' % slug, '|/catalogo/]]')
        return _guias.con_enlaces(texto)

    return [(t, [arreglar(p) for p in parrafos]) for t, parrafos in BLOQUES]
