# -*- coding: utf-8 -*-
"""El contenido de las 12 landings por caracteristica (Jorge Urzua, 05-10-2026).

Reemplaza los textos cortos del 04-10 por los del documento: traen el "que
considerar antes de comprar" y tres preguntas por pagina, que es lo que las
hace distintas entre si. Las fichas (slug, filtro, que se publica y que no)
siguen viviendo en caracteristicas.py; aca va solo el texto.

LA PAGINA DE LA PLAYA NO LLEVA EL TEXTO DEL DOCUMENTO
-----------------------------------------------------
Es la unica excepcion y es deliberada. El documento propone:

    H1    "Parcela en la playa"
    meta  "Cumple el sueño de tener tu terreno frente al mar"
    texto "Despertar con el sonido de las olas dejo de ser un lujo..."

Y Leonardo dijo textual el 01-10 (citado en caracteristicas.py):

    "parcelas en la playa NO TENGO, pero hay algunas relativamente cerca,
     30 min"

Publicar eso es prometer algo que el catalogo no cumple, y lo paga el cliente
que llega, mira y se va. El SLUG se mantiene (es lo que Google indexa y lo que
Jorge trabaja), pero el H1 y el texto dicen la verdad, con los minutos. La
keyword se trabaja igual y nadie llega enganado.

Esa decision ya estaba tomada el 04-10 y este documento no trae un dato nuevo
que la cambie: la cambia Leonardo el dia que tenga una parcela en la playa.
"""

