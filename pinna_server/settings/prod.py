from __future__ import absolute_import
from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'fpe$gz=$que9h2517rv-(9+tjvtpa!f_1akp%g6@cf^u9q3!k%'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pinna',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}