from django.db import models
from django.utils.text import slugify


REGIONES = [
    ('metropolitana', 'Región Metropolitana'),
    ('valparaiso',    'Valparaíso'),
    ('ohiggins',      "O'Higgins"),
    ('maule',         'Maule'),
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
    precio       = models.BigIntegerField(default=0, help_text='Precio en CLP')
    superficie   = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Superficie en m²')
    descripcion  = models.TextField(blank=True)
    destacada    = models.BooleanField(default=False)
    estado       = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')

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
        return f"${self.precio:,}".replace(',', '.')

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

    @property
    def estado_color(self):
        return {'disponible': '#22C55E', 'reservada': '#EAB308', 'vendida': '#EF4444'}.get(self.estado, '#888')


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


class Consulta(models.Model):
    ESTADO_CHOICES = [
        ('nueva',       'Nueva'),
        ('contactado',  'Contactado'),
        ('en_proceso',  'En proceso'),
        ('cerrada',     'Cerrada'),
    ]

    nombre           = models.CharField(max_length=120)
    email            = models.EmailField(blank=True)
    telefono         = models.CharField(max_length=30)
    region_interes   = models.CharField(max_length=20, choices=REGIONES, blank=True)
    monto_disponible = models.BigIntegerField(null=True, blank=True, help_text='Presupuesto aprox CLP')
    parcela          = models.ForeignKey(Parcela, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='consultas')
    mensaje          = models.TextField(blank=True)
    estado           = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='nueva')
    notas            = models.TextField(blank=True, help_text='Notas internas')
    creado           = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'

    def __str__(self):
        return f"{self.nombre} ({self.telefono}) — {self.get_estado_display()}"

    @property
    def monto_display(self):
        if not self.monto_disponible:
            return 'No especificado'
        return f"${self.monto_disponible:,}".replace(',', '.')
