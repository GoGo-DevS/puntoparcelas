from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-puntoparcelas-dev-only-7x9k2m4p1q8'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://puntoparcelas.cl',
    'https://www.puntoparcelas.cl',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site_globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

_ESTATICOS = {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'}

# ── DONDE VIVEN LAS FOTOS ────────────────────────────────────────────────────
# 20-08-2026: la cuenta de Cloudinary de este sitio quedo DESHABILITADA por
# pasarse del cupo gratis. Medido en vivo: cada foto devolvia
#     HTTP 401 · X-Cld-Error: cloud_name dd1ps0y8f is disabled
# o sea el sitio de un cliente pagado, en produccion y con dominio propio,
# quedo sin UNA sola foto.
#
# Cloudinary no cobra por GUARDAR sino por SERVIR, asi que el costo sube justo
# cuando al cliente le va bien. Cloudflare R2 no cobra egreso NUNCA: 10 GB
# gratis y despues US$0,015 por GB. Es la misma migracion que ya se hizo en
# Medina4x4, Villarreal y Popi.
#
# Cloudinary se deja como segunda opcion y NO se borra: si algun dia hay que
# volver, es cambiar una variable de entorno, no un despliegue.
R2_ACCESS_KEY = os.environ.get('R2_ACCESS_KEY_ID', '')
R2_SECRET_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '')
R2_BUCKET = os.environ.get('R2_BUCKET', '')
R2_ENDPOINT = os.environ.get('R2_ENDPOINT', '')
# URL publica del bucket (dominio propio de R2 o el r2.dev). Sin esto las fotos
# se guardan pero el navegador no sabe de donde bajarlas.
R2_PUBLIC_URL = os.environ.get('R2_PUBLIC_URL', '').rstrip('/')

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')

if R2_ACCESS_KEY and R2_SECRET_KEY and R2_BUCKET and R2_ENDPOINT:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {
                'access_key': R2_ACCESS_KEY,
                'secret_key': R2_SECRET_KEY,
                'bucket_name': R2_BUCKET,
                'endpoint_url': R2_ENDPOINT,
                # R2 no usa regiones como S3, pero boto3 exige una.
                'region_name': 'auto',
                # Las fotos de las parcelas son publicas: sin esto cada <img>
                # tendria que ir firmada y con vencimiento.
                'querystring_auth': False,
                'default_acl': None,      # R2 no implementa las ACL de S3
                'file_overwrite': False,  # no pisar una foto por nombre repetido
                'custom_domain': R2_PUBLIC_URL.replace('https://', '')
                                 .replace('http://', '') or None,
            },
        },
        'staticfiles': _ESTATICOS,
    }
elif CLOUDINARY_URL:
    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']
    STORAGES = {
        'default': {'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'},
        'staticfiles': _ESTATICOS,
    }
else:
    # Disco local. En Render esto se BORRA en cada despliegue: sirve para
    # desarrollo, no para produccion.
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': _ESTATICOS,
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'panel:login'
LOGIN_REDIRECT_URL = 'panel:dashboard'
LOGOUT_REDIRECT_URL = 'panel:login'

# Email
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_DESTINO = os.environ.get('EMAIL_DESTINO', 'hola@puntoparcelas.cl')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER or 'noreply@puntoparcelas.cl'
