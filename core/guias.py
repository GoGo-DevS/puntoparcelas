# -*- coding: utf-8 -*-
"""Las 14 guias informacionales que mando Jorge Urzua el 05-10-2026.

POR QUE EXISTE ESTA SECCION
---------------------------
El sitio tenia 75 URLs y TODAS eran de catalogo: region, comuna y ficha de
proyecto. Ni una sola respondia una pregunta. Quien busca "que hacer en Puerto
Varas" todavia no esta comprando, pero esta eligiendo zona -- y quien elige
zona es quien despues compra. Ese trafico hoy se lo llevan los portales de
turismo.

Son 15.890 busquedas/mes sobre 80 keywords agrupadas en 14 paginas: una por
localidad y no una por patron, porque "panoramas en Osorno" y "lugares
turisticos de Osorno" son la misma intencion escrita distinto, y separarlas
daria seis paginas compitiendo por el mismo contenido.

Va en /guias/ y no en /blog/ a proposito: es contenido permanente, no
publicaciones con fecha.

EL ENLACE SE RESUELVE CONTRA LA BASE, NO SE ESCRIBE A MANO
----------------------------------------------------------
Esto es lo unico que se aparta del documento, y es por un hecho medido el
06-10-2026 contra el sitio en vivo. El documento afirma:

    "Las doce localidades tienen comuna publicada en el catalogo, asi que el
     enlace de bajada existe en todas."

Es falso. Tres destinos dan 404 hoy:

    /catalogo/araucania/villarrica/   404   (la guia de Villarrica)
    /catalogo/araucania/              404   (su region TAMPOCO existe)
    /catalogo/valparaiso/algarrobo/   404   (la guia de Algarrobo)

Y no es un error de Jorge ni un bug del sitio: una region o comuna sin parcelas
devuelve 404 A PROPOSITO desde el 22-09 (ver tests_regiones_vacias). Si Leonardo
no tiene ninguna parcela en Villarrica, esa pagina no debe existir.

Por eso los enlaces del cuerpo NO son href fijos. Cada uno se resuelve al
dibujar la pagina, con esta cascada:

    comuna con parcelas          ->  /catalogo/<region>/<comuna>/
    si no, region con parcelas   ->  /catalogo/<region>/
    si no                        ->  /catalogo/

Asi, el dia que Leonardo cargue una parcela en Villarrica el enlace aparece
solo, y mientras tanto no se publica ni un 404. Es la misma regla que ya usan
las ciudades y las caracteristicas.

EL TEXTO ES EL DE JORGE, SIN REESCRIBIR
---------------------------------------
Se extrajo del .docx conservando los estilos de Word (Heading2 = H2,
ListParagraph = vinieta); no se transcribio a mano, porque una copia manual de
50.000 caracteres mete errores que despues nadie revisa.
"""

