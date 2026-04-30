"""Development settings."""
from .base import *
from decouple import config

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('MYSQLDATABASE', default='taskflow_db'),
        'USER': config('MYSQLUSER', default='root'),
        'PASSWORD': config('MYSQLPASSWORD', default=''),
        'HOST': config('MYSQLHOST', default='localhost'),
        'PORT': config('MYSQLPORT', default='3306'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
