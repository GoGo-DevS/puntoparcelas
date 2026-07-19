import os

from django.db import models
from django.utils.text import slugify


def _geo_pdf_storage():
    """Use RawMediaCloudinaryStorage in production so PDFs upload as raw (not image)."""
    if os.environ.get('CLOUDINARY_URL'):
        from cloudinary_storage.storage import RawMediaCloudinaryStorage
        return RawMediaCloudinaryStorage()
    from django.core.files.storage import FileSystemStorage
    return FileSystemStorage()


REGIONES = [
    ('coquimbo',      'Coquimbo'),
    ('valparaiso',    'Valparaíso'),
    ('metropolitana', 'Región Metropolitana'),
    ('ohiggins',      "O'Higgins"),
    ('maule',         'Maule'),
    ('nuble',         'Ñuble'),
    ('biobio',        'Biobío'),
    ('araucania',     'La Araucanía'),
    ('los_rios',      'Los Ríos'),
    ('los_lagos',     'Los Lagos'),
    ('aysen',         'Aysén'),
    ('otro',          'Otra región'),
]


class Parcela(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada',  'Reservada'),
        ('vendida',    'Vendida'),
    ]

    nombre       = models.CharField(max_length=200)
    slug         = models.SlugField(max_length=200, unique=True, blank=True)
    region       = models.CharField(max_length=20, choices=REGIONES, default='metropolitana')
    sector       = models.CharField(max_length=120, blank=True, help_text='Ej: Colina, Pirque, Lampa')
    MONEDA_CHOICES = [('CLP', 'CLP ($)'), ('UF', 'UF')]

    precio       = models.BigIntegerField(default=0, help_text='Número sin puntos ni comas')
    moneda       = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='CLP')
    superficie   = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Superficie en m²')
    descripcion  = models.TextField(blank=True)
    destacada    = models.BooleanField(default=False)
    estado       = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')
    video_url      = models.URLField(blank=True, help_text='URL de YouTube (ej: https://youtu.be/XXX)')
    mapa_url       = models.URLField(blank=True, help_text='URL de Google Maps (link de compartir, para el botón)')
    mapa_embed_url = models.URLField(blank=True, help_text='URL embed de Google Maps (para mostrar el mapa en la web)')
    geo_pdf        = models.FileField(upload_to='geo/', blank=True, help_text='Plano GEO en PDF',
                                      storage=_geo_pdf_storage)

    # Atributos booleanos
    tiene_luz           = models.BooleanField(default=False, verbose_name='Luz eléctrica')
    tiene_agua          = models.BooleanField(default=False, verbose_name='Agua potable')
    tiene_acceso        = models.BooleanField(default=False, verbose_name='Acceso pavimentado')
    vista_privilegiada  = models.BooleanField(default=False, verbose_name='Vista privilegiada')
    tiene_cercado       = models.BooleanField(default=False, verbose_name='Cercado perimetral')
    tiene_porton        = models.BooleanField(default=False, verbose_name='Portón de acceso')
    es_turistico        = models.BooleanField(default=False, verbose_name='Uso turístico permitido')
    bosque_nativo       = models.BooleanField(default=False, verbose_name='Bosque nativo')
    rol_propio          = models.BooleanField(default=False, verbose_name='Rol propio / Escriturado')

    creado      = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-destacada', 'precio']
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'

    def __str__(self):
        return f"{self.nombre} — {self.get_region_display()}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)[:180] or 'parcela'
            slug = base
            i = 2
            while Parcela.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def foto_principal_url(self):
        foto = self.fotos.filter(principal=True).first() or self.fotos.first()
        if foto and foto.imagen:
            try:
                return foto.imagen.url
            except ValueError:
                pass
        return ''

    @property
    def precio_clp(self):
        if not self.precio:
            return 'Consultar'
        num = f"{self.precio:,}".replace(',', '.')
        return f"UF {num}" if self.moneda == 'UF' else f"${num}"

    def _youtube_id(self):
        if not self.video_url:
            return ''
        import re
        m = re.search(r'(?:v=|youtu\.be/|embed/|shorts/|live/)([A-Za-z0-9_-]{11})', self.video_url)
        return m.group(1) if m else ''

    @property
    def video_id(self):
        return self._youtube_id()

    @property
    def video_embed_url(self):
        vid = self._youtube_id()
        return f"https://www.youtube.com/embed/{vid}" if vid else ''

    @property
    def video_thumbnail_url(self):
        vid = self._youtube_id()
        return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg" if vid else ''

    @property
    def superficie_display(self):
        ha = self.superficie / 10000
        if ha >= 1:
            return f"{ha:,.2f} ha".replace(',', '.')
        return f"{int(self.superficie):,} m²".replace(',', '.')

    @property
    def atributos_activos(self):
        attrs = []
        if self.tiene_luz:          attrs.append(('luz',     'bi-lightning-charge-fill', 'Luz eléctrica'))
        if self.tiene_agua:         attrs.append(('agua',    'bi-droplet-fill',          'Agua potable'))
        if self.tiene_acceso:       attrs.append(('acceso',  'bi-signpost-2-fill',       'Acceso pavimentado'))
        if self.vista_privilegiada: attrs.append(('vista',   'bi-binoculars-fill',       'Vista privilegiada'))
        if self.tiene_cercado:      attrs.append(('cercado', 'bi-border-all',            'Cercado'))
        if self.tiene_porton:       attrs.append(('porton',  'bi-door-closed-fill',      'Portón'))
        if self.es_turistico:       attrs.append(('turistico','bi-camera-fill',          'Uso turístico'))
        if self.bosque_nativo:      attrs.append(('bosque',  'bi-tree-fill',             'Bosque nativo'))
        if self.rol_propio:         attrs.append(('rol',     'bi-file-earmark-check-fill','Rol propio'))
        return attrs

    def _mapa_coords(self):
        """Extract (lat, lng) from a Google Maps embed pb URL."""
        if not self.mapa_embed_url:
            return None, None
        import re
        m = re.search(r'!2d(-?\d+\.?\d*)!3d(-?\d+\.?\d*)', self.mapa_embed_url)
        if m:
            return m.group(2), m.group(1)  # lat, lng
        return None, None

    @property
    def mapa_embed_url_valid(self):
        """Return a reliable embed URL derived from coordinates in the pb URL."""
        lat, lng = self._mapa_coords()
        if lat and lng:
            return f'https://maps.google.com/maps?q={lat},{lng}&output=embed&hl=es'
        if self.mapa_embed_url and 'google.com/maps/embed' in self.mapa_embed_url:
            return self.mapa_embed_url
        return ''

    @property
    def geo_pdf_viewer_url(self):
        """Google Docs Viewer URL for opening the PDF in a new tab."""
        if not self.geo_pdf:
            return ''
        from urllib.parse import quote
        return f"https://docs.google.com/viewer?url={quote(self.geo_pdf.url, safe='')}"

    @property
    def estado_color(self):
        return {'disponible': '#22C55E', 'reservada': '#EAB308', 'vendida': '#EF4444'}.get(self.estado, '#888')


