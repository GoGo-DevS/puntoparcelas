from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Consulta, Parcela, Testimonio


PARCELAS = [
    {
        'nombre': 'Parcela El Arrayán — Vista al Valle',
        'slug': 'parcela-el-arrayan-vista-al-valle',
        'region': 'metropolitana', 'sector': 'Lo Barnechea',
        'precio': 48_000_000, 'superficie': 5000,
        'descripcion': 'Hermosa parcela de 5.000 m² en Lo Barnechea con vista privilegiada al valle de Santiago. Cuenta con acceso pavimentado, luz trifásica y agua potable de red municipal. Ideal para construcción de casa de campo o inversión de largo plazo. Escritura limpia sin gravámenes.',
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': True, 'tiene_porton': True,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Río Claro — Sector Pirque',
        'slug': 'parcela-rio-claro-pirque',
        'region': 'metropolitana', 'sector': 'Pirque',
        'precio': 35_000_000, 'superficie': 3500,
        'descripcion': 'Tranquila parcela en Pirque, a 25 min de Buin. Con acceso a canal de riego y electricidad. Zona de alta plusvalía por proyectos inmobiliarios en desarrollo. Terreno plano, ideal para edificación.',
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': True, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Bosque Nativo — Colina Norte',
        'slug': 'parcela-bosque-nativo-colina',
        'region': 'metropolitana', 'sector': 'Colina',
        'precio': 42_500_000, 'superficie': 8000,
        'descripcion': 'Impresionante parcela de 8.000 m² rodeada de bosque nativo en Colina. Zona privilegiada con aire puro y naturaleza. Ideal para eco-proyecto o cabaña de descanso. Camino de acceso propio. Documentación al día.',
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': True, 'tiene_porton': True,
        'es_turistico': True, 'bosque_nativo': True, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Viña El Huique — O\'Higgins',
        'slug': 'parcela-vina-el-huique-ohiggins',
        'region': 'ohiggins', 'sector': 'San Vicente de Tagua Tagua',
        'precio': 28_000_000, 'superficie': 10000,
        'descripcion': 'Terreno agrícola de 1 hectárea en la fértil VI Región. Riego garantizado, suelo apto para viña, frutales y huerta. Excelente conectividad con San Vicente. Oportunidad de inversión para producción agrícola o fundo familiar.',
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': True, 'tiene_porton': True,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Campestre — Maule Sur',
        'slug': 'parcela-campestre-maule-sur',
        'region': 'maule', 'sector': 'Talca',
        'precio': 18_500_000, 'superficie': 7500,
        'descripcion': 'Parcela semi-rural de 7.500 m² a 15 km de Talca. Agua de pozo profundo, electricidad en el predio. Entorno campestre de alta tranquilidad. Adyacente a Carretera Panamericana para fácil acceso.',
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Lago Villarrica — Araucanía',
        'slug': 'parcela-lago-villarrica-araucania',
        'region': 'araucania', 'sector': 'Pucón',
        'precio': 65_000_000, 'superficie': 4200,
        'descripcion': 'Parcela turística de primer nivel en las inmediaciones de Pucón con vista al volcán Villarrica. A 800 metros del lago. Uso turístico permitido. Electricidad y agua de red. Alto potencial para arriendo turístico o proyecto hotelero boutique.',
        'destacada': True, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': True, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Cerro Concepción — Biobío',
        'slug': 'parcela-cerro-concepcion-biobio',
        'region': 'biobio', 'sector': 'Chiguayante',
        'precio': 22_000_000, 'superficie': 4800,
        'descripcion': 'Parcela elevada en Chiguayante con vista al río Biobío. Excelente acceso por camino asfaltado. Electricidad trifásica disponible en predio. A 15 minutos del centro de Concepción.',
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': False, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': True, 'tiene_porton': True,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Algarrobal — Valparaíso',
        'slug': 'parcela-algarrobal-valparaiso',
        'region': 'valparaiso', 'sector': 'Casablanca',
        'precio': 38_000_000, 'superficie': 6200,
        'descripcion': 'Parcela en el Valle de Casablanca, reconocida zona vinícula. Suelo de alta calidad para vinos blancos y espumantes. Camino de acceso interior, cercado perimetral. A 30 min de Valparaíso y 1 hora de Santiago.',
        'destacada': False, 'estado': 'reservada',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': True, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': False, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Liucura — Los Ríos',
        'slug': 'parcela-liucura-los-rios',
        'region': 'los_rios', 'sector': 'Panguipulli',
        'precio': 29_500_000, 'superficie': 12000,
        'descripcion': 'Excepcional parcela de 1,2 hectáreas en la cuenca del lago Panguipulli. Acceso por camino ripiado mantenido. Electricidad en el camino a 200 m. Bosque nativo de arrayanes y tepas. Ideal para retiro, ecoturismo o cabaña en venta.',
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': False, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': True, 'tiene_cercado': False, 'tiene_porton': False,
        'es_turistico': True, 'bosque_nativo': True, 'rol_propio': True,
    },
    {
        'nombre': 'Parcela Los Boldos — Lampa',
        'slug': 'parcela-los-boldos-lampa',
        'region': 'metropolitana', 'sector': 'Lampa',
        'precio': 31_000_000, 'superficie': 5600,
        'descripcion': 'Sólida parcela en Lampa, comuna de alto crecimiento habitacional. Conexión eléctrica en terreno, red de agua y pavimento en la calle frontal. Zona con proyectos habitacionales aprobados. Ideal para dividir o construir.',
        'destacada': False, 'estado': 'disponible',
        'tiene_luz': True, 'tiene_agua': True, 'tiene_acceso': True,
        'vista_privilegiada': False, 'tiene_cercado': True, 'tiene_porton': True,
        'es_turistico': False, 'bosque_nativo': False, 'rol_propio': True,
    },
]

