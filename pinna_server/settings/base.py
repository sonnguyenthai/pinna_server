"""
Django settings for pinna_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os


############ DJANGO BASE CONFIGURATIONS
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname((os.path.dirname(os.path.dirname(__file__))))

ALLOWED_HOSTS = []

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'pinax_theme_bootstrap',
    'bootstrapform',
    'account',
    'south',
    'pinna',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pinna_server.urls'

WSGI_APPLICATION = 'pinna_server.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    #'account.context_processors.account' # For django account.
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
TEMPLATE_DIRS = (
    os.path.normpath(os.path.join(BASE_DIR, 'templates')),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'assets'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    os.path.normpath(os.path.join(BASE_DIR, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760

# Logging
PINNA_LOG_FILE = "logs/pinna.log"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, PINNA_LOG_FILE),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}
########## END OF DJANGO BASE CONFIGURATIONS

########## DJANGO REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'pinna.api_authentication.APIAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'EXCEPTION_HANDLER': 'pinna.api_authentication.custom_exception_handler',

}
########## END OF DJANGO REST FRAMEWORK CONFIGURATION

########## USER ACCOUNT CONFIGURATION

ACCOUNT_OPEN_SIGNUP = False

LOGIN_URL = "/login"

ACCOUNT_LOGIN_URL = "pinna_login"

ACCOUNT_NOTIFY_ON_PASSWORD_CHANGE = False

ACCOUNT_LOGIN_REDIRECT_URL = "/"

########## END USER ACCOUNT CONFIGURATION

########## PINNA CONFIGURATION
# Expiration time of user logged session
PINNA_SESSION_EXPIRATION_TIME = 24*30

# Expiration time of a track
PINNA_TRACK_EXPIRATION_TIME = 24*3600

# Credentials for mobile client
PINNA_CLIENT_APP_ID = "abc"
PINNA_CLIENT_APP_KEY = "1234"

# Header name for API request
PINNA_APP_ID_HEADER = "PINNA_APPLICATION_ID"
PINNA_APP_KEY_HEADER = "PINNA_APPLICATION_KEY"
PINNA_AUTH_TOKEN_HEADER = "PINNA_AUTHENTICATED_TOKEN"

# Amazon CloudFront URL for user profile
PINNA_AWS_USER_PROFILE_URL = "https://d99edoy1nujid.cloudfront.net"
# Cloudfront distribution id
PINNA_AWS_USER_PROFILE_ID = "E3HWN47998LE8T"
PINNA_USER_PROFILE_BUCKET = "pinna-user-profile"

# Amazon CloudFront URL for music data
PINNA_AWS_MUSIC_DATA_URL = "https://d2k0rohda32b2b.cloudfront.net" #"http://s3gl0b7falyqyx.cloudfront.net"
# Cloudfront distribution id
PINNA_AWS_MUSIC_DATA_ID = "E15JFEQ2UVU8OI" #"E23SZVUD902VLM"
PINNA_MUSIC_BUCKET = "pinna-music-data"

# AWS Access Keys
PINNA_AWS_ACCESS_KEY_ID = "AKIAI6OZCBLHHH6KDNDA"
PINNA_AWS_SECRET_KEY_ID = "JrHV3a8UOxH+a2mpKjg/msfCSKptEtAbxSaqRYy3"

# CloudFront key pairs
SETTING_BASE_DIR = os.path.dirname(__file__)
PINNA_CLOUDFRONT_PUBLIC_KEY_FILE = os.path.join(
    SETTING_BASE_DIR, "cloudfront_keys/rsa-APKAJWBGE5RAERODGKPQ.pem")
PINNA_CLOUDFRONT_PRIVATE_KEY_FILE = os.path.join(
    SETTING_BASE_DIR, "cloudfront_keys/pk-APKAJWBGE5RAERODGKPQ.pem")
PINNA_CLOUDFRONT_KEY_ID = "APKAJWBGE5RAERODGKPQ"

PINNA_NUMBER_OF_TRACKS_PER_PAGE = 100

# Trending station
PINNA_TRENDING_STATION_TIME = 24*7*2 # hours of 2 weeks
PINNA_NUMBER_OF_TRENDING_STATIONS = 20 # 20 stations in trending top

# Google Play Public Key
PINNA_GOOGLE_PLAY_PKEY = 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4qSfI6gQ/' \
                         'T6YtGUSaQF4l7bUr+JFkAwACVCv9q33+2MfPYqnIcoWbdluULmjy9' \
                         'ieGOATYzT++pcPyeJz5kcLaGuxAQUsdxW6nsvkErtQAkXkXldsqWG' \
                         'BtCgdcR6czpOIhiqQ9jvXv7t+fYCoAXzjI2ShCSJvtVCG8k8r5WH1' \
                         'q/Vy+7tuwTmq+CvpEQoBKwHLPk7DflyOJPnPldLW9N8yjG+52fcie' \
                         'w0899dycvw+yDxmiYh5t6qg/MX9hwzQ0QNjsQDcAOIathWgXSym/8' \
                         'dmVZ+umJwnwh6rf52albAZhK+ul3api/jeI4NxDn7OeSkIMrdh076A2WlbUS2c6mgr8QIDAQAB'

# Pinna Setting ID: Row ID in the database of Pinna settings
PINNA_SETTING_ID = "FkAwACVCv9q33+2M"