class PlanPago(models.Model):
    parcela        = models.ForeignKey(Parcela, on_delete=models.CASCADE, related_name='planes')
    nombre         = models.CharField(max_length=120)
    precio_contado = models.BigIntegerField(default=0, help_text='Precio al contado CLP')
    precio_credito = models.BigIntegerField(null=True, blank=True, help_text='Total crédito CLP')
    diferencia     = models.BigIntegerField(null=True, blank=True)
    pie            = models.BigIntegerField(null=True, blank=True)
    cuota          = models.BigIntegerField(null=True, blank=True, help_text='Cuota mensual CLP')
    num_cuotas     = models.IntegerField(null=True, blank=True)
    orden          = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Plan de Pago'
        verbose_name_plural = 'Planes de Pago'

    def __str__(self):
        return f"{self.nombre} — {self.parcela.nombre}"

    def _fmt(self, val):
        if val is None:
            return '—'
        return f"${val:,}".replace(',', '.')

    @property
    def contado_fmt(self): return self._fmt(self.precio_contado)
    @property
    def credito_fmt(self): return self._fmt(self.precio_credito)
    @property
    def diferencia_fmt(self): return self._fmt(self.diferencia)
    @property
    def pie_fmt(self): return self._fmt(self.pie)
    @property
    def cuota_fmt(self): return self._fmt(self.cuota)