# Cada guia: h1/title/meta son la ficha SEO; `cuerpo` es [(etiqueta, texto)]
# donde la etiqueta sale del estilo del documento:
#     h2 = Heading2     p = parrafo     li = vinieta
#
# Dentro del texto, [[anchor|/ruta/]] es un enlace interno que se resuelve
# contra la base al dibujar la pagina. Ver el bloque de arriba.
GUIAS = {
    'que-hacer-en-puerto-varas': {
        'h1': 'Qué hacer en Puerto Varas: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Puerto Varas | Punto Parcelas',
        'meta': 'Qué hacer en Puerto Varas: panoramas, lugares turísticos, clima y cómo llegar. '
            'La guía de la ciudad a orillas del lago Llanquihue.',
        'keyword': 'que hacer en puerto varas  (2.400/mes)',
        'secundarias': 'panoramas en puerto varas (480) · clima de puerto varas (210) · como llegar a '
            'puerto varas (320) · lugares turisticos de puerto varas (70) · vivir en puerto '
            'varas (90)',
        'volumen': '3.570 búsquedas/mes',
        'cuerpo': [
            ('p', 'Puerto Varas se mira dos veces: la primera por el lago, la segunda por los dos '
             'volcanes que lo cierran al otro lado.'),
            ('p', 'La ciudad está en la orilla sur del lago Llanquihue, con el Osorno y el Calbuco '
             'enfrente, y esa postal explica buena parte de su atractivo turístico y también '
             'inmobiliario.'),
            ('p', 'Su casco antiguo guarda las casas de madera de la colonización alemana, varias '
             'declaradas monumento nacional, y alrededor hay lago, río y parque nacional a '
             'menos de una hora.'),
            ('p', 'Es, además, la zona donde las búsquedas de parcelas del sur se concentran, así '
             'que mucha gente llega de paseo y vuelve a mirar terrenos. Las parcelas '
             'disponibles están en [[Parcelas en Puerto '
             'Varas|/catalogo/los-lagos/puerto-varas/]].'),
            ('h2', 'Panoramas en Puerto Varas para un fin de semana'),
            ('p', 'El paseo costanera y la playa Hermosa funcionan todo el año, incluso cuando el '
             'clima no acompaña. Para un día completo, los Saltos del Petrohué quedan a unos '
             '60 kilómetros por un camino pavimentado y bien señalizado.'),
            ('p', 'En el lago se hace kayak, stand up paddle y navegación. Hacia la cordillera, el '
             'centro de esquí del volcán Osorno opera en invierno y en verano abre los '
             'miradores con vista al Llanquihue.'),
            ('p', 'Quien viaja con tiempo suele combinar la ciudad con Petrohué, el lago Todos los '
             'Santos y la ruta hacia Ensenada, que es el tramo más fotografiado de la zona.'),
            ('h2', 'Lugares turísticos de Puerto Varas que vale la pena'),
            ('p', 'La iglesia del Sagrado Corazón de Jesús, construida en madera a comienzos del '
             'siglo XX, es el punto de referencia del centro y está a pasos de la costanera.'),
            ('p', 'El Parque Nacional Vicente Pérez Rosales, el más antiguo de Chile, se entra por '
             'Petrohué y concentra los saltos, el lago Todos los Santos y los senderos al '
             'volcán.'),
            ('p', 'A 30 kilómetros, Frutillar completa el circuito con su Teatro del Lago y el '
             'museo de la colonización alemana.'),
            ('h2', 'Clima de Puerto Varas: qué esperar en cada estación'),
            ('p', 'Es clima templado lluvioso, con precipitación repartida en todo el año y un '
             'verano más seco entre enero y marzo. Llueve de verdad y conviene asumirlo al '
             'planificar.'),
            ('p', 'Los veranos son frescos, con máximas que rara vez pasan los 25 grados, y los '
             'inviernos fríos y húmedos, con mínimas cerca de cero y heladas en el sector '
             'alto.'),
            ('p', 'Esa humedad constante es la que mantiene el verde todo el año, y también la que '
             'obliga a revisar el drenaje del suelo cuando se compra terreno.'),
            ('h2', 'Cómo llegar a Puerto Varas'),
            ('p', 'Por tierra, la Ruta 5 Sur pasa por el borde de la ciudad: son unos 1.000 '
             'kilómetros desde Santiago y unos 20 desde Puerto Montt.'),
            ('p', 'En avión, el aeropuerto El Tepual de Puerto Montt recibe vuelos diarios desde '
             'Santiago y queda a unos 40 minutos en auto. Hay transfer compartido y arriendo '
             'de vehículos en el mismo terminal.'),
            ('p', 'En bus, los servicios desde Santiago tardan entre 12 y 14 horas, y desde Puerto '
             'Montt hay recorridos cada pocos minutos.'),
            ('h2', 'Vivir en Puerto Varas'),
            ('p', 'La ciudad tiene colegios, clínica, supermercados y servicios, lo que la '
             'diferencia de un balneario de temporada: funciona los doce meses del año.'),
            ('p', 'El costo de vida es más alto que en el promedio del sur, sobre todo en '
             'vivienda, y eso empuja a muchos a buscar terreno en el camino a Ensenada, hacia '
             'Llanquihue o hacia Puerto Octay.'),
            ('p', 'Si estás mirando la zona completa, el catálogo de [[Parcelas en Los '
             'Lagos|/catalogo/los-lagos/]] reúne todas las comunas con proyectos disponibles.'),
            ('p', 'Para comparar con la localidad vecina, revisa también [[qué hacer en '
             'Osorno|/guias/que-hacer-en-osorno/]].'),
            ('p', 'Cuando ya tengas clara la zona, revisa todos los [[terrenos en venta|/]] '
             'disponibles en el país y filtra por región para encontrar tu parcela.'),
        ],
    },
    'que-hacer-en-chillan': {
        'h1': 'Qué hacer en Chillán: panoramas, termas, clima y cómo llegar',
        'title': 'Qué hacer en Chillán | Punto Parcelas',
        'meta': 'Qué hacer en Chillán: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'de la capital de Ñuble y los Nevados de Chillán.',
        'keyword': 'que hacer en chillan  (880/mes)',
        'secundarias': 'panoramas en chillan (480) · clima de chillan (480) · como llegar a chillan '
            '(390) · lugares turisticos de chillan (110) · vivir en chillan (10)',
        'volumen': '2.350 búsquedas/mes',
        'cuerpo': [
            ('p', 'Chillán tiene dos caras que se visitan por separado: la ciudad histórica y la '
             'cordillera con termas y nieve a 80 kilómetros.'),
            ('p', 'Es la capital de la región de Ñuble y el centro de servicios de todo el valle, '
             'con una historia que la hizo reconstruirse varias veces después de terremotos.'),
            ('p', 'Acá nació Bernardo O\'Higgins, y el Mercado de Chillán es uno de los más '
             'conocidos del país por su cocina y su artesanía en mimbre.'),
            ('p', 'Hacia la cordillera está el complejo de los Nevados de Chillán, que funciona '
             'como centro de esquí en invierno y como zona de termas y senderos el resto del '
             'año. Los proyectos de la comuna están en [[Parcelas en '
             'Chillán|/catalogo/nuble/chillan/]].'),
            ('h2', 'Panoramas en Chillán durante todo el año'),
            ('p', 'El Mercado de Chillán es el punto de partida obligado: longaniza, queso de '
             'Chanco y mimbre de Chimbarongo en un mismo lugar, con cocinerías abiertas al '
             'mediodía.'),
            ('p', 'En invierno, los Nevados de Chillán ofrecen esquí y snowboard con una de las '
             'temporadas más largas de Chile. En verano, el mismo complejo abre piscinas '
             'termales, canopy y senderos.'),
            ('p', 'Más cerca, la Escuela México guarda los murales de David Alfaro Siqueiros y '
             'Xavier Guerrero, pintados como regalo tras el terremoto de 1939.'),
            ('h2', 'Lugares turísticos de Chillán y sus alrededores'),
            ('p', 'La Catedral de Chillán, con sus arcos parabólicos antisísmicos, y la Plaza de '
             'Armas ordenan el centro histórico.'),
            ('p', 'A unos 30 kilómetros, el Valle Las Trancas concentra alojamiento y restaurantes '
             'camino a la cordillera, y es la base habitual para subir a las termas.'),
            ('p', 'El Parque Monumental Bernardo O\'Higgins, en Chillán Viejo, tiene un mural de 60 '
             'metros dedicado al prócer.'),
            ('h2', 'Clima de Chillán: veranos secos, inviernos lluviosos'),
            ('p', 'Es clima mediterráneo con estación seca marcada. Los veranos son calurosos, con '
             'máximas que superan los 30 grados en enero y febrero, y bastante secos.'),
            ('p', 'El invierno concentra la lluvia entre mayo y agosto, con mínimas cercanas a '
             'cero y heladas frecuentes en el valle.'),
            ('p', 'La diferencia con la cordillera es fuerte: a la altura de las termas nieva '
             'varios meses al año, mientras en la ciudad la nieve es excepcional.'),
            ('h2', 'Cómo llegar a Chillán'),
            ('p', 'Por la Ruta 5 Sur son unos 400 kilómetros desde Santiago, alrededor de cuatro '
             'horas y media en auto.'),
            ('p', 'En bus hay salidas frecuentes desde el Terminal Alameda y servicios nocturnos. '
             'El terminal de Chillán queda en el centro.'),
            ('p', 'También llega el tren: el servicio desde la Estación Central de Santiago hace '
             'el recorrido con paradas intermedias y es una alternativa cómoda para quien no '
             'viaja en auto.'),
            ('h2', 'Vivir en Chillán'),
            ('p', 'Es una ciudad de tamaño medio con universidades, hospital regional y comercio '
             'consolidado, y eso la hace funcional todo el año sin depender del turismo.'),
            ('p', 'El valor del suelo es bastante más bajo que en el litoral central o la zona de '
             'los lagos, y por eso aparece seguido en las búsquedas de terreno con superficie '
             'grande.'),
            ('p', 'El catálogo completo de la zona está en [[parcelas chillan|/catalogo/nuble/]].'),
            ('p', 'Para comparar con otra localidad de la misma región, revisa también [[qué hacer '
             'en Puerto Varas|/guias/que-hacer-en-puerto-varas/]].'),
            ('p', 'Si Chillán entra en tus opciones, mira el resto de [[terrenos en venta|/]] '
             'publicados y compara zona por zona.'),
        ],
    },
    'que-hacer-en-osorno': {
        'h1': 'Qué hacer en Osorno: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Osorno | Punto Parcelas',
        'meta': 'Qué hacer en Osorno: panoramas, lugares turísticos, clima y cómo llegar. Guía de '
            'la ciudad, sus termas y los lagos cercanos.',
        'keyword': 'que hacer en osorno  (720/mes)',
        'secundarias': 'panoramas en osorno (260) · clima de osorno (720) · como llegar a osorno (320) · '
            'lugares turisticos de osorno (70) · vivir en osorno (10)',
        'volumen': '2.100 búsquedas/mes',
        'cuerpo': [
            ('p', 'Osorno no se visita por la ciudad: se usa como base para llegar a los lagos, '
             'las termas y el parque nacional que la rodean.'),
            ('p', 'Es el centro de servicios del norte de la región de Los Lagos, con una vocación '
             'agrícola y ganadera que se nota en su feria y en su industria lechera.'),
            ('p', 'Desde acá salen los caminos al lago Rupanco, al lago Puyehue y al Parque '
             'Nacional Puyehue, además de la ruta internacional al paso Cardenal Samoré.'),
            ('p', 'Esa posición es la que explica su interés inmobiliario: permite vivir con todos '
             'los servicios y tener terreno a media hora del agua. Los proyectos están en '
             '[[Parcelas en Osorno|/catalogo/los-lagos/osorno/]].'),
            ('h2', 'Panoramas en Osorno y sus alrededores'),
            ('p', 'Las Termas de Puyehue, a unos 75 kilómetros, son el panorama más pedido: '
             'piscinas termales al aire libre en medio del bosque, abiertas todo el año.'),
            ('p', 'El lago Rupanco y el lago Puyehue ofrecen playas, pesca y navegación, con '
             'sectores bastante menos concurridos que el Llanquihue.'),
            ('p', 'En la ciudad, el Fuerte Reina Luisa, a orillas del río Rahue, y el Museo '
             'Histórico Municipal cubren bien una mañana.'),
            ('h2', 'Lugares turísticos de Osorno que conviene conocer'),
            ('p', 'El Parque Nacional Puyehue protege bosque valdiviano, saltos de agua y el '
             'sector de Aguas Calientes, con senderos señalizados de distinta dificultad.'),
            ('p', 'La Catedral San Mateo Apóstol, de líneas modernas y vitrales, es el edificio '
             'más reconocible del centro.'),
            ('p', 'Hacia el sur, el volcán Osorno y el lago Llanquihue quedan a poco más de una '
             'hora, lo que permite combinar los dos sectores en un mismo viaje.'),
            ('h2', 'Clima de Osorno a lo largo del año'),
            ('p', 'Es templado lluvioso, con lluvia repartida todo el año y un máximo entre mayo y '
             'agosto. El verano es más seco pero nunca del todo.'),
            ('p', 'Las temperaturas son moderadas: máximas de alrededor de 23 grados en enero y '
             'mínimas cercanas a 3 en julio, con heladas en el valle.'),
            ('p', 'Comparado con Puerto Varas, el sector tiene algo menos de precipitación, y eso '
             'es un dato real a la hora de elegir terreno.'),
            ('h2', 'Cómo llegar a Osorno'),
            ('p', 'Por la Ruta 5 Sur son unos 920 kilómetros desde Santiago y 110 desde Puerto '
             'Montt, con la carretera pasando por el costado de la ciudad.'),
            ('p', 'El aeropuerto Cañal Bajo recibe vuelos comerciales, aunque la mayoría de los '
             'viajeros llega por El Tepual, en Puerto Montt, a una hora y media.'),
            ('p', 'En bus hay servicios directos desde Santiago y recorridos frecuentes con Puerto '
             'Montt, Valdivia y Bariloche por el paso internacional.'),
            ('h2', 'Vivir en Osorno'),
            ('p', 'Tiene hospital, universidades, colegios y comercio completo, y un costo de vida '
             'más bajo que las ciudades turísticas de la misma región.'),
            ('p', 'Quien compra terreno acá suele buscar superficie: en el sector rural de la '
             'comuna las hectáreas rinden bastante más por presupuesto que en el borde del '
             'Llanquihue.'),
            ('p', 'El catálogo de [[Parcelas en Los Lagos|/catalogo/los-lagos/]] muestra todas las '
             'comunas de la región.'),
            ('p', 'Para comparar con la ciudad vecina, revisa también [[qué hacer en Puerto '
             'Varas|/guias/que-hacer-en-puerto-varas/]].'),
            ('p', 'Para seguir comparando, revisa todos los [[terrenos en venta|/]] del portal y '
             'elige según la región que más te acomode.'),
        ],
    },
    'que-hacer-en-villarrica': {
        'h1': 'Qué hacer en Villarrica: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Villarrica | Punto Parcelas',
        'meta': 'Qué hacer en Villarrica: panoramas, lugares turísticos, clima y cómo llegar. '
            'Guía del lago, el volcán y los alrededores de Pucón.',
        'keyword': 'que hacer en villarrica  (1.000/mes)',
        'secundarias': 'panoramas en villarrica (320) · clima de villarrica (260) · como llegar a '
            'villarrica (390) · lugares turisticos de villarrica (50) · vivir en villarrica '
            '(10)',
        'volumen': '2.030 búsquedas/mes',
        'cuerpo': [
            ('p', 'Villarrica tiene el lago y el volcán del mismo nombre enfrente, y bastante '
             'menos gente que Pucón, su vecina a 25 kilómetros.'),
            ('p', 'Está en la ribera suroeste del lago Villarrica, en la región de La Araucanía, y '
             'funciona como el acceso natural a toda la zona lacustre.'),
            ('p', 'El volcán Villarrica, uno de los más activos de Chile, domina el paisaje y es a '
             'la vez atracción turística y centro de esquí en invierno.'),
            ('p', 'La diferencia con Pucón es de ritmo y de precio: mismo lago, misma vista, menos '
             'saturación en temporada. Los terrenos disponibles están en [[Parcelas en '
             'Villarrica|/catalogo/araucania/villarrica/]].'),
            ('h2', 'Panoramas en Villarrica para cualquier estación'),
            ('p', 'La playa Pucará y el muelle concentran la actividad de verano, con navegación, '
             'kayak y deportes acuáticos en el lago.'),
            ('p', 'El ascenso al volcán se hace con guía autorizado y crampones, y es la excursión '
             'más conocida de la zona. En invierno, el centro de esquí opera en su ladera '
             'norte.'),
            ('p', 'Las termas de los alrededores, como Palguín y Menetúe, funcionan todo el año y '
             'son el plan clásico de día lluvioso.'),
            ('h2', 'Lugares turísticos de Villarrica y la zona lacustre'),
            ('p', 'El Museo Histórico y Arqueológico de Villarrica guarda piezas mapuche y es un '
             'buen punto de partida para entender la zona.'),
            ('p', 'El Parque Nacional Villarrica protege araucarias milenarias y senderos que '
             'conectan con los lagos Tinquilco y Caburgua.'),
            ('p', 'A 25 kilómetros está Pucón, y hacia el sur el lago Calafquén y Lican Ray '
             'completan el circuito de la Araucanía lacustre.'),
            ('h2', 'Clima de Villarrica: lluvioso con verano marcado'),
            ('p', 'Es templado lluvioso con influencia mediterránea: llueve bastante entre abril y '
             'septiembre, y el verano es claramente más seco.'),
            ('p', 'En enero las máximas rondan los 25 grados y las noches son frescas. En invierno '
             'las mínimas se acercan a cero y nieva en la cota alta del volcán.'),
            ('p', 'La lluvia es menor que en Puerto Varas y mayor que en Chillán, lo que ubica a '
             'la zona en un punto intermedio bastante cómodo para vivir todo el año.'),
            ('h2', 'Cómo llegar a Villarrica'),
            ('p', 'Desde Santiago son unos 750 kilómetros por la Ruta 5 Sur, con desvío en Freire '
             'hacia el oriente. En auto son entre ocho y nueve horas.'),
            ('p', 'El aeropuerto más cercano es La Araucanía, en Temuco, a unos 90 kilómetros, con '
             'vuelos diarios desde Santiago.'),
            ('p', 'En bus hay servicios directos desde Santiago y conexiones frecuentes con '
             'Temuco, Pucón y Valdivia.'),
            ('h2', 'Vivir en Villarrica'),
            ('p', 'Es una ciudad con servicios completos de hospital, colegios y comercio, que no '
             'se apaga fuera de temporada, a diferencia de varios balnearios del sur.'),
            ('p', 'El valor del suelo con vista al lago está entre los más altos de la región, '
             'pero a pocos kilómetros hacia el interior el panorama cambia por completo.'),
            ('p', 'El catálogo de [[Parcelas en Araucanía|/catalogo/araucania/]] reúne los '
             'proyectos de la zona.'),
            ('p', 'Para comparar con otra localidad del sur, revisa también [[qué hacer en Puerto '
             'Varas|/guias/que-hacer-en-puerto-varas/]].'),
            ('p', 'Cuando ya tengas clara la zona, revisa todos los [[terrenos en venta|/]] '
             'disponibles en el país y filtra por región para encontrar tu parcela.'),
        ],
    },
    'que-hacer-en-pichilemu': {
        'h1': 'Qué hacer en Pichilemu: panoramas, surf, clima y cómo llegar',
        'title': 'Qué hacer en Pichilemu | Punto Parcelas',
        'meta': 'Qué hacer en Pichilemu: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'de la capital del surf en Chile y de Punta de Lobos.',
        'keyword': 'que hacer en pichilemu  (1.000/mes)',
        'secundarias': 'panoramas en pichilemu (320) · clima de pichilemu (140) · como llegar a '
            'pichilemu (390) · lugares turisticos de pichilemu (40) · vivir en pichilemu (10)',
        'volumen': '1.900 búsquedas/mes',
        'cuerpo': [
            ('p', 'Pichilemu dejó de ser balneario de verano hace rato: Punta de Lobos la '
             'convirtió en destino de surf durante los doce meses del año.'),
            ('p', 'Está en el secano costero de la región de O\'Higgins y es la localidad costera '
             'más consolidada de ese tramo, con servicios y oferta de alojamiento propia.'),
            ('p', 'Su ola izquierda de Punta de Lobos recibe competencias internacionales y es '
             'reserva mundial de surf, lo que le dio proyección más allá del turismo local.'),
            ('p', 'Esa demanda sostenida explica por qué el suelo de la zona se movió tanto en la '
             'última década. Los proyectos están en [[Parcelas en '
             'Pichilemu|/catalogo/ohiggins/pichilemu/]].'),
            ('h2', 'Panoramas en Pichilemu más allá de la playa'),
            ('p', 'Punta de Lobos es la parada obligada: el mirador sobre los farellones y las dos '
             'rocas que salen del agua funcionan incluso para quien no entra al mar.'),
            ('p', 'La Laguna Petrel, al borde del pueblo, permite kayak y avistamiento de aves en '
             'agua calma, que es la alternativa cuando el oleaje no deja.'),
            ('p', 'Hacia el sur, las salinas de Cáhuil mantienen la extracción artesanal de sal y '
             'se visitan con recorridos guiados por los pozos.'),
            ('h2', 'Lugares turísticos de Pichilemu y su historia'),
            ('p', 'El Parque Ross, con sus palmeras y araucarias, y el edificio del antiguo casino '
             'recuerdan el origen del balneario como destino de la aristocracia a comienzos '
             'del siglo XX.'),
            ('p', 'La playa Infiernillo y la Terraza concentran el movimiento del centro, con la '
             'costanera y los puestos de artesanía.'),
            ('p', 'Más al sur están Bucalemu y Cáhuil, y hacia el norte Puertecillo y Matanzas, '
             'todas en la misma franja costera.'),
            ('h2', 'Clima de Pichilemu: templado y con viento'),
            ('p', 'Es clima mediterráneo costero, suave todo el año: las máximas de verano rondan '
             'los 22 grados y las mínimas de invierno rara vez bajan de 5.'),
            ('p', 'El viento es la constante y el factor que hace funcionar el surf. También '
             'explica por qué las tardes se sienten más frescas de lo que marca el '
             'termómetro.'),
            ('p', 'La lluvia se concentra entre mayo y agosto, y la camanchaca matinal es '
             'frecuente en primavera.'),
            ('h2', 'Cómo llegar a Pichilemu'),
            ('p', 'Desde Santiago son unos 185 kilómetros por la Ruta 66, la Autopista del Sol y '
             'el Acceso Sur, con desvío en Santa Cruz o por San Fernando.'),
            ('p', 'En auto el viaje toma entre dos horas y media y tres, y el camino está '
             'pavimentado en todo el trayecto.'),
            ('p', 'En bus hay servicios directos desde el Terminal San Borja de Santiago, con '
             'varias salidas diarias y más frecuencia en temporada alta.'),
            ('h2', 'Vivir en Pichilemu'),
            ('p', 'Tiene colegios, consultorio, supermercados y comercio estable, aunque la '
             'población se multiplica en enero y febrero y eso se siente en los servicios.'),
            ('p', 'Quien se queda a vivir suele buscar terreno en el sector alto o camino a '
             'Cáhuil, donde hay más superficie y menos presión turística que en el borde de '
             'playa.'),
            ('p', 'El catálogo de [[parcelas cerca de santiago|/catalogo/ohiggins/]] muestra todas '
             'las localidades del secano costero.'),
            ('p', 'Para comparar con otra de la misma región, revisa también [[qué hacer en '
             'Litueche|/guias/que-hacer-en-litueche/]].'),
            ('p', 'Si Pichilemu entra en tus opciones, mira el resto de [[terrenos en venta|/]] '
             'publicados y compara zona por zona.'),
        ],
    },
    'que-hacer-en-frutillar': {
        'h1': 'Qué hacer en Frutillar: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Frutillar | Punto Parcelas',
        'meta': 'Qué hacer en Frutillar: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'del Teatro del Lago y el borde del lago Llanquihue.',
        'keyword': 'que hacer en frutillar  (1.000/mes)',
        'secundarias': 'panoramas en frutillar (140) · clima de frutillar (90) · como llegar a frutillar '
            '(260) · lugares turisticos de frutillar (40) · vivir en frutillar (10)',
        'volumen': '1.540 búsquedas/mes',
        'cuerpo': [
            ('p', 'Frutillar tiene un teatro de categoría internacional construido sobre el lago, '
             'y eso no es una exageración turística: es el Teatro del Lago.'),
            ('p', 'El pueblo está en la ribera oeste del lago Llanquihue, con vista directa al '
             'volcán Osorno, y conserva la arquitectura de la colonización alemana mejor que '
             'cualquier otra localidad de la zona.'),
            ('p', 'Se divide en Frutillar Alto, junto a la carretera, y Frutillar Bajo, el sector '
             'histórico a orillas del lago, que es el que se visita.'),
            ('p', 'Cada verano, las Semanas Musicales llenan el pueblo de conciertos desde hace '
             'más de cincuenta años. Los terrenos disponibles están en [[Parcelas en '
             'Frutillar|/catalogo/los-lagos/frutillar/]].'),
            ('h2', 'Panoramas en Frutillar durante el año'),
            ('p', 'El Teatro del Lago mantiene temporada estable de conciertos y ópera, y su '
             'edificio sobre el agua se puede recorrer con visita guiada.'),
            ('p', 'La costanera y la playa de Frutillar Bajo funcionan como paseo todo el año, con '
             'la vista al Osorno de fondo.'),
            ('p', 'En verano, las Semanas Musicales llevan música clásica al pueblo durante dos '
             'semanas de enero y febrero, y conviene reservar alojamiento con bastante '
             'anticipación.'),
            ('h2', 'Lugares turísticos de Frutillar y su herencia alemana'),
            ('p', 'El Museo Colonial Alemán reconstruye las casas, la herrería y el molino de los '
             'colonos, con jardines que bajan hacia el lago.'),
            ('p', 'La iglesia y las casas patrimoniales del sector bajo conservan la madera '
             'original, y varias funcionan hoy como hotel o café.'),
            ('p', 'A 30 kilómetros está Puerto Varas y a 20 Llanquihue, lo que permite recorrer el '
             'circuito del lago completo en un día.'),
            ('h2', 'Clima de Frutillar: templado y lluvioso'),
            ('p', 'Es el mismo clima templado lluvioso de la cuenca del Llanquihue: precipitación '
             'todo el año, con máximo invernal entre mayo y agosto.'),
            ('p', 'Los veranos son frescos, con máximas en torno a 23 grados, y los inviernos '
             'fríos y húmedos, con mínimas cerca de cero.'),
            ('p', 'El lago modera la temperatura del borde, así que las heladas son menos intensas '
             'junto al agua que algunos kilómetros tierra adentro.'),
            ('h2', 'Cómo llegar a Frutillar'),
            ('p', 'La Ruta 5 Sur pasa por Frutillar Alto: son unos 970 kilómetros desde Santiago y '
             '70 desde Puerto Montt.'),
            ('p', 'Desde el aeropuerto El Tepual de Puerto Montt el viaje toma alrededor de una '
             'hora en auto.'),
            ('p', 'En bus, los servicios entre Puerto Montt, Puerto Varas y Osorno paran en '
             'Frutillar Alto, a unos dos kilómetros del sector bajo.'),
            ('h2', 'Vivir en Frutillar'),
            ('p', 'Es un pueblo chico y tranquilo, con servicios básicos cubiertos y dependencia '
             'de Puerto Varas y Puerto Montt para lo mayor.'),
            ('p', 'El borde de lago tiene precio de borde de lago; subiendo hacia el interior, el '
             'mismo presupuesto rinde bastante más superficie.'),
            ('p', 'El catálogo de [[Parcelas en Los Lagos|/catalogo/los-lagos/]] reúne las comunas '
             'de la zona.'),
            ('p', 'Para comparar con la ciudad vecina, revisa también [[qué hacer en Puerto '
             'Varas|/guias/que-hacer-en-puerto-varas/]].'),
            ('p', 'Para seguir comparando, revisa todos los [[terrenos en venta|/]] del portal y '
             'elige según la región que más te acomode.'),
        ],
    },
    'que-hacer-en-algarrobo': {
        'h1': 'Qué hacer en Algarrobo: panoramas, playas, clima y cómo llegar',
        'title': 'Qué hacer en Algarrobo | Punto Parcelas',
        'meta': 'Qué hacer en Algarrobo: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'del balneario del litoral central y sus playas.',
        'keyword': 'que hacer en algarrobo  (390/mes)',
        'secundarias': 'panoramas en algarrobo (110) · clima de algarrobo (210) · como llegar a '
            'algarrobo (170) · lugares turisticos de algarrobo (10) · vivir en algarrobo (10)',
        'volumen': '900 búsquedas/mes',
        'cuerpo': [
            ('p', 'Algarrobo es el balneario del litoral central que mejor combina playa '
             'tranquila, servicios y cercanía a Santiago.'),
            ('p', 'Está en la provincia de San Antonio, región de Valparaíso, y su bahía protegida '
             'le da un mar bastante más calmo que el del litoral abierto.'),
            ('p', 'Es conocido por el club de yates, por la piscina más grande del mundo en San '
             'Alfonso del Mar y por la Isla de los Pájaros Niños, con su colonia de pingüinos '
             'de Humboldt.'),
            ('p', 'La cercanía a la capital lo mantiene activo todo el año, no solo en temporada. '
             'Los proyectos de la comuna están en [[Parcelas en '
             'Algarrobo|/catalogo/valparaiso/algarrobo/]].'),
            ('h2', 'Panoramas en Algarrobo para el fin de semana'),
            ('p', 'La playa San Pedro y la playa Las Cadenas son las de mar más calmo, aptas para '
             'baño y para navegar a vela desde el club de yates.'),
            ('p', 'La playa El Canelillo, más pequeña y rodeada de roca, es la favorita para '
             'caminar al atardecer.'),
            ('p', 'Desde el borde se ve la Isla de los Pájaros Niños, santuario de la naturaleza '
             'con pingüinos de Humboldt. No se desembarca, pero hay recorridos en lancha por '
             'su perímetro.'),
            ('h2', 'Lugares turísticos de Algarrobo y alrededores'),
            ('p', 'El complejo San Alfonso del Mar es la postal más difundida del balneario por su '
             'laguna artificial de más de un kilómetro.'),
            ('p', 'Hacia el norte están Mirasol, El Quisco e Isla Negra, donde está la casa museo '
             'de Pablo Neruda, a quince minutos en auto.'),
            ('p', 'Hacia el sur, El Tabo y Las Cruces completan el recorrido del litoral central.'),
            ('h2', 'Clima de Algarrobo: templado todo el año'),
            ('p', 'Es mediterráneo costero, de amplitud térmica baja: veranos con máximas cercanas '
             'a 24 grados e inviernos con mínimas en torno a 7.'),
            ('p', 'La lluvia se concentra entre mayo y agosto y es moderada. El resto del año es '
             'seco, con neblina costera frecuente en las mañanas de primavera.'),
            ('p', 'Esa estabilidad es la razón por la que el litoral central se usa todo el año y '
             'no solo en verano.'),
            ('h2', 'Cómo llegar a Algarrobo'),
            ('p', 'Desde Santiago son unos 110 kilómetros por la Autopista del Sol, Ruta 78, con '
             'desvío hacia el norte en el cruce de Casablanca o por San Antonio.'),
            ('p', 'En auto el viaje toma alrededor de hora y media sin congestión, bastante más en '
             'los retornos de fin de semana largo.'),
            ('p', 'En bus hay servicios frecuentes desde el Terminal Alameda y desde San Antonio, '
             'que es el nodo de la zona.'),
            ('h2', 'Vivir en Algarrobo'),
            ('p', 'Tiene comercio, colegios y servicios de salud básicos, con Valparaíso y San '
             'Antonio cubriendo lo mayor a media hora.'),
            ('p', 'La población estable creció fuerte con el trabajo remoto, y eso presionó el '
             'valor del suelo cerca del borde costero.'),
            ('p', 'El catálogo de [[terrenos en viña del mar|/catalogo/valparaiso/]] muestra las '
             'comunas disponibles.'),
            ('p', 'Para comparar con otra localidad del mismo litoral, revisa también [[qué hacer '
             'en Santo Domingo|/guias/que-hacer-en-santo-domingo/]].'),
            ('p', 'Cuando ya tengas clara la zona, revisa todos los [[terrenos en venta|/]] '
             'disponibles en el país y filtra por región para encontrar tu parcela.'),
        ],
    },
    'que-hacer-en-constitucion': {
        'h1': 'Qué hacer en Constitución: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Constitución | Punto Parcelas',
        'meta': 'Qué hacer en Constitución: panoramas, lugares turísticos, clima y cómo llegar. '
            'Guía de la desembocadura del río Maule y sus playas.',
        'keyword': 'que hacer en constitucion  (170/mes)',
        'secundarias': 'panoramas en constitucion (40) · clima de constitucion (0) · como llegar a '
            'constitucion (210) · lugares turisticos de constitucion (10) · vivir en '
            'constitucion (10)',
        'volumen': '440 búsquedas/mes',
        'cuerpo': [
            ('p', 'Constitución tiene algo que no se repite en la costa chilena: un río grande '
             'desembocando entre roqueríos que se pueden caminar.'),
            ('p', 'La ciudad está donde el río Maule se encuentra con el mar, en la región del '
             'Maule, y vive del borde costero y de la industria forestal.'),
            ('p', 'Su atractivo principal son las formaciones rocosas de la playa, con la Piedra '
             'de la Iglesia como la más conocida, accesible a pie cuando baja la marea.'),
            ('p', 'Se reconstruyó después del terremoto y tsunami de 2010, y hoy su costanera es '
             'uno de los paseos mejor habilitados de la zona. Los proyectos están en '
             '[[Parcelas en Constitución|/catalogo/maule/constitucion/]].'),
            ('h2', 'Panoramas en Constitución junto al río y el mar'),
            ('p', 'La playa Piedras Blancas y el sector de la Piedra de la Iglesia concentran las '
             'formaciones rocosas que dan identidad al lugar. Conviene revisar la tabla de '
             'marea antes de caminar entre ellas.'),
            ('p', 'Por el río se hacen paseos en bote hasta la desembocadura, y más arriba está el '
             'sector de Putú con sus dunas.'),
            ('p', 'La costanera nueva, construida después del tsunami, funciona como paseo urbano '
             'con ciclovía y miradores al río.'),
            ('h2', 'Lugares turísticos de Constitución y la costa del Maule'),
            ('p', 'Las dunas de Putú, a unos 25 kilómetros al norte, son un campo dunar extenso '
             'con acceso por camino rural.'),
            ('p', 'Hacia el sur están Chanco y la Reserva Nacional Federico Albert, con bosque '
             'plantado sobre dunas para contener el avance de la arena.'),
            ('p', 'Río arriba, el valle del Maule concentra viñas con visita abierta, a una hora '
             'de la ciudad.'),
            ('h2', 'Clima de Constitución: costero y templado'),
            ('p', 'Es mediterráneo costero con influencia marina fuerte: veranos templados de '
             'máximas cercanas a 24 grados e inviernos suaves con mínimas en torno a 6.'),
            ('p', 'La lluvia se concentra entre mayo y agosto y es más abundante que en el litoral '
             'central, porque la zona ya está en transición hacia el sur.'),
            ('p', 'El viento de la tarde y la neblina costera matinal son habituales casi todo el '
             'año.'),
            ('h2', 'Cómo llegar a Constitución'),
            ('p', 'Desde Santiago son unos 340 kilómetros: Ruta 5 Sur hasta San Javier o Talca y '
             'luego camino hacia la costa.'),
            ('p', 'En auto el viaje toma alrededor de cuatro horas. El tramo final está '
             'pavimentado y bien señalizado.'),
            ('p', 'En bus hay servicios desde Santiago y conexiones frecuentes con Talca, que es '
             'la capital regional y el nodo de la zona.'),
            ('h2', 'Vivir en Constitución'),
            ('p', 'Es una ciudad con servicios propios de hospital, colegios y comercio, y no un '
             'balneario de temporada, lo que la hace funcional todo el año.'),
            ('p', 'El valor del suelo es considerablemente más bajo que en el litoral central a la '
             'misma distancia del mar, y ese contraste es lo que atrae a quien busca terreno '
             'costero.'),
            ('p', 'El catálogo de [[parcelas en maule|/catalogo/maule/]] reúne las comunas de la '
             'región.'),
            ('p', 'Para comparar con otra localidad cercana, revisa también [[qué hacer en '
             'Cauquenes|/guias/que-hacer-en-cauquenes/]].'),
            ('p', 'Si Constitución entra en tus opciones, mira el resto de [[terrenos en venta|/]] '
             'publicados y compara zona por zona.'),
        ],
    },
    'que-hacer-en-cauquenes': {
        'h1': 'Qué hacer en Cauquenes: panoramas, termas, clima y cómo llegar',
        'title': 'Qué hacer en Cauquenes | Punto Parcelas',
        'meta': 'Qué hacer en Cauquenes: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'del secano interior del Maule y sus termas.',
        'keyword': 'que hacer en cauquenes  (50/mes)',
        'secundarias': 'panoramas en cauquenes (10) · clima de cauquenes (140) · como llegar a cauquenes '
            '(140) · lugares turisticos de cauquenes (10) · vivir en cauquenes (0)',
        'volumen': '350 búsquedas/mes',
        'cuerpo': [
            ('p', 'Cauquenes es secano interior puro: viñas viejas de país, cerros suaves y termas '
             'a veinte minutos del centro.'),
            ('p', 'La ciudad está en el secano costero de la región del Maule, entre la cordillera '
             'de la Costa y el valle central, con una vocación vitivinícola de siglos.'),
            ('p', 'Es una de las zonas donde todavía se trabaja la cepa país en secano, sin riego, '
             'y eso le dio un lugar propio en el mapa del vino chileno.'),
            ('p', 'Su atractivo para quien busca terreno es la superficie: acá las hectáreas '
             'rinden bastante más por presupuesto que en la costa. Los proyectos están en '
             '[[Parcelas en Cauquenes|/catalogo/maule/cauquenes/]].'),
            ('h2', 'Panoramas en Cauquenes y el secano'),
            ('p', 'Las Termas de Cauquenes, a unos 25 kilómetros, son el panorama tradicional de '
             'la zona: piscinas de agua termal en un entorno de cerros.'),
            ('p', 'La ruta del vino del secano permite visitar viñas familiares que trabajan cepa '
             'país y cinsault con métodos antiguos.'),
            ('p', 'El embalse Tutuvén, cerca de la ciudad, se usa para pesca y paseo, y es el '
             'punto de agua más cercano al centro.'),
            ('h2', 'Lugares turísticos de Cauquenes y alrededores'),
            ('p', 'La Plaza de Armas y la Parroquia de Cauquenes ordenan un centro histórico de '
             'escala pequeña, recorrible a pie en una mañana.'),
            ('p', 'Hacia la costa están Chanco y Pelluhue, a menos de una hora, con playas '
             'extensas y poca ocupación fuera de temporada.'),
            ('p', 'Hacia el interior, Quirihue y el límite con Ñuble completan el circuito del '
             'secano.'),
            ('h2', 'Clima de Cauquenes: seco en verano, lluvioso en invierno'),
            ('p', 'Es mediterráneo con estación seca prolongada: veranos calurosos de máximas '
             'sobre 29 grados y muy secos, e inviernos lluviosos.'),
            ('p', 'La precipitación se concentra entre mayo y agosto, y el resto del año llueve '
             'poco, lo que define la agricultura de secano de la zona.'),
            ('p', 'La amplitud térmica diaria es alta: días calurosos y noches frescas incluso en '
             'pleno verano.'),
            ('h2', 'Cómo llegar a Cauquenes'),
            ('p', 'Desde Santiago son unos 350 kilómetros por la Ruta 5 Sur, con desvío hacia la '
             'costa en Parral o en San Javier.'),
            ('p', 'En auto el viaje toma alrededor de cuatro horas, con el tramo final por camino '
             'regional pavimentado.'),
            ('p', 'En bus hay servicios desde Santiago y conexiones con Talca, Chillán y Linares.'),
            ('h2', 'Vivir en Cauquenes'),
            ('p', 'Es una ciudad chica con hospital, colegios y comercio básico, y una vida '
             'bastante más tranquila y económica que el promedio de la región.'),
            ('p', 'El agua es la variable que define todo acá: en secano, un terreno con pozo '
             'ejecutado y caudal medido vale distinto a uno donde el pozo es una promesa.'),
            ('p', 'El catálogo de [[parcelas en maule|/catalogo/maule/]] muestra las comunas con '
             'proyectos.'),
            ('p', 'Para comparar con otra localidad del Maule, revisa también [[qué hacer en '
             'Constitución|/guias/que-hacer-en-constitucion/]].'),
            ('p', 'Para seguir comparando, revisa todos los [[terrenos en venta|/]] del portal y '
             'elige según la región que más te acomode.'),
        ],
    },
    'que-hacer-en-santo-domingo': {
        'h1': 'Qué hacer en Santo Domingo: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Santo Domingo | Punto Parcelas',
        'meta': 'Qué hacer en Santo Domingo: panoramas, lugares turísticos, clima y cómo llegar. '
            'Guía del balneario de Rocas de Santo Domingo.',
        'keyword': 'que hacer en santo domingo  (110/mes)',
        'secundarias': 'panoramas en santo domingo (10) · clima de santo domingo (40) · como llegar a '
            'santo domingo (70) · lugares turisticos de santo domingo (10) · vivir en santo '
            'domingo (10)',
        'volumen': '250 búsquedas/mes',
        'cuerpo': [
            ('p', 'Santo Domingo es el balneario más tranquilo del litoral central, y lo es por '
             'diseño: se planificó con calles arboladas y sin edificios en altura.'),
            ('p', 'Está en la región de Valparaíso, al sur de San Antonio y en la desembocadura '
             'del río Maipo, con una playa de varios kilómetros casi sin interrupciones.'),
            ('p', 'El sector de Rocas de Santo Domingo se trazó a mediados del siglo XX como '
             'balneario residencial, con pinos, calles curvas y baja densidad.'),
            ('p', 'Esa decisión urbana se mantiene y es la razón de su carácter: nada de torres '
             'frente al mar. Los proyectos de la comuna están en [[Parcelas en Santo '
             'Domingo|/catalogo/valparaiso/santo-domingo/]].'),
            ('h2', 'Panoramas en Santo Domingo y su entorno'),
            ('p', 'La playa es el panorama central: extensa, abierta y con oleaje fuerte, más apta '
             'para caminar y pescar que para baño prolongado.'),
            ('p', 'El campo de golf de Rocas de Santo Domingo es uno de los más antiguos del país '
             'y recibe torneos durante el año.'),
            ('p', 'En la desembocadura del Maipo hay humedal con avifauna, que es el punto de '
             'interés natural más relevante de la comuna.'),
            ('h2', 'Lugares turísticos de Santo Domingo y la costa cercana'),
            ('p', 'El humedal del río Maipo, declarado santuario de la naturaleza, concentra aves '
             'migratorias y tiene senderos de observación.'),
            ('p', 'A diez minutos está San Antonio con su puerto y su terminal pesquero, el más '
             'activo de la zona central.'),
            ('p', 'Hacia el norte, Llolleo, Las Cruces e Isla Negra completan el recorrido del '
             'litoral.'),
            ('h2', 'Clima de Santo Domingo: suave y estable'),
            ('p', 'Es mediterráneo costero de baja amplitud térmica: máximas de verano cercanas a '
             '23 grados y mínimas de invierno en torno a 7.'),
            ('p', 'La lluvia es moderada y se concentra entre mayo y agosto. La neblina matinal es '
             'frecuente en primavera y se levanta cerca del mediodía.'),
            ('p', 'El viento de la tarde es constante, algo a tener en cuenta al orientar una '
             'construcción.'),
            ('h2', 'Cómo llegar a Santo Domingo'),
            ('p', 'Desde Santiago son unos 120 kilómetros por la Autopista del Sol, Ruta 78, hasta '
             'San Antonio y luego al sur por la costa.'),
            ('p', 'En auto son cerca de hora y media, con el tramo final pavimentado y de poco '
             'tráfico.'),
            ('p', 'En bus hay servicios directos desde el Terminal Alameda y recorridos locales '
             'frecuentes desde San Antonio.'),
            ('h2', 'Vivir en Santo Domingo'),
            ('p', 'Es una comuna de baja densidad, con servicios acotados en el balneario y San '
             'Antonio cubriendo salud, comercio y educación a quince minutos.'),
            ('p', 'La población estable es pequeña y creció con el trabajo remoto, lo que mantiene '
             'el interés por terrenos en el sector residencial y en el camino interior.'),
            ('p', 'El catálogo de [[terrenos en viña del mar|/catalogo/valparaiso/]] reúne las '
             'comunas disponibles.'),
            ('p', 'Para comparar con otro balneario del mismo litoral, revisa también [[qué hacer '
             'en Algarrobo|/guias/que-hacer-en-algarrobo/]].'),
            ('p', 'Cuando ya tengas clara la zona, revisa todos los [[terrenos en venta|/]] '
             'disponibles en el país y filtra por región para encontrar tu parcela.'),
        ],
    },
    'que-hacer-en-litueche': {
        'h1': 'Qué hacer en Litueche: panoramas, clima y cómo llegar',
        'title': 'Qué hacer en Litueche | Punto Parcelas',
        'meta': 'Qué hacer en Litueche: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'del cruce al secano costero de O\'Higgins.',
        'keyword': 'que hacer en litueche  (50/mes)',
        'secundarias': 'panoramas en litueche (0) · clima de litueche (90) · como llegar a litueche (90) '
            '· lugares turisticos de litueche (0) · vivir en litueche (0)',
        'volumen': '230 búsquedas/mes',
        'cuerpo': [
            ('p', 'Litueche es el cruce obligado del secano costero de O\'Higgins: desde su centro '
             'salen los caminos a Matanzas, Navidad y Pichilemu.'),
            ('p', 'El pueblo está tierra adentro, en la provincia Cardenal Caro, y funciona como '
             'punto de servicios de toda la franja costera de la región.'),
            ('p', 'Su entorno es agrícola y ganadero, de cerros suaves y campos abiertos, con '
             'precios de suelo bastante por debajo de la costa a veinte minutos.'),
            ('p', 'Ese contraste es lo que lo pone en el mapa para quien busca superficie cerca '
             'del mar sin pagar borde costero. Los proyectos están en [[Parcelas en '
             'Litueche|/catalogo/ohiggins/litueche/]].'),
            ('h2', 'Panoramas en Litueche y la zona'),
            ('p', 'El atractivo del lugar es el entorno rural y los caminos: desde acá se llega en '
             'media hora a Matanzas y Pupuya, conocidas por el kitesurf.'),
            ('p', 'La laguna de Cáhuil y sus salinas quedan a unos 40 kilómetros, y Pichilemu a '
             'poco más de 50.'),
            ('p', 'En el pueblo mismo, la feria y el comercio local son el punto de encuentro de '
             'los campos de alrededor.'),
            ('h2', 'Lugares turísticos de Litueche y el secano costero'),
            ('p', 'Matanzas y Pupuya, en la comuna vecina de Navidad, son dos de los mejores '
             'puntos de viento de Chile para kitesurf y windsurf.'),
            ('p', 'La desembocadura del río Rapel, hacia el norte, tiene sectores de pesca y paseo '
             'en bote.'),
            ('p', 'Puertecillo, al norte de Pichilemu, es el punto de surf más recóndito de la '
             'zona y se llega por camino de tierra.'),
            ('h2', 'Clima de Litueche: seco en verano y templado'),
            ('p', 'Es mediterráneo de interior cercano a la costa: veranos secos con máximas sobre '
             '27 grados e inviernos lluviosos de mínimas cercanas a 5.'),
            ('p', 'Al estar tierra adentro tiene más amplitud térmica que la costa: días más '
             'calurosos y noches más frías que en Pichilemu.'),
            ('p', 'La lluvia se concentra entre mayo y agosto y el agua es el factor determinante '
             'del secano, porque no hay riego natural el resto del año.'),
            ('h2', 'Cómo llegar a Litueche'),
            ('p', 'Desde Santiago son unos 150 kilómetros por la Autopista del Sol hasta Melipilla '
             'y luego por la ruta hacia el sur.'),
            ('p', 'En auto el viaje toma alrededor de dos horas, con camino pavimentado en todo el '
             'trayecto.'),
            ('p', 'En bus hay servicios desde Santiago y recorridos locales que conectan con '
             'Pichilemu, Navidad y Marchigüe.'),
            ('h2', 'Vivir en Litueche'),
            ('p', 'Es un pueblo chico con consultorio, colegios y comercio básico; lo mayor se '
             'resuelve en Pichilemu o en San Fernando.'),
            ('p', 'La ventaja está en la superficie y en el agua: en el secano conviene exigir '
             'certificado de pozo y caudal medido antes de firmar.'),
            ('p', 'El catálogo de [[parcelas cerca de santiago|/catalogo/ohiggins/]] muestra todas '
             'las localidades de la región.'),
            ('p', 'Para comparar con la costa cercana, revisa también [[qué hacer en '
             'Pichilemu|/guias/que-hacer-en-pichilemu/]].'),
            ('p', 'Si Litueche entra en tus opciones, mira el resto de [[terrenos en venta|/]] '
             'publicados y compara zona por zona.'),
        ],
    },
    'que-es-una-parcela-de-agrado': {
        'h1': 'Qué es una parcela de agrado y en qué se diferencia de un terreno',
        'title': 'Qué es una parcela de agrado | Punto Parcelas',
        'meta': 'Qué es una parcela de agrado, en qué se diferencia de un terreno, qué es el rol '
            'propio y cómo comprar una parcela en Chile.',
        'keyword': 'que es una parcela de agrado  (110/mes)',
        'secundarias': 'parcela o terreno diferencia (0) · que es rol propio (40) · como comprar una '
            'parcela en chile (10) · conviene invertir en parcelas (0)',
        'volumen': '160 búsquedas/mes',
        'cuerpo': [
            ('p', 'Una parcela de agrado no es cualquier terreno rural: es una figura legal '
             'específica, y de ahí salen casi todas las dudas al comprar.'),
            ('p', 'El nombre viene del Decreto Ley 3.516, que permitió dividir predios rústicos en '
             'lotes de media hectárea como mínimo, con fines distintos de la explotación '
             'agrícola.'),
            ('p', 'Esa es la clave: la parcela de agrado se compra para habitar, descansar o '
             'invertir, no para producir. De ahí el "agrado".'),
            ('p', 'Entender la figura ahorra problemas, porque define qué se puede construir, qué '
             'documentos exigir y qué permite y qué no permite la normativa.'),
            ('h2', 'Parcela o terreno: la diferencia que importa'),
            ('p', 'Al comparar parcela o terreno, la diferencia no está en el tamaño sino en el '
             'estado legal de la subdivisión. Un terreno rural puede estar sin subdividir, y '
             'en ese caso lo que se compra es una cuota de un predio mayor, en comunidad con '
             'otros propietarios.'),
            ('p', 'Una parcela de agrado, en cambio, es un lote ya subdividido, con plano aprobado '
             'por el Servicio Agrícola y Ganadero y con inscripción propia en el Conservador '
             'de Bienes Raíces.'),
            ('p', 'La consecuencia práctica es grande: sobre un lote propio se puede hipotecar, '
             'vender y construir de forma independiente. Sobre una cuota en comunidad, cada '
             'decisión depende del resto de los comuneros.'),
            ('h2', 'Qué es rol propio y por qué se exige'),
            ('p', 'El rol es el número con que el Servicio de Impuestos Internos identifica una '
             'propiedad para efectos de contribuciones. Quien pregunta qué es rol propio está '
             'preguntando, en realidad, si la parcela existe como unidad independiente ante '
             'el Estado.'),
            ('p', 'Con rol propio la parcela tiene su propio avalúo, paga sus propias '
             'contribuciones y puede recibir servicios a nombre del dueño.'),
            ('p', 'Sin rol propio, la parcela comparte el del predio madre, y eso complica desde '
             'pedir un crédito hipotecario hasta solicitar factibilidad eléctrica.'),
            ('p', 'Es, junto con la escritura inscrita, el documento que no se negocia.'),
            ('h2', 'Cómo comprar una parcela en Chile, paso a paso'),
            ('p', 'El proceso tiene una secuencia que conviene respetar y no apurar.'),
            ('li', 'Visitar el terreno en persona, idealmente después de una lluvia fuerte.'),
            ('li', 'Pedir el certificado de dominio vigente y el de hipotecas y gravámenes.'),
            ('li', 'Verificar el rol propio, el plano aprobado por el SAG y la recepción de la '
             'subdivisión.'),
            ('li', 'Revisar la factibilidad de agua: pozo ejecutado con caudal medido, no '
             'prometido.'),
            ('li', 'Confirmar la factibilidad eléctrica y quién mantiene el camino de acceso.'),
            ('li', 'Firmar promesa de compraventa y después escritura, con inscripción en el '
             'Conservador.'),
            ('h2', 'Conviene invertir en parcelas: qué mirar antes de decidir'),
            ('p', 'La pregunta de si conviene invertir en parcelas no tiene respuesta única, pero '
             'sí tres factores que explican casi toda la diferencia de rentabilidad.'),
            ('p', 'El primero es la consolidación del sector: un loteo donde ya hay casas '
             'construidas y camino mantenido se aprecia distinto a uno donde no hay nada.'),
            ('p', 'El segundo es el agua, que en el secano define el valor más que la vista. El '
             'tercero es el acceso: distancia real a un centro urbano con servicios, medida '
             'en tiempo de manejo y no en kilómetros.'),
            ('p', 'Si estás en etapa de comparar zonas, las guías de localidad de este sitio '
             'cubren clima, accesos y vida diaria de cada una, y el catálogo por región '
             'muestra lo que hay disponible hoy.'),
            ('p', 'Con la figura legal clara, el paso siguiente es mirar la oferta: revisa todos '
             'los [[terrenos en venta|/]] disponibles y compara por región.'),
        ],
    },
    'que-hacer-en-vichuquen': {
        'h1': 'Qué hacer en Vichuquén: panoramas, lago, clima y cómo llegar',
        'title': 'Qué hacer en Vichuquén | Punto Parcelas',
        'meta': 'Qué hacer en Vichuquén: panoramas, lugares turísticos, clima y cómo llegar. Guía '
            'del lago Vichuquén y la Laguna Torca.',
        'keyword': 'que hacer en vichuquen  (20/mes)',
        'secundarias': 'panoramas en vichuquen (10) · clima de vichuquen (0) · como llegar a vichuquen '
            '(30) · lugares turisticos de vichuquen (10) · vivir en vichuquen (0)',
        'volumen': '70 búsquedas/mes',
        'cuerpo': [
            ('p', 'El lago Vichuquén es agua salada conectada al mar, y por eso tiene la '
             'combinación rara de lago navegable con fauna marina.'),
            ('p', 'La comuna está en la costa norte de la región del Maule y gira en torno a su '
             'lago, uno de los destinos náuticos más establecidos de Chile central.'),
            ('p', 'El pueblo de Vichuquén conserva casas de adobe y teja colonial, y está '
             'declarado zona típica.'),
            ('p', 'Junto al lago está la Reserva Nacional Laguna Torca, refugio de cisnes de '
             'cuello negro. Los proyectos de la comuna están en [[Parcelas en '
             'Vichuquén|/catalogo/maule/vichuquen/]].'),
            ('h2', 'Panoramas en Vichuquén sobre el agua'),
            ('p', 'El lago concentra la actividad: esquí acuático, vela, kayak y wakeboard, con '
             'clubes y rampas de acceso en varios sectores de la orilla.'),
            ('p', 'La playa de Llico, en la desembocadura, suma mar abierto a quince minutos del '
             'lago, con oleaje y pesca.'),
            ('p', 'La Reserva Nacional Laguna Torca permite avistamiento de aves desde senderos y '
             'miradores habilitados.'),
            ('h2', 'Lugares turísticos de Vichuquén y su patrimonio'),
            ('p', 'El pueblo de Vichuquén, con su iglesia y sus casas de adobe, es zona típica y '
             'se recorre a pie en poco tiempo.'),
            ('p', 'El Museo de Vichuquén guarda piezas arqueológicas de la zona, incluida cerámica '
             'de influencia incaica.'),
            ('p', 'Hacia el sur, Iloca y Duao completan el circuito costero de la provincia de '
             'Curicó.'),
            ('h2', 'Clima de Vichuquén: mediterráneo con brisa de lago'),
            ('p', 'Es mediterráneo costero: veranos secos y templados con máximas cercanas a 26 '
             'grados, e inviernos lluviosos de mínimas en torno a 6.'),
            ('p', 'El lago y el mar moderan la temperatura, así que los extremos son menores que '
             'en el valle de Curicó, a la misma latitud.'),
            ('p', 'El viento de la tarde es constante en verano y es justamente lo que sostiene la '
             'actividad de vela.'),
            ('h2', 'Cómo llegar a Vichuquén'),
            ('p', 'Desde Santiago son unos 270 kilómetros: Ruta 5 Sur hasta Curicó y luego camino '
             'al poniente hacia Hualañé y el lago.'),
            ('p', 'En auto el viaje toma alrededor de tres horas y media, con el último tramo por '
             'camino regional pavimentado.'),
            ('p', 'En bus hay servicios desde Curicó, que es el nodo de conexión con Santiago.'),
            ('h2', 'Vivir en Vichuquén'),
            ('p', 'Es una comuna rural de población pequeña, con servicios básicos en el pueblo y '
             'Curicó cubriendo salud y comercio mayor a una hora.'),
            ('p', 'El borde de lago es el sector más cotizado y tiene precio acorde; hacia el '
             'interior y en el camino a Llico el panorama cambia.'),
            ('p', 'El catálogo de [[parcelas en maule|/catalogo/maule/]] reúne las comunas de la '
             'región.'),
            ('p', 'Para comparar con otra localidad del Maule, revisa también [[qué hacer en '
             'Constitución|/guias/que-hacer-en-constitucion/]].'),
            ('p', 'Para seguir comparando, revisa todos los [[terrenos en venta|/]] del portal y '
             'elige según la región que más te acomode.'),
        ],
    },
    'que-revisar-antes-de-comprar-una-parcela': {
        'h1': 'Qué revisar antes de comprar una parcela',
        'title': 'Qué revisar antes de comprar una parcela | Punto Parcelas',
        'meta': 'Qué revisar antes de comprar una parcela: documentos, agua, acceso y cómo '
            'funciona el crédito directo. La lista completa.',
        'keyword': 'que revisar antes de comprar una parcela  (0/mes)',
        'secundarias': 'como saber si una parcela tiene agua (0) · como funciona el credito directo en '
            'parcelas (0)',
        'volumen': '0 búsquedas/mes',
        'cuerpo': [
            ('p', 'Casi todos los problemas de una compra de parcela se detectan antes de firmar, '
             'y con tres documentos.'),
            ('p', 'La parcela se compra mirando la vista y se sufre por el camino, el agua o un '
             'gravamen que nadie revisó.'),
            ('p', 'Esta es la revisión que conviene hacer en orden, partiendo por lo que se '
             'verifica en papel y terminando por lo que solo se ve en terreno.'),
            ('p', 'Ninguno de estos pasos requiere abogado para la primera revisión, aunque sí '
             'conviene tenerlo para la escritura.'),
            ('h2', 'Los documentos que hay que pedir'),
            ('p', 'Son cinco y se piden todos juntos, antes de cualquier reserva o pago.'),
            ('li', 'Certificado de dominio vigente, que acredita quién es el dueño hoy.'),
            ('li', 'Certificado de hipotecas y gravámenes, que muestra deudas, embargos y '
             'servidumbres.'),
            ('li', 'Plano de subdivisión aprobado por el SAG y su resolución.'),
            ('li', 'Rol de avalúo propio del lote en el Servicio de Impuestos Internos.'),
            ('li', 'Certificado de deuda de contribuciones al día.'),
            ('h2', 'Cómo saber si una parcela tiene agua'),
            ('p', 'Esta es la revisión que más dinero ahorra y la que más se omite. Quien pregunta '
             'cómo saber si una parcela tiene agua suele recibir como respuesta que "hay napa '
             'en el sector", y eso no es un dato.'),
            ('p', 'Lo que corresponde pedir es el informe del pozo ya ejecutado, con su '
             'profundidad y su caudal medido en litros por segundo, más el derecho de '
             'aprovechamiento de aguas inscrito cuando exista.'),
            ('p', 'Si el pozo no está hecho, el costo y el resultado son del comprador: perforar '
             'sin garantía de caudal puede costar varios millones y no dar agua suficiente.'),
            ('p', 'En zonas de secano, como el interior del Maule o de O\'Higgins, este punto '
             'define el valor del terreno más que la superficie.'),
            ('h2', 'El acceso, la servidumbre y el camino'),
            ('p', 'Un terreno sin acceso legal garantizado vale mucho menos de lo que parece, '
             'aunque hoy se llegue sin problema.'),
            ('p', 'Hay que verificar que el acceso esté constituido como servidumbre de tránsito '
             'inscrita, y no que sea un camino de hecho por el predio del vecino.'),
            ('p', 'La otra pregunta es quién mantiene el camino interior y con qué fondos: en '
             'loteos nuevos esto suele quedar a cargo de la comunidad de copropietarios, y '
             'conviene saber el monto del gasto común antes de comprar.'),
            ('h2', 'Cómo funciona el crédito directo en parcelas'),
            ('p', 'Cuando el banco no financia terreno rural, varios proyectos ofrecen crédito '
             'directo: el vendedor financia el saldo en cuotas, sin intermediario bancario.'),
            ('p', 'Lo habitual es un pie de entre el 20% y el 30% y el saldo en cuotas mensuales a '
             'plazos de 2 a 10 años, con la escritura entregada al pagar la última cuota o '
             'con hipoteca a favor del vendedor desde el inicio.'),
            ('p', 'Las dos cosas que conviene dejar claras por escrito son qué pasa si el '
             'comprador se atrasa y en qué momento exacto se inscribe la propiedad a su '
             'nombre. Esa diferencia es la que distingue un crédito directo serio de uno que '
             'no lo es.'),
            ('p', 'El catálogo por región indica qué proyectos trabajan con esta modalidad.'),
            ('h2', 'Lo que solo se ve en terreno'),
            ('p', 'Tres cosas no aparecen en ningún certificado y hay que ir a verlas.'),
            ('p', 'El drenaje después de una lluvia fuerte, porque un sector que acumula agua en '
             'invierno no se arregla con relleno. La pendiente real, que en plano se ve '
             'distinta a como se camina. Y el ruido o el olor del entorno: una planta, un '
             'plantel avícola o una ruta cercana cambian el uso de la parcela y no figuran en '
             'el plano.'),
            ('p', 'Conviene además visitar en día de semana y en fin de semana: el movimiento del '
             'sector cambia bastante entre uno y otro.'),
            ('p', 'Con esta revisión hecha, ya puedes avanzar tranquilo: mira todos los [[terrenos '
             'en venta|/]] publicados y elige la parcela según la región que buscas.'),
        ],
    },
}

