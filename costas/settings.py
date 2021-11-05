import os
import django_heroku
import dj_database_url
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_KEY = 'pk_test_51H1OafE3YTenXSzfecGaACyMkoh9MtZy2PXiqmLadSwnEzODKRBoWnGMeqWoO3K3EMDTj3tDnlwIeHah5kTjqsLq00eZj4z5WG'
SECRET_KEY = 'sk_test_51H1OafE3YTenXSzf4hDhTVGnjmRJQa6vvnhGzgv9nQMf7FKIYilKeprkktpl4GnvUkwRlMmtCUSQQuOZhfIZMaau00IBxGfxmW'
WEBHOOK_SECRET = 'whsec_qIZQ7psuAA4NhQZwXooNpJorQVdDDGjH'

ALLOWED_HOSTS = ['rocky-waters-53961.herokuapp.com', '127.0.0.1:8000']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'paypal.standard.ipn',
    'django_countries',
    'crispy_forms',
    'cloudinary',
    'django_cleanup.apps.CleanupConfig',
    'core'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'costas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.custom_context_processor.get_context_data'
            ],
        },
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

PAYPAL_RECEIVER_EMAIL = 'sb-vibcr8298370@business.example.com'

PAYPAL_TEST = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

if ENVIRONMENT == 'production':
    DEBUG = False
    PUBLIC_KEY = os.getenv('PUBLIC_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Auth related stuff
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

LOGIN_REDIRECT_URL = '/'            #To redirect user after logging in to the homepage

# CRISPY FORMS

CRISPY_TEMPLATE_PACK = "bootstrap4"

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNT_EMAIL_VERIFICATION = "none"

PAYPAL_BUY_BUTTON_IMAGE = "https://www.paypalobjects.com/webstatic/en_US/i/buttons/cc-badges-ppppcmcvdam.png"


django_heroku.settings(locals())

# adding config
cloudinary.config( 
  cloud_name = "ezekielcloud", 
  api_key = "454864669193459", 
  api_secret = "PjBovHpe40O-Jd3yFvePFSvdfDo" 
)