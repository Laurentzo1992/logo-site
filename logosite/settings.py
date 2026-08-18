from pathlib import Path
import  os
from decouple import config, Csv
from django.contrib.messages import constants as message_constants
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Active les en-têtes/cookies HTTPS uniquement une fois le site réellement
# servi en HTTPS (derrière un reverse proxy ou un PaaS qui termine le TLS).
# Mettre USE_HTTPS=True dans l'environnement de production une fois le
# certificat en place.
USE_HTTPS = config('USE_HTTPS', default=not DEBUG, cast=bool)

if USE_HTTPS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "siteweb",
    "blog",
    "catalog",
    "about",
    "connexion",
    "tinymce",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "logosite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR.joinpath('templates'),
                 BASE_DIR.joinpath('static')
                 ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "logosite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASE_URL = config(
    'DATABASE_URL',
    default='postgres://{user}:{password}@{host}:{port}/{name}'.format(
        user=config('DB_USER', default='logosite'),
        password=config('DB_PASSWORD', default='logosite'),
        host=config('DB_HOST', default='db'),
        port=config('DB_PORT', default='5432'),
        name=config('DB_NAME', default='logosite'),
    ),
)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=config('DB_SSL_REQUIRE', default=False, cast=bool),
    )
}
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "fr-fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / 'static'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "logosite/static")
]

MEDIA_URL = '/images/'
MEDIA_ROOT = os.path.join(BASE_DIR, "logosite/static/images")

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# Default primary key field type


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MESSAGE_TAGS = {
    message_constants.ERROR: "danger",
}

LIBELLE_FILE_DIR = BASE_DIR / 'libelle'



TINYMCE_DEFAULT_CONFIG = {
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'width': 1200,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': 'link image',
    'images_file_types': 'jpg,svg,webp'
}

TINYMCE_JS_URL = os.path.join(BASE_DIR, "logosite/static/tinymce/js/tinymce/tinymce.min.js")



# Production mode

# TINYMCE_JS_URL = os.path.join(BASE_DIR, "static/tinymce/js/tinymce/tinymce.min.js")
TINYMCE_JS_URL = 'https://cdn.tiny.cloud/1/n5qu4r62gjp1qb6xssmi5fox13hr8nwaq4dcf2sc969zf3bs/tinymce/7/tinymce.min.js'
TINYMCE_COMPRESSOR = False



# Email setting

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'ssl0.ovh.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')