SLUGS = tuple(GUIAS)


# ---------------------------------------------------------------------------
# Resolucion de los enlaces internos
# ---------------------------------------------------------------------------
import re

from django.utils.html import escape
from django.utils.safestring import mark_safe

_ENLACE = re.compile(r'\[\[([^|\]]+)\|([^\]]+)\]\]')


def _ruta_viva(ruta):
    """La mejor ruta REAL para ese destino, bajando de comuna a region a catalogo.

    El documento da por hecho que las 12 comunas existen y tres no (medido el
    06-10 contra el sitio). Una comuna o region sin parcelas devuelve 404 a
    proposito, asi que publicar el href tal cual seria publicar un enlace roto
    en la pagina que justamente viene a traer trafico.

    Se consulta en cada render y no se cachea: Leonardo carga parcelas desde su
    panel y el enlace tiene que aparecer el mismo dia, no en el proximo deploy.
    """
    from .seo import ciudades_de_region
    from .views import REGION_KEY_A_SLUG, _regiones_con_parcelas

    tramos = [t for t in ruta.strip('/').split('/') if t]
    # Solo se verifican las rutas de catalogo; /, /guias/... pasan tal cual.
    if len(tramos) < 2 or tramos[0] != 'catalogo':
        return ruta

    slug_a_key = {slug: key for key, slug in REGION_KEY_A_SLUG.items()}
    key = slug_a_key.get(tramos[1])
    if key is None:                       # no es una region: caracteristica u otra
        return ruta

    vivas = _regiones_con_parcelas()
    if key not in vivas:                  # ni la region existe -> catalogo completo
        return '/catalogo/'

    ruta_region = '/catalogo/%s/' % tramos[1]
    if len(tramos) == 2:
        return ruta_region

    # Pedia una comuna: solo vale si HOY tiene parcelas.
    if any(c['slug'] == tramos[2] for c in ciudades_de_region(key)):
        return '/catalogo/%s/%s/' % (tramos[1], tramos[2])
    return ruta_region


def con_enlaces(texto):
    """El texto con [[anchor|ruta]] convertido en <a>, con la ruta ya resuelta.

    Se escapa el texto ANTES de meter el HTML: el contenido viene de un .docx y
    cualquier `<` o `&` suelto rompe la pagina o, peor, inyecta marcado.
    """
    partes, fin = [], 0
    for m in _ENLACE.finditer(texto):
        partes.append(escape(texto[fin:m.start()]))
        anchor, ruta = m.group(1), _ruta_viva(m.group(2))
        partes.append('<a href="%s">%s</a>' % (escape(ruta), escape(anchor)))
        fin = m.end()
    partes.append(escape(texto[fin:]))
    return mark_safe(''.join(partes))


def cuerpo_renderizado(slug):
    """[(etiqueta, html)] listo para la plantilla."""
    guia = GUIAS.get(slug)
    if not guia:
        return []
    return [(tipo, con_enlaces(txt)) for tipo, txt in guia['cuerpo']]


def sin_marcadores(texto):
    """El texto plano, sin los [[...]]. Para la meta y el schema."""
    return _ENLACE.sub(lambda m: m.group(1), texto)
