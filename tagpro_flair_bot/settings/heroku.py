from base import *

DEBUG = False

WSGI_APPLICATION = 'tagpro_flair_bot.wsgi.heroku.application'

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] =  dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

if RAVEN_PUBLIC_KEY and RAVEN_PRIVATE_KEY and RAVEN_PROJECT_ID:
    RAVEN_CONFIG = {
        'dsn': 'https://%s:%s@app.getsentry.com/%s' % (
            RAVEN_PUBLIC_KEY, RAVEN_PRIVATE_KEY, RAVEN_PROJECT_ID)}

    INSTALLED_APPS = INSTALLED_APPS + (
        'raven.contrib.django.raven_compat',)

    MIDDLEWARE_CLASSES = (
        'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
        ) + MIDDLEWARE_CLASSES + (
        'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',)

try:
    from localsettings import *
except ImportError:
    pass
