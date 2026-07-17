from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import os

from core.models import Parcela, Testimonio


PARCELAS = [
    {
        'nombre': 'Vive Ovalle',
        'slug': 'vive-ovalle',
        'region': 'coquimbo', 'sector': 'Sector Los Baños, Playa Talcaruca',
        'precio': 12_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas agrícolas de 5.000 m² frente al mar en la IV Región de Coquimbo. '
            'Topografía 100% plana con lomaje suave para aprovechar al máximo el terreno. '
            'Ubicadas en Ruta D-540, Sector Los Baños, a pasos del borde costero — '
            'una plusvalía única en la zona.\n\n'
            'Distancias: 40 min del Parque Nacional Fray Jorge · 1 h de Tongoy · '
            '1 h 30 min de Coquimbo · 4 h 30 min de Santiago.\n\n'
            'Servicios: luz mediante paneles solares · agua mediante camión aljibe. '
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar en 10 días hábiles. '
            'Reserva: $350.000 (gastos operacionales). '
            'Financiamiento directo disponible: 12 o 24 cuotas. Pie desde $3.990.000.'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parque Algarrobo',
        'slug': 'parque-algarrobo',
        'region': 'valparaiso', 'sector': 'Santo Domingo',
        'precio': 110_000_000, 'superficie': 50000,
        'descripcion': (
            'Macrolotes desde 5 hectáreas en la V Región de Valparaíso, a pasos de Santo Domingo. '
            'Entorno natural privilegiado con acceso a playas, reserva natural y conectividad directa con Santiago.\n\n'
            'Distancias: 15 min de Algarrobo · 10 min de San Alfonso del Mar · '
            '15 min de Playa El Canelo · 30 min de Tunquen · 1 h 20 min de Santiago vía Ruta 68.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Financiamiento directo hasta 60 cuotas. Pie desde 35%. '
            'Reserva: $500.000. Precio se fija contra firma de promesa (cuotas en pesos).'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': True, 'rol_propio': True,
    },
    {
        'nombre': 'Proyecto Vive Til Til',
        'slug': 'proyecto-vive-til-til',
        'region': 'metropolitana', 'sector': 'Til Til, cercano a Lampa y Batuco',
        'precio': 49_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas agrícolas de 5.000 m² en la Región Metropolitana, en la atractiva '
            'ubicación de Til Til. Topografía plana con lomaje suave, acceso estabilizado '
            'y documentación vigente. Excelente opción de inversión cerca de Santiago.\n\n'
            'Distancias: 35 min de Santiago · 25 min de Til Til · 27 min de Lampa · 28 min de Batuco.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar en 10 días hábiles. '
            'Venta solo contado. Reserva: $350.000 (gastos operacionales).'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Hacienda Don Bastián',
        'slug': 'hacienda-don-bastian',
        'region': 'ohiggins', 'sector': 'La Estrella, VI Región',
        'precio': 15_990_000, 'superficie': 5000,
        'descripcion': (
            'Ubicado en el corazón de la VI Región, en medio de lomajes suaves e increíbles pendientes, '
            'con flora y fauna típica del valle central de Chile. Hacienda Don Bastián es uno de los '
            'encantos naturales con cualidades topográficas únicas — todo un oasis.\n\n'
            'Distancias: 3 min del centro de La Estrella · 30 min de Litueche · '
            '30 min de Central Rapel · 1 h de Lago Rapel · 50 min de Pichilemu · 2 h de Santiago.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Parcelas agrícolas con accesos estabilizados.'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': False, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Estancia Paredones',
        'slug': 'estancia-paredones',
        'region': 'ohiggins', 'sector': 'Paredones, VI Región',
        'precio': 5_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas a orilla de carretera asfaltada con locomoción y postación eléctrica disponible. '
            'Topografía variada entre lomaje y pendiente. Una de las opciones más accesibles de la '
            'VI Región con excelente conectividad.\n\n'
            'Distancias: 6 min de San Pedro de Alcántara · 40 min a playas (Bucalemu/Llico) · '
            '35 min de Laguna Torca · 25 min del centro de Paredones · '
            '1 h de Pichilemu · 3 h de Santiago.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Accesos estabilizados con maicillo.'
        ),
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Olivos de Trinidad',
        'slug': 'olivos-de-trinidad',
        'region': 'ohiggins', 'sector': 'Marchigue, cerca de Peralillo',
        'precio': 19_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas con topografía plana y lomaje suave en la zona de Marchigue, VI Región. '
            'Acceso pavimentado con excelente conectividad. Entorno de alto valor paisajístico '
            'con proyección de plusvalía en el Valle de Colchagua.\n\n'
            'Distancias: 15 min de Peralillo · 1 h de Pichilemu · 2 h 30 min de Santiago.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG). '
            'Escrituración en 10–15 días hábiles. Reserva: $350.000 (gastos operacionales). '
            'Financiamiento directo disponible: 12 o 24 cuotas.'
        ),
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Fundo la Quirigua',
        'slug': 'fundo-la-quirigua',
        'region': 'maule', 'sector': 'Lago Vichuquén, VII Región',
        'precio': 13_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas en la VII Región del Maule, a pasos de la Laguna Torca y el Lago Vichuquén. '
            'Topografía plana con lomaje suave. Zona de altísimo atractivo turístico y natural '
            'a menos de 4 horas de Santiago.\n\n'
            'Distancias: 3 min de Laguna Torca · 8 min del Lago Vichuquén · '
            '7 km de Playa Llico · 30 min de Bucalemu · 40 min de Playa Duao · '
            '1 h de Pichilemu · 3 h 30 min de Santiago.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Financiamiento directo disponible: pie $3.990.000 + 24 cuotas de $550.000.'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': False, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Vive Chillán',
        'slug': 'vive-chillan',
        'region': 'nuble', 'sector': 'Portezuelo - San Nicolás, XVI Región',
        'precio': 9_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas agrícolas 100% planas en la XVI Región del Ñuble, entre Portezuelo y San Nicolás. '
            'Ruta N-60-O Los Conquistadores. Excelente opción para inversión agrícola o residencial '
            'en una de las regiones de mayor crecimiento del país.\n\n'
            'Distancias: 30 min de Chillán · 1 h 30 min de Concepción · '
            '1 h 30 min de Talcahuano · 2 h de Talca · 5 h de Santiago.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Accesos estabilizados. Sin financiamiento directo — venta contado.'
        ),
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': False, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Bosques de Frutillar',
        'slug': 'bosques-de-frutillar',
        'region': 'los_lagos', 'sector': 'Frutillar, X Región',
        'precio': 14_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas en la X Región de Los Lagos con impresionantes vistas a los volcanes. '
            'Topografía plana con lomaje suave en entorno natural privilegiado. '
            'Factibilidad de agua y luz. A pasos de Ruta 5 y aeropuerto regional.\n\n'
            'Distancias: 15 min del centro de Frutillar · 18 min del Lago Frutillar Bajo · '
            '10 min de Ruta 5 · 40 min del aeropuerto · 50 min de Puerto Montt · 15 min de Purranque.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), '
            'listo para escriturar en 10 días hábiles. Reserva: $350.000 (gastos operacionales).'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': True, 'rol_propio': True,
    },
    {
        'nombre': 'Vive Osorno',
        'slug': 'vive-osorno',
        'region': 'los_lagos', 'sector': 'Osorno, X Región',
        'precio': 22_990_000, 'superficie': 5000,
        'descripcion': (
            'Parcelas 100% planas a orilla de camino público en la X Región de Los Lagos, '
            'a solo 13 minutos de la plaza de Osorno. Excelente accesibilidad — '
            '3 minutos del asfalto y cercano al aeropuerto regional.\n\n'
            'Distancias: 13 min de la plaza de Osorno · 15 min del aeropuerto Osorno · '
            '45 min de Entrelagos · 1 h 10 min de Bahía Manza · 2 h de aduana Argentina.\n\n'
            'Rol propio individual, documentación al día (CBR/SII/SAG), listo para escriturar. '
            'Financiamiento directo disponible: pie desde $4.990.000 en 12, 24 o 36 cuotas. '
            'Reserva: $350.000 (gastos operacionales).'
        ),
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
]


