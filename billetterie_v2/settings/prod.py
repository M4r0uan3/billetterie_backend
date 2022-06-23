import os

from billetterie_v2.settings.dev import SECRET_KEY
from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['ma-billetterie-prod.herokuapp.com']

SECRET_KEY = os.environ['SECRET_KEY']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
