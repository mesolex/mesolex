import sys

from mesolex.settings.base import *  # noqa

DEBUG = True

SECRET_KEY = os.environ.get('SECRET_KEY', 'hlm&v%v5685+3@5kz359#3dla==vccyz$8fs!tvy8s$1#3hr-*')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'log/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'lexicon.management.commands.import_data': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

CORS_ALLOWED_ORIGINS = [
    'http://localhost:9000',
]