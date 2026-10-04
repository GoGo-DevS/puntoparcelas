# -*- coding: utf-8 -*-
"""Las paginas por caracteristica que pidio Jorge (hoja "04 Caracteristicas").

POR QUE ESTE ARCHIVO EXISTE
---------------------------
El sitio tenia DOS tipos de pagina de catalogo -- por region y por ciudad -- y
la planilla de Indexo pide un TERCERO: por caracteristica ("parcelas con
credito directo", "parcela vista al mar"). Las dos URLs que Jorge probo el
01-10 daban 404 por esto, no por un error suyo.

LA DECISION QUE ORDENA TODO: DERIVADA vs MARCADA
------------------------------------------------
Una caracteristica se calcula sola (DERIVADA) o la marca Leonardo (MARCADA).
No es un detalle de implementacion, es lo que decide si la pagina miente.

  DERIVADA: sale de un dato que el sistema YA tiene y que Leonardo edita en la
  ficha (region, precio, rol propio, agua, luz). Si manana le baja el precio a
  una parcela, entra o sale sola de "baratas". Hacerlas manuales seria pedirle
  que mantenga el mismo dato en dos lados, y el dia que se olvide la pagina
  queda mintiendo sin que nada avise.

  MARCADA: no hay forma de deducirla. "Vista al mar" no esta en ningun campo y
  no se puede adivinar de la region -- Vive Ovalle tiene vista al mar y las
  otras cuatro de Coquimbo no. Esas son 4 casillas nuevas en la ficha, con los
  valores que dio Leonardo el 01-10 precargados por `marcar_caracteristicas`.

LO QUE NO SE PUBLICA, Y POR QUE
-------------------------------
  - "Parcela con casa" (880 busquedas/mes): Leonardo dijo textual "nada por
    ahora". Es la segunda keyword con mas volumen de la planilla y aun asi no
    se crea: una pagina sin una sola parcela se indexa igual y queda compitiendo
    contra las que si tienen. Nace el dia que cargue una.
  - "Parcela rural": Jorge la pide, Leonardo NO la menciono en su lista. No se
    inventa el criterio.

  Las dos quedan abajo en NO_PUBLICADAS para que la proxima sesion sepa que
  fueron una decision y no un olvido.

EL CASO DELICADO: "PARCELA EN LA PLAYA"
---------------------------------------
Es la keyword de mas volumen que SI se puede llenar (880/mes), y Leonardo dijo
igual de claro: "parcelas en la playa NO TENGO, pero hay algunas relativamente
cerca, 30 min". Publicar un H1 que diga "Parcela en la playa" sobre parcelas
que no estan en la playa es prometer algo que el catalogo no cumple, y lo paga
el cliente que llega y se va.

La salida: el SLUG queda como lo pide Jorge (es lo que ve Google) y el H1 y el
texto dicen la verdad -- "cerca de la playa", con los minutos. La keyword se
trabaja igual y nadie llega enganado.
"""
from django.db.models import Q

# (slug, H1, title, bajada que se muestra arriba de la grilla)
# El slug es el de la planilla de Indexo: no se cambia, es lo que Jorge trabaja.
_FICHAS = {
    'parcelas-sur-de-chile': (
        'Parcelas en el sur de Chile',
        'Parcelas en el sur de Chile en venta | Punto Parcelas',
        'Nuestros proyectos en la Región de Los Lagos: Frutillar, Puerto Varas, '
        'Osorno, Rupanco y Hualaihué.'),
    'parcelas-baratas': (
        'Parcelas baratas',
        'Parcelas baratas en venta desde $5.000.000 | Punto Parcelas',
        'Parcelas bajo los $10.000.000, varias con crédito directo y pie cero.'),
    'parcela-con-rol-propio': (
        'Parcelas con rol propio',
        'Parcelas con rol propio en venta | Punto Parcelas',
        'Parcelas ya subdivididas y con rol propio del SII: se escrituran a tu '
        'nombre sin esperar la subdivisión.'),
    'parcela-con-agua-y-luz': (
        'Parcelas con agua y luz',
        'Parcelas con agua y luz en venta | Punto Parcelas',
        'Parcelas que ya cuentan con agua potable y electricidad en el terreno.'),
    'parcela-con-credito-directo': (
        'Parcelas con crédito directo',
        'Parcelas con crédito directo y pie cero | Punto Parcelas',
        'Financiamiento directo con el vendedor, sin banco. Varias con pie cero.'),
    'parcela-vista-al-mar': (
        'Parcelas con vista al mar',
        'Parcelas con vista al mar en venta | Punto Parcelas',
        'Parcelas con vista directa al mar.'),
    'parcela-vista-al-lago': (
        'Parcelas con vista al lago',
        'Parcelas con vista al lago en venta | Punto Parcelas',
        'Parcelas con vista a lagos del sur: Rupanco, Llanquihue y Vichuquén.'),
    'parcela-en-la-playa': (
        # H1 honesto: ver el bloque de arriba. El slug SI es el de Jorge.
        'Parcelas cerca de la playa',
        'Parcelas cerca de la playa en venta | Punto Parcelas',
        'No vendemos parcelas con salida directa a la playa, pero estas están a '
        'menos de 30 minutos del mar.'),
    'parcela-de-campo': (
        'Parcelas de campo',
        'Parcelas de campo en venta en Chile | Punto Parcelas',
        'Todos nuestros proyectos son parcelas de campo, desde 5.000 m².'),
    'parcela-de-agrado': (
        'Parcelas de agrado',
        'Parcelas de agrado en venta en Chile | Punto Parcelas',
        'Parcelas de agrado de 5.000 m² en adelante, con rol propio y acceso.'),
}