class FotoParcela(models.Model):
    parcela   = models.ForeignKey(Parcela, on_delete=models.CASCADE, related_name='fotos')
    imagen    = models.ImageField(upload_to='parcelas/')
    principal = models.BooleanField(default=False)
    orden     = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-principal', 'orden']
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return f"Foto #{self.pk} — {self.parcela.nombre}"


class Testimonio(models.Model):
    nombre         = models.CharField(max_length=80)
    profesion      = models.CharField(max_length=80, blank=True, default='Inversionista')
    ciudad         = models.CharField(max_length=80, blank=True)
    texto          = models.TextField()
    estrellas      = models.PositiveSmallIntegerField(default=5)
    es_placeholder = models.BooleanField(default=True)
    activo         = models.BooleanField(default=True)
    orden          = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = 'Testimonio'
        verbose_name_plural = 'Testimonios'

    def __str__(self):
        tag = ' (placeholder)' if self.es_placeholder else ''
        return f"{self.nombre}{tag}"

    @property
    def inicial(self):
        partes = self.nombre.split()
        if len(partes) >= 2:
            return f"{partes[0][0]}.{partes[1][0]}."
        return self.nombre[0].upper() + '.'

    @property
    def rango_estrellas(self):
        return range(self.estrellas)


class SiteConfig(models.Model):
    foto_contacto = models.ImageField(upload_to='config/', blank=True, help_text='Foto de Leonardo en /contacto/')

    class Meta:
        verbose_name = 'Configuración del sitio'

    def __str__(self):
        return 'Configuración del sitio'

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Consulta(models.Model):
    ESTADO_CHOICES = [
        ('nueva',       'Nueva'),
        ('contactado',  'Contactado'),
        ('en_proceso',  'En proceso'),
        ('cerrada',     'Cerrada'),
    ]
    MONTO_RANGO_CHOICES = [
        ('menos_10m',  'Menos de $10.000.000'),
        ('10m_20m',    '$10.000.000 – $20.000.000'),
        ('20m_35m',    '$20.000.000 – $35.000.000'),
        ('35m_50m',    '$35.000.000 – $50.000.000'),
        ('mas_50m',    'Más de $50.000.000'),
    ]
    COMO_CHOICES = [
        ('instagram',  'Instagram'),
        ('referido',   'Referido de un amigo'),
        ('google',     'Google'),
        ('facebook',   'Facebook'),
        ('otro',       'Otro'),
    ]

    nombre              = models.CharField(max_length=120)
    email               = models.EmailField(blank=True)
    telefono            = models.CharField(max_length=30)
    region_interes      = models.CharField(max_length=20, choices=REGIONES, blank=True)
    monto_rango         = models.CharField(max_length=20, choices=MONTO_RANGO_CHOICES, blank=True)
    como_nos_conociste  = models.CharField(max_length=20, choices=COMO_CHOICES, blank=True)
    parcela             = models.ForeignKey(Parcela, on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='consultas')
    mensaje             = models.TextField(blank=True)
    estado              = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='nueva')
    notas               = models.TextField(blank=True, help_text='Notas internas')
    creado              = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'

    def __str__(self):
        return f"{self.nombre} ({self.telefono}) — {self.get_estado_display()}"

    @property
    def monto_display(self):
        return self.get_monto_rango_display() or 'No especificado'
