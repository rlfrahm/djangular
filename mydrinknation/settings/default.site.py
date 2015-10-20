# THIS IS UNIQUE FOR EACH ENVIRONMENT
# THIS IS NOT TRACKED BY GIT

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!+=s&=o_x8t^j8b0(-bb$*%6@f7g+f6^wmirwu6k(rr2r28l#)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        # 'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'NAME': 'django',
        # 'USER': 'django',
        # 'PASSWORD': 'password',
        # 'HOST': 'localhost',
        # 'PORT': '',
    }
}

# http://stackoverflow.com/a/26219292/2824391
# IF SQLITE3 Uncomment This!
# from django.db.backends.signals import connection_created
# from django.dispatch import receiver
# import math
#
# @receiver(connection_created)
# def extend_sqlite(connection=None, **kwargs):
#     if connection.vendor == "sqlite":
#         # sqlite doesn't natively support math functions, so add them
#         cf = connection.connection.create_function
#         cf('acos', 1, math.acos)
#         cf('cos', 1, math.cos)
#         cf('radians', 1, math.radians)
#         cf('sin', 1, math.sin)

#For email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email@gmail.com'
EMAIL_HOST_PASSWORD = ''

# Haystack Search (Solr)
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}

# Set this to true if you want to disable registration of new accounts
SIGN_UP_LOCKED = False

# Set this to true if you want to include google analytics
ANALYTICS = False