TESTIMONIOS = [
    {
        'nombre': 'Claudia Reyes',
        'profesion': 'Inversionista',
        'ciudad': 'Santiago',
        'texto': 'Compré mi parcela en Pirque con Leonardo y fue un proceso increíblemente sencillo. Todo en orden, escriturado en tiempo récord. 100% recomendado.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 1,
    },
    {
        'nombre': 'Rodrigo Molina',
        'profesion': 'Empresario',
        'ciudad': 'Concepción',
        'texto': 'Llevaba meses buscando una parcela en la VIII región. Leonardo me consiguió opciones que no encontré en ningún otro lado, con precios reales y documentación impecable.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 2,
    },
    {
        'nombre': 'Patricia Uribe',
        'profesion': 'Inversionista',
        'ciudad': 'Viña del Mar',
        'texto': 'Gracias a Punto Parcelas tengo mi inversión en Casablanca. El seguimiento fue excelente y la transparencia en todo el proceso me dio mucha confianza.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 3,
    },
    {
        'nombre': 'Héctor Sáez',
        'profesion': 'Arquitecto',
        'ciudad': 'Temuco',
        'texto': 'La parcela en Pucón superó todas mis expectativas. Vista al volcán, listo para construir. Proceso limpio y asesoría profesional en todo momento.',
        'estrellas': 5, 'es_placeholder': True, 'orden': 4,
    },
]


class Command(BaseCommand):
    help = 'Carga datos iniciales de parcelas, testimonios y superusuario'

    def handle(self, *args, **options):
        created_parcelas = 0
        for data in PARCELAS:
            slug = data.pop('slug', None)
            _, created = Parcela.objects.get_or_create(
                slug=slug or data['nombre'][:50],
                defaults=data,
            )
            if created:
                created_parcelas += 1

        created_testimonios = 0
        for data in TESTIMONIOS:
            _, created = Testimonio.objects.get_or_create(
                nombre=data['nombre'],
                defaults=data,
            )
            if created:
                created_testimonios += 1

        # Superusuario Leonardo
        if not User.objects.filter(username='leonardo').exists():
            User.objects.create_superuser(
                username='leonardo',
                password='PuntoParcelas2026!',
                email='hola@puntoparcelas.cl',
                first_name='Leonardo',
                last_name='Valencia',
            )
            self.stdout.write('Superusuario "leonardo" creado (clave: PuntoParcelas2026!)')

        self.stdout.write(
            self.style.SUCCESS(
                f'Seed OK — {created_parcelas} parcelas, {created_testimonios} testimonios creados.'
            )
        )