# Las 4 que Leonardo marca a mano. El resto se calculan solas.
CAMPOS_MARCADOS = ('cerca_playa', 'vista_mar', 'vista_lago', 'credito_directo')

# Pedidas por Jorge y NO publicadas a proposito. Si alguna deja de estar vacia,
# se mueve a _FICHAS y listo.
NO_PUBLICADAS = {
    'parcela-con-casa': 'Leonardo: "parcelas con casa, nada por ahora" (01-10-2026).',
    'parcela-rural':    'Jorge la pide; Leonardo no la nombro. Falta su criterio.',
}

SLUGS = tuple(_FICHAS)


def filtro(slug):
    """El Q() que define la caracteristica. None si el slug no existe."""
    return {
        # --- derivadas: salen de datos que Leonardo ya edita en la ficha ---
        'parcelas-sur-de-chile':   Q(region='los_lagos'),
        'parcelas-baratas':        Q(moneda='CLP', precio__gt=0, precio__lte=10_000_000),
        'parcela-con-rol-propio':  Q(rol_propio=True),
        'parcela-con-agua-y-luz':  Q(tiene_agua=True, tiene_luz=True),
        # --- marcadas por el ---
        'parcela-con-credito-directo': Q(credito_directo=True),
        'parcela-vista-al-mar':        Q(vista_mar=True),
        'parcela-vista-al-lago':       Q(vista_lago=True),
        'parcela-en-la-playa':         Q(cerca_playa=True),
        # --- el catalogo completo con otro titulo ---------------------------
        # Leonardo dijo "todas" para las dos. No filtran nada a proposito: lo
        # que aportan es el H1 y el texto, que es lo que se busca en Google.
        'parcela-de-campo':  Q(),
        'parcela-de-agrado': Q(),
    }.get(slug)


def ficha(slug):
    """(h1, title, bajada) o None."""
    return _FICHAS.get(slug)


