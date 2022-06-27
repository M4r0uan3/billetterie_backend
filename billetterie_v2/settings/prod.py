import os
import dj_database_url
from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
ALLOWED_HOSTS = ['mabilletterie-prod.herokuapp.com']

SECRET_KEY = os.environ['SECRET_KEY']

DATABASES = {
    'default': dj_database_url.config()
}


CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dlxjpwigp',
    'API_KEY': '238828169723339',
    'API_SECRET': 'HxnDwjcNNWVmOHqNOd3uAJZ7wfk',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.RawMediaCloudinaryStorage'
