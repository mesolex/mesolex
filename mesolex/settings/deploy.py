from .base import *

ENVIRONMENT = os.environ['ENVIRONMENT']

DEBUG = False

DATABASES['default']['NAME'] = os.environ.get('DB_NAME', 'mesolex_%s' % ENVIRONMENT.lower())
DATABASES['default']['USER'] = os.environ.get('DB_USER', 'mesolex_%s' % ENVIRONMENT.lower())
DATABASES['default']['PASSWORD'] = os.environ.get('DB_PASSWORD', '')

ALLOWED_HOSTS = [os.environ['DOMAIN']] + [
    dn for dn in os.environ.get('ADDITIONAL_DOMAINS', '').split(',') if dn
]

WEBSERVER_ROOT = '/var/www/mesolex/'
PUBLIC_ROOT = os.path.join(WEBSERVER_ROOT, 'public')
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')
MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'media')