# slug -> {title, meta, intro, considerar, preguntas}
# `preguntas` alimenta el FAQPage, asi que son las que se VEN en la pagina.
CONTENIDO = {
    'parcela-en-la-playa': {
        'title': 'Parcelas cerca de la playa en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas a menos de 30 minutos del mar en Chile, con rol propio y '
            'financiamiento. Compara proyectos cerca de la playa y agenda tu visita.',
        'keyword': 'terreno playa (880/mes)',
        'intro': [
            'Tener un terreno propio a pasos del mar es posible sin pagar primera línea. '
             'Estas parcelas están a menos de 30 minutos de la costa: cerca para ir a la '
             'playa el fin de semana, y a un valor muy distinto al de un terreno frente al '
             'mar.',
            'En Punto Parcelas reunimos proyectos cercanos al litoral, con rol propio y '
             'opciones de financiamiento. Compara ubicación, superficie y precio, y agenda '
             'una visita para ver a qué distancia real queda el mar.',
        ],
        'considerar': [
            'Acceso y conectividad: revisa el estado del camino y la distancia real a la '
             'ciudad más cercana.',
            'Agua y luz: confirma la factibilidad (pozo, APR o red), clave en sectores '
             'costeros.',
            'Uso de suelo y rol propio: asegúrate de que permita construir y tenga rol '
             'individual.',
            'Entorno y orientación: la vista, el viento y la cercanía al mar marcan la '
             'diferencia.',
        ],
        'preguntas': [
            ('¿Estas parcelas están en la playa?',
             'No tenemos parcelas con salida directa a la playa. Las que aparecen acá están '
              'a menos de 30 minutos en auto del mar, que es lo que permite ir a la costa el '
              'fin de semana sin pagar el valor de un terreno costero.'),
            ('¿Cuánto cuesta una parcela en la playa?',
             'El valor depende de la región, la cercanía al mar y los servicios. En Punto '
              'Parcelas hay alternativas para distintos presupuestos, muchas con '
              'financiamiento directo. Consulta el precio vigente en cada proyecto.'),
            ('¿En qué zonas de Chile hay terrenos en la playa?',
             'Principalmente en el litoral central y la costa de O’Higgins, el Maule y Los '
              'Lagos. Revisa los proyectos disponibles y filtra por región.'),
        ],
    },
    'parcelas-sur-de-chile': {
        'title': 'Parcelas y terrenos en el sur de Chile en venta | Punto Parcelas',
        'meta': 'Parcelas en el sur de Chile en venta: lagos, bosque nativo y naturaleza. '
            'Terrenos con rol propio y financiamiento. Compara proyectos y agenda tu visita.',
        'keyword': 'terrenos sur de chile (720/mes)',
        'intro': [
            'El sur de Chile es sinónimo de lagos, bosque nativo y aire puro. Una parcela en '
             'el sur es la puerta de entrada a ese estilo de vida: un lugar propio para '
             'desconectarte, construir tu refugio o invertir en una de las zonas con mayor '
             'demanda turística del país.',
            'En Punto Parcelas reunimos terrenos en el sur de Chile en regiones como Los '
             'Lagos, Los Ríos y La Araucanía. Compara ubicación, superficie, vistas y '
             'financiamiento, y elige la parcela que mejor se adapta a tu proyecto.',
        ],
        'considerar': [
            'Clima y suelo: el sur es lluvioso; revisa drenaje y accesos en invierno.',
            'Agua y luz: confirma factibilidad, muchas parcelas usan pozo o APR.',
            'Entorno: cercanía a lagos, ríos o bosque nativo suma plusvalía y disfrute.',
            'Conectividad: distancia a la ciudad y al aeropuerto más cercano.',
        ],
        'preguntas': [
            ('¿Por qué invertir en una parcela en el sur de Chile?',
             'Por la combinación de naturaleza, turismo creciente y plusvalía. Son terrenos '
              'muy buscados para casa de descanso, arriendo vacacional o inversión a largo '
              'plazo.'),
            ('¿En qué regiones del sur hay parcelas disponibles?',
             'Principalmente en Los Lagos (Frutillar, Puerto Varas, Osorno), Los Ríos y La '
              'Araucanía. Filtra por región para ver los proyectos.'),
            ('¿Tienen rol propio y financiamiento?',
             'La mayoría cuenta con rol individual y varias ofrecen financiamiento directo. '
              'Revisa cada ficha.'),
        ],
    },
    'parcelas-baratas': {
        'title': 'Parcelas baratas en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas baratas en venta en Chile desde valores accesibles, con crédito directo '
            'y pie bajo. Compara terrenos económicos y empieza a invertir hoy.',
        'keyword': 'vendo terreno 2 millones (480/mes)',
        'intro': [
            'Tener un terreno propio no tiene por qué ser caro. Las parcelas baratas son la '
             'forma más accesible de dar el primer paso: invertir en tierra, asegurar '
             'plusvalía y construir a tu ritmo, sin descapitalizarte.',
            'En Punto Parcelas reunimos las parcelas más económicas de Chile, muchas con '
             'crédito directo y pie bajo. Compara precio, ubicación y condiciones, y '
             'encuentra el terreno que cabe en tu presupuesto.',
        ],
        'considerar': [
            'Precio total y financiamiento: compara el valor final, el pie y las cuotas, no '
             'solo el titular.',
            'Servicios: una parcela barata puede no tener agua o luz aún; confirma la '
             'factibilidad.',
            'Rol y documentación: verifica rol propio y papeles al día antes de comprar.',
            'Ubicación: el precio bajo suele ir de la mano con mayor distancia; evalúa el '
             'acceso.',
        ],
        'preguntas': [
            ('¿Qué tan barata puede ser una parcela?',
             'Hay terrenos desde pocos millones de pesos, sobre todo con crédito directo y '
              'pie bajo. El valor depende de la región, la superficie y los servicios. '
              'Consulta los precios vigentes.'),
            ('¿Las parcelas baratas tienen crédito directo?',
             'Muchas sí, con pie accesible y cuotas sin banco. Es la vía más usada para '
              'comprar terreno económico en Chile.'),
            ('¿Una parcela barata es buena inversión?',
             'Sí, si tiene rol propio, documentación al día y buen acceso. La tierra tiende '
              'a revalorizarse, y comprar a bajo valor mejora tu rentabilidad.'),
        ],
    },
    'parcela-de-campo': {
        'title': 'Parcelas de campo en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas de campo en venta en Chile: naturaleza, tranquilidad y aire libre. '
            'Terrenos con rol propio y financiamiento. Compara proyectos y agenda tu visita.',
        'keyword': 'parcelas campo (320/mes)',
        'intro': [
            'Cambiar el ruido de la ciudad por el canto de los pájaros es más posible de lo '
             'que crees. Una parcela de campo te da espacio, aire libre y tranquilidad para '
             'construir tu casa, cultivar o simplemente desconectarte los fines de semana.',
            'En Punto Parcelas reunimos parcelas de campo en todo Chile, con rol propio y '
             'financiamiento. Compara superficie, entorno y servicios, y elige el terreno que '
             'se adapta a tu proyecto de vida.',
        ],
        'considerar': [
            'Uso de suelo: confirma que permita construir vivienda o casa de agrado.',
            'Agua y luz: revisa factibilidad de pozo, APR y red eléctrica.',
            'Acceso: estado del camino y distancia a servicios básicos.',
            'Topografía: terreno plano o con lomaje suave facilita construir.',
        ],
        'preguntas': [
            ('¿Qué es una parcela de campo?',
             'Es un terreno rural con rol propio, pensado para vivir, descansar o invertir '
              'en un entorno natural, lejos del ruido de la ciudad. Suele tener superficies '
              'desde 5.000 m².'),
            ('¿Puedo construir en una parcela de campo?',
             'En general sí, cumpliendo la normativa y el uso de suelo de la comuna. Cada '
              'ficha indica las condiciones del proyecto.'),
            ('¿Dónde hay parcelas de campo en Chile?',
             'En prácticamente todas las regiones, desde Coquimbo hasta Los Lagos. Filtra '
              'por región o comuna para ver las disponibles.'),
        ],
    },
    'parcela-vista-al-mar': {
        'title': 'Parcelas con vista al mar en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas con vista al mar en venta en Chile. Terrenos con panorámica al océano, '
            'rol propio y financiamiento. Compara proyectos y agenda tu visita.',
        'keyword': 'terrenos con vista al mar (260/mes)',
        'intro': [
            'Pocas cosas se comparan con una puesta de sol sobre el océano desde tu propia '
             'tierra. Una parcela con vista al mar une lo mejor de dos mundos: el valor de un '
             'terreno propio y una panorámica que no pasa de moda ni pierde plusvalía.',
            'En Punto Parcelas reunimos terrenos con vista al mar en distintos puntos de la '
             'costa de Chile. Compara ubicación, orientación de la vista, superficie y '
             'financiamiento, y elige la parcela con la mejor panorámica para ti.',
        ],
        'considerar': [
            'Orientación de la vista: confirma que la panorámica al mar sea despejada y '
             'permanente.',
            'Topografía: las parcelas en altura suelen tener mejor vista; revisa la '
             'pendiente para construir.',
            'Servicios y acceso: agua, luz y camino, clave en sectores de cerro costero.',
            'Rol propio: verifica rol individual y uso de suelo.',
        ],
        'preguntas': [
            ('¿Qué es una parcela con vista al mar?',
             'Es un terreno, normalmente en altura o primera línea de cerro costero, con '
              'panorámica despejada al océano y rol propio. Ideal para casa de descanso o '
              'inversión.'),
            ('¿La vista al mar sube el valor del terreno?',
             'Sí. La vista es un atributo escaso y muy valorado, por lo que estas parcelas '
              'suelen tener mejor plusvalía y demanda de arriendo.'),
            ('¿Dónde encuentro terrenos con vista al mar?',
             'En el litoral central y la costa de O’Higgins y el Maule, principalmente. '
              'Revisa los proyectos y filtra por región.'),
        ],
    },
    'parcela-de-agrado': {
        'title': 'Parcelas de agrado en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas de agrado en venta en Chile: terreno propio para tu casa de descanso o '
            'vida de campo. Rol propio y financiamiento. Compara proyectos y visita.',
        'keyword': 'parcelas de agrado (210/mes)',
        'intro': [
            'Una parcela de agrado es, literalmente, un terreno para disfrutar: pensado para '
             'construir tu casa de descanso, pasar los fines de semana en familia o darte el '
             'gusto de tener tu propio pedazo de campo con todas las comodidades.',
            'En Punto Parcelas reunimos parcelas de agrado en distintas regiones, con rol '
             'propio y financiamiento. Compara entorno, superficie y servicios, y elige la '
             'que mejor se ajusta a tu estilo de vida.',
        ],
        'considerar': [
            'Entorno: vistas, bosque, agua y tranquilidad son parte del valor de agrado.',
            'Servicios: factibilidad de agua y luz para habitarla cómodamente.',
            'Uso de suelo: que permita construir vivienda de agrado.',
            'Rol propio y documentación al día.',
        ],
        'preguntas': [
            ('¿Qué es una parcela de agrado?',
             'Es un terreno de campo con rol propio, destinado a vivienda de descanso o '
              'recreación más que a producción agrícola. Combina naturaleza y comodidad.'),
            ('¿En qué se diferencia de una parcela rural?',
             'La de agrado está pensada para vivir y disfrutar, con mejor entorno y '
              'servicios; la rural tiene un enfoque más productivo o agrícola.'),
            ('¿Tienen financiamiento?',
             'Varias cuentan con crédito directo o pie accesible. Revisa cada proyecto.'),
        ],
    },
    'parcela-con-credito-directo': {
        'title': 'Parcelas con crédito directo en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas con crédito directo en venta en Chile: compra tu terreno sin banco, con '
            'pie bajo y cuotas. Compara proyectos con financiamiento directo y empieza hoy.',
        'keyword': 'parcelas con crédito directo (170/mes)',
        'intro': [
            'Comprar tierra sin depender de la aprobación de un banco es posible. Una '
             'parcela con crédito directo te permite reservar tu terreno con un pie accesible '
             'y pagar el saldo en cuotas, directamente con el vendedor, sin trámites '
             'bancarios eternos.',
            'En Punto Parcelas reunimos los proyectos que ofrecen crédito directo en todo '
             'Chile. Compara pie, número de cuotas y condiciones, y asegura tu parcela aunque '
             'hoy no califiques para un crédito hipotecario.',
        ],
        'considerar': [
            'Pie y cuotas: revisa el monto inicial, la cantidad de cuotas y si hay interés o '
             'reajuste.',
            'Contrato: que quede claro el traspaso y la escrituración al terminar de pagar.',
            'Rol propio y documentación al día.',
            'Respaldo del vendedor: trayectoria y proyectos entregados.',
        ],
        'preguntas': [
            ('¿Qué es el crédito directo en una parcela?',
             'Es un financiamiento que entrega el mismo vendedor, sin banco: pagas un pie y '
              'el saldo en cuotas. Facilita comprar terreno a quienes no acceden a crédito '
              'hipotecario.'),
            ('¿Qué pie piden normalmente?',
             'Varía por proyecto; hay opciones con pie bajo e incluso pie cero. Revisa las '
              'condiciones de cada parcela.'),
            ('¿Cuándo se escritura la parcela?',
             'Por lo general al terminar de pagar las cuotas, según el contrato. Confirma '
              'este punto antes de reservar.'),
        ],
    },
    'parcela-vista-al-lago': {
        'title': 'Parcelas con vista al lago en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas con vista al lago en venta en Chile. Terrenos con panorámica a lagos '
            'del sur, rol propio y financiamiento. Compara proyectos y agenda tu visita.',
        'keyword': 'parcelas vista al lago (50/mes)',
        'intro': [
            'Imagina abrir la ventana y encontrarte con un lago reflejando la cordillera. '
             'Una parcela con vista al lago es uno de los terrenos más codiciados del sur de '
             'Chile, por su belleza, su tranquilidad y su alta plusvalía.',
            'En Punto Parcelas reunimos parcelas con vista al lago en regiones como Los '
             'Lagos y Los Ríos. Compara ubicación, orientación de la vista y financiamiento, '
             'y elige tu lugar frente al agua.',
        ],
        'considerar': [
            'Vista despejada: confirma que la panorámica al lago sea permanente.',
            'Acceso al agua: pregunta si el proyecto tiene acceso o bajada al lago.',
            'Servicios: factibilidad de agua y luz.',
            'Rol propio y uso de suelo.',
        ],
        'preguntas': [
            ('¿Dónde hay parcelas con vista al lago en Chile?',
             'Principalmente en el sur: lagos Llanquihue, Rupanco, Ranco y Villarrica, entre '
              'otros. Filtra por región para verlas.'),
            ('¿Tienen acceso al lago?',
             'Algunos proyectos ofrecen acceso o bajada comunitaria al lago; otros solo la '
              'vista. Revisa cada ficha.'),
            ('¿Por qué tienen buena plusvalía?',
             'Porque la vista al lago es un atributo escaso y muy demandado para turismo y '
              'segunda vivienda.'),
        ],
    },
    'parcela-con-rol-propio': {
        'title': 'Parcelas con rol propio en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas con rol propio en venta en Chile: terreno individual, escriturable y '
            'seguro. Rol único y financiamiento. Compara proyectos y agenda tu visita.',
        'keyword': 'parcelas con rol propio (50/mes)',
        'intro': [
            'El rol propio es una de las garantías más importantes al comprar tierra. Una '
             'parcela con rol propio significa que tu terreno es una unidad independiente '
             'ante el SII, con su propio rol de avalúo, lista para escriturar solo a tu '
             'nombre.',
            'En Punto Parcelas reunimos parcelas con rol propio en todo Chile, para que '
             'compres con seguridad jurídica. Compara ubicación, superficie y financiamiento, '
             'y elige un terreno 100% individual.',
        ],
        'considerar': [
            'Rol individual: verifica que el rol sea único y esté a nombre del proyecto, no '
             'en copropiedad.',
            'Documentación: escritura, certificados SAG, SII y Conservador al día.',
            'Deslindes definidos y plano aprobado.',
            'Factibilidad de servicios y acceso.',
        ],
        'preguntas': [
            ('¿Qué significa que una parcela tenga rol propio?',
             'Que es una unidad independiente con su propio rol de avalúo en el SII, '
              'escriturable individualmente. Da mayor seguridad jurídica que comprar en '
              'copropiedad o por derechos.'),
            ('¿Por qué es importante el rol propio?',
             'Porque te permite ser dueño exclusivo de tu terreno, acceder a servicios a tu '
              'nombre y vender o heredar sin depender de otros copropietarios.'),
            ('¿Todas las parcelas de Punto Parcelas tienen rol propio?',
             'La gran mayoría sí. Cada ficha indica el estado del rol y la documentación.'),
        ],
    },
    'parcela-con-agua-y-luz': {
        'title': 'Parcelas con agua y luz en venta en Chile | Punto Parcelas',
        'meta': 'Parcelas con agua y luz en venta en Chile: terreno con factibilidad de '
            'servicios, listo para construir. Rol propio y financiamiento. Compara proyectos '
            'y visita.',
        'keyword': 'parcelas con agua (50/mes)',
        'intro': [
            'Agua y luz son lo primero que se pregunta al comprar un terreno, y con razón: '
             'definen qué tan rápido puedes construir y habitar. Una parcela con agua y luz '
             'te ahorra tiempo, costos y sorpresas, porque los servicios esenciales ya están '
             'resueltos o con factibilidad confirmada.',
            'En Punto Parcelas reunimos parcelas con agua y luz en distintas regiones de '
             'Chile, con rol propio y financiamiento. Compara el tipo de factibilidad, la '
             'superficie y el entorno, y elige un terreno listo para tu proyecto.',
        ],
        'considerar': [
            'Tipo de agua: pozo, APR o red; confirma caudal y factibilidad real.',
            'Electricidad: red disponible o postación cercana, y el costo de empalme.',
            'Documentación de factibilidad por escrito.',
            'Rol propio y acceso.',
        ],
        'preguntas': [
            ('¿Qué significa que una parcela tenga agua y luz?',
             'Que cuenta con los servicios básicos resueltos o con factibilidad confirmada: '
              'agua (pozo, APR o red) y electricidad. Esto acelera y abarata la construcción.'),
            ('¿Qué conviene revisar sobre el agua?',
             'El tipo de abastecimiento (pozo, APR o red), el caudal y que exista '
              'factibilidad por escrito. En el campo es el punto más importante.'),
            ('¿Dónde encuentro parcelas con agua y luz?',
             'En proyectos de varias regiones. Cada ficha detalla el estado de los '
              'servicios; filtra por los que ya tienen factibilidad.'),
        ],
    },
}