TESTIMONIOS = [
    {
        'nombre': 'Claudia Reyes',
        'profesion': 'Inversionista',
        'ciudad': 'Santiago',
        'texto': 'Compré mi parcela con Leonardo y fue un proceso increíblemente sencillo. Todo en orden, escriturado en tiempo récord. 100% recomendado.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 1,
    },
    {
        'nombre': 'Rodrigo Molina',
        'profesion': 'Empresario',
        'ciudad': 'Concepción',
        'texto': 'Llevaba meses buscando una parcela en el sur. Leonardo me consiguió opciones que no encontré en ningún otro lado, con precios reales y documentación impecable.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 2,
    },
    {
        'nombre': 'Patricia Uribe',
        'profesion': 'Inversionista',
        'ciudad': 'Viña del Mar',
        'texto': 'Gracias a Punto Parcelas tengo mi inversión asegurada. El seguimiento fue excelente y la transparencia en todo el proceso me dio mucha confianza.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 3,
    },
    {
        'nombre': 'Héctor Sáez',
        'profesion': 'Arquitecto',
        'ciudad': 'Temuco',
        'texto': 'La parcela superó todas mis expectativas. Vista privilegiada, listo para construir. Proceso limpio y asesoría profesional en todo momento.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 4,
    },
]


class Command(BaseCommand):
    help = 'Carga datos REALES de parcelas desde puntoparcelas.cl + testimonios + superusuario'

    def handle(self, *args, **options):
        created_parcelas = 0
        updated_parcelas = 0
        for data in PARCELAS:
            slug = data.pop('slug')
            obj, created = Parcela.objects.get_or_create(slug=slug, defaults={**data, 'slug': slug})
            if not created:
                for k, v in data.items():
                    setattr(obj, k, v)
                obj.slug = slug
                obj.save()
                updated_parcelas += 1
            else:
                created_parcelas += 1

        created_testimonios = 0
        for data in TESTIMONIOS:
            _, created = Testimonio.objects.get_or_create(nombre=data['nombre'], defaults=data)
            if created:
                created_testimonios += 1

        username = os.environ.get('PANEL_USERNAME', 'leonardo')
        password = os.environ.get('PANEL_PASSWORD', 'PuntoParcelas2026!')
        email = os.environ.get('PANEL_EMAIL', 'l.valencia@ctpchile.cl')

        user = User.objects.filter(username=username).first()
        if not user:
            User.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                first_name=os.environ.get('PANEL_FIRST_NAME', 'Leonardo'),
                last_name=os.environ.get('PANEL_LAST_NAME', 'Valencia'),
            )
            self.stdout.write(f'Superusuario "{username}" creado.')
        elif os.environ.get('PANEL_PASSWORD'):
            user.email = email
            user.first_name = os.environ.get('PANEL_FIRST_NAME', user.first_name or 'Leonardo')
            user.last_name = os.environ.get('PANEL_LAST_NAME', user.last_name or 'Valencia')
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(f'Superusuario "{username}" actualizado desde variables PANEL_.')

        self.stdout.write(self.style.SUCCESS(
            f'Seed OK — {created_parcelas} parcelas creadas, {updated_parcelas} actualizadas, '
            f'{created_testimonios} testimonios.'
        ))