# -------------------------------------------------------------------------
# EL TEXTO PROPIO DE CADA PAGINA
#
# Medido en vivo el 04-10: parcela-de-campo y parcela-de-agrado eran 96%
# identicas, y con-rol-propio 87%. Las tres muestran las mismas 116 parcelas,
# asi que cambiando solo el H1 y una bajada Google las lee como la misma pagina
# tres veces: elige una, degrada las otras y compiten entre ellas.
#
# Cada bloque responde la pregunta que trae quien busca ese termino. Son datos
# del marco legal chileno (DL 3.516), publicos y verificables -- NO afirmaciones
# sobre el negocio de Leonardo. Sin plazos, precios ni promesas suyas, igual que
# el resto del sitio.
_EXPLICACIONES = {
    'parcela-de-agrado': [
        ('¿Qué es una parcela de agrado?',
         'Es un terreno rústico subdividido al amparo del Decreto Ley 3.516, que '
         'permite dividir predios agrícolas en lotes de 5.000 m² (media hectárea) '
         'como mínimo. Esa superficie es el piso legal: no existen parcelas de '
         'agrado más chicas. Se compran para construir una casa de descanso o '
         'para vivir fuera de la ciudad, manteniendo el uso agrícola del suelo.'),
        ('¿En qué se diferencia de un sitio urbano?',
         'Una parcela de agrado está fuera del límite urbano, así que no llega '
         'con urbanización municipal: el agua suele ser de pozo o puntera y la '
         'electricidad se empalma a la red rural. A cambio, el precio por metro '
         'es mucho menor y no hay restricciones de constructibilidad urbana.'),
        ('¿Qué conviene revisar antes de comprar?',
         'Que el loteo esté aprobado por el SAG, que la parcela tenga rol propio '
         'o esté en trámite, cómo llega el agua y la luz, y qué dice la '
         'servidumbre de acceso. Son los puntos que definen si vas a poder '
         'escriturar y construir sin sorpresas.'),
    ],
    'parcela-de-campo': [
        ('¿Qué es una parcela de campo?',
         '"Parcela de campo" es como se le dice en el día a día a lo que la ley '
         'llama parcela de agrado: un terreno rural de media hectárea o más, '
         'fuera del límite urbano. Los dos nombres se usan para lo mismo, así '
         'que no hay que buscar dos cosas distintas.'),
        ('¿Para qué se usan?',
         'Para casa de fin de semana, para irse a vivir al campo, para plantar o '
         'para dejarlas como inversión mientras la zona se valoriza. El uso '
         'manda sobre lo que conviene mirar: quien va a vivir ahí necesita '
         'resolver agua y luz antes que nada; quien invierte mira la plusvalía '
         'del sector y el acceso.'),
        ('¿Se puede construir?',
         'Sí, con permiso de la Dirección de Obras de la municipalidad. Al estar '
         'en suelo rural hay limitaciones de superficie construida y de '
         'subdivisión posterior, que es justamente lo que protege el entorno y '
         'lo que hace que el campo siga siendo campo.'),
    ],
    'parcela-con-rol-propio': [
        ('¿Qué significa que tenga rol propio?',
         'Que el Servicio de Impuestos Internos ya le asignó un número de rol a '
         'esa parcela en particular, separado del predio madre. Es la prueba de '
         'que la subdivisión está hecha y registrada, no en trámite.'),
        ('¿Por qué importa al momento de comprar?',
         'Sin rol propio la parcela todavía es parte de un terreno más grande, y '
         'la escritura queda sujeta a que la subdivisión termine. Con rol propio '
         'se escritura a tu nombre de inmediato y puedes pagar tus propias '
         'contribuciones, pedir empalmes y tramitar permisos sin depender del '
         'vendedor.'),
    ],
    'parcela-con-agua-y-luz': [
        ('¿Qué significa "con agua y luz" en una parcela?',
         'Que el terreno ya tiene resuelto el suministro: agua por pozo, puntera '
         'o APR según el sector, y electricidad empalmada a la red. En suelo '
         'rural eso no viene por defecto y es lo que más encarece habilitar una '
         'parcela después de comprarla.'),
        ('¿Puedo construir de inmediato?',
         'Tener agua y luz resuelve el servicio, pero construir igual requiere '
         'el permiso de la Dirección de Obras. Lo que te ahorras es el costo y '
         'la espera de habilitar los suministros desde cero.'),
    ],
    'parcelas-baratas': [
        ('¿Por qué hay parcelas tan económicas?',
         'El precio de una parcela depende de la zona, del acceso, de si tiene '
         'agua y luz, y de si ya está subdividida con rol propio. Una parcela '
         'más económica suele estar más lejos de la ciudad o tener alguno de '
         'esos puntos pendientes; no significa que el terreno sea peor.'),
        ('¿Qué revisar en una parcela de bajo precio?',
         'Lo mismo que en cualquier otra: loteo aprobado, rol propio o en '
         'trámite, cómo llega el agua y la luz, y la servidumbre de acceso. Si '
         'alguno está pendiente, conviene saber cuánto cuesta resolverlo antes '
         'de comparar precios.'),
    ],
    'parcelas-sur-de-chile': [
        ('¿Qué tiene de particular comprar en el sur?',
         'El sur tiene más agua y vegetación nativa, y los terrenos suelen ser '
         'más baratos por metro que en la zona central. A cambio, el clima pide '
         'otro tipo de construcción y conviene mirar el drenaje del terreno y el '
         'estado del camino en invierno.'),
    ],
}


def explicacion(slug):
    """Los bloques de texto propios de la pagina, o lista vacia."""
    return _EXPLICACIONES.get(slug, [])
