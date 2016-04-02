# -*- coding: utf-8 -*-
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../')


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '=r#xr(wfdh@*)a8omuulxg25&xhh2mpbla#0hb!1&*w5p7+8&)')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# Static asset configuration
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'raven.contrib.django.raven_compat',
    'social.apps.django_app.default',

    'tagpro_flair_bot',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'social.apps.django_app.context_processors.backends',
    'social.apps.django_app.context_processors.login_redirect',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates/"),)

AUTH_USER_MODEL = 'tagpro_flair_bot.TagProUser'

AUTHENTICATION_BACKENDS = (
    'social_auth.backend.RedditOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

GOOGLE_ANALYTICS_TRACKING_ID = os.environ.get('GOOGLE_ANALYTICS_TRACKING_ID', None)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'social_auth.pipeline.set_token'
)

SOCIAL_AUTH_DISCONNECT_PIPELINE = (
    'social.pipeline.disconnect.get_entries',
    'social.pipeline.disconnect.revoke_tokens',
    'social.pipeline.disconnect.disconnect',
    'social_auth.pipeline.deauth_tagpro'
)

SOCIAL_AUTH_REDDIT_KEY = os.environ.get('SOCIAL_AUTH_REDDIT_KEY', None)
SOCIAL_AUTH_REDDIT_SECRET = os.environ.get('SOCIAL_AUTH_REDDIT_SECRET', None)
SOCIAL_AUTH_REDDIT_KEY_SECURE = os.environ.get('SOCIAL_AUTH_REDDIT_KEY_SECURE', None)
SOCIAL_AUTH_REDDIT_SECRET_SECURE = os.environ.get('SOCIAL_AUTH_REDDIT_SECRET_SECURE', None)

RAVEN_PUBLIC_KEY = os.environ.get('RAVEN_PUBLIC_KEY', None)
RAVEN_PRIVATE_KEY = os.environ.get('RAVEN_PRIVATE_KEY', None)
RAVEN_PROJECT_ID = os.environ.get('RAVEN_PROJECT_ID', None)

REDDIT_MOD_USERNAME = os.environ.get('REDDIT_MOD_USERNAME', None)
REDDIT_MOD_PASSWORD = os.environ.get('REDDIT_MOD_PASSWORD', None)
REDDIT_MOD_SUBREDDIT = os.environ.get('REDDIT_MOD_SUBREDDIT', None)
REDDIT_WIKI_SUBREDDIT = os.environ.get('REDDIT_WIKI_SUBREDDIT', None)
REDDIT_WIKI_PAGE = os.environ.get('REDDIT_WIKI_PAGE', None)
REDDIT_MAX_RETRIES = 5


BOT_USER_AGENT = "/r/tagpro flair helper"

LOGIN_REDIRECT_URL = '/'
LOGIN_ERROR_URL = '/'

# Set to your TagPro name to avoid needing to change it to a token
TAGPRO_AUTH_TOKEN_OVERRIDE = os.environ.get('TAGPRO_AUTH_TOKEN_OVERRIDE', None)

ROOT_URLCONF = 'tagpro_flair_bot.urls'

WSGI_APPLICATION = 'tagpro_flair_bot.wsgi.development.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
