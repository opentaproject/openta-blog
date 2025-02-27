import os
import sys
from django.core.management import call_command

"""
Django settings for blog project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
from django.core.management import call_command
from .util import create_database_if_not_exists


from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$a%sbcorrazhwe7j63jjxynztgbz9xh6$9x8x!b$suwawrx+o="

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://www.openta.se',
    'http://ffm516-2023.localhost:8000',
    'http://*.localhost:8080',
    'https://instructure.com',
    'http://127.0.0.1:8000',
    'https://*',
    'http://*',
]



# Application definition

INSTALLED_APPS = [
    'grappelli',
    "django.contrib.admin",
    "django.contrib.humanize",
    'filebrowser',
    'lti_provider',
    "django_ckeditor_5",
    "users",
    "blog.apps.BlogConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    #'backend.middleware.rewrite_response.ResponseRewriteMiddleware', 
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [ f"{BASE_DIR}/blog/templates/", ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": BASE_DIR / "db.sqlite3",
#    }
#}

STATIC_ROOT = os.path.join(BASE_DIR, "deploystatic")
ATOMIC_REQUESTS = False
PGHOST = os.environ.get("PGHOST", "localhost")
PGPASSWORD = os.environ.get("PGPASSWORD")
PGUSER = os.environ.get("PGUSER")
PGDATABASE = os.environ.get('PGDATABASE')
PGDATABASE_NAME = os.environ.get('PGDATABASE_NAME','default')


DATABASES = {
     PGDATABASE_NAME : {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": PGDATABASE,
        "USER": PGUSER,
        "PASSWORD": PGPASSWORD,
        "HOST": PGHOST,
        "PORT": 5432,
        "ATOMIC_REQUESTS": ATOMIC_REQUESTS,
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Stockholm"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SUBDOMAIN = os.environ.get('SUBDOMAIN','blog')
db = DATABASES[PGDATABASE_NAME];
db_name = db['NAME'];
host = db['HOST'];
user = db['USER'];
password = db['PASSWORD']
superuser = os.environ.get("SUPERUSER", 'super')
superuser_password = os.environ.get("SUPERUSER_PASSWORD",'')
SUPERUSER=superuser
SUPERUSER_PASSWORD=superuser_password

create_database_if_not_exists(db_name, host,user, password , superuser, superuser_password) 



#MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = f'/subdomain-data/{SUBDOMAIN}/media'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
RUNNING_DEVSERVER = 'runserver' in sys.argv
if RUNNING_DEVSERVER :
    STATIC_URL = '/deploystatic/'

FILEBROWSER_ROOT = MEDIA_ROOT  # os.path.join(MEDIA_ROOT, 'uploads')
FILEBROWSER_DIRECTORY = ''
os.makedirs(os.path.join( FILEBROWSER_ROOT, '_versions') ,exist_ok=True)

#CKEDITOR_UPLOAD_PATH = 'uploads/'
#CKEDITOR_IMAGE_BACKEND = "pillow"
#CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js' 
#CKEDITOR_CONFIGS = {
#    'default':
#        {
#            'toolbar': 'full',
#            'width': 'auto',
#            'extraPlugins': ','.join([
#                'codesnippet',
#            ]),
#        },
#}


customColorPalette = [
      {
          'color': 'hsl(4, 90%, 58%)',
          'label': 'Red'
      },
      {
          'color': 'hsl(340, 82%, 52%)',
          'label': 'Pink'
      },
      {
          'color': 'hsl(291, 64%, 42%)',
          'label': 'Purple'
      },
      {
          'color': 'hsl(262, 52%, 47%)',
          'label': 'Deep Purple'
      },
      {
          'color': 'hsl(231, 48%, 48%)',
          'label': 'Indigo'
      },
      {
          'color': 'hsl(207, 90%, 54%)',
          'label': 'Blue'
      },
  ]

#CKEDITOR_5_CUSTOM_CSS = 'path_to.css' # optional

CKEDITOR_5_CONFIGS = {
  'default': {
      'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                  'bulletedList', 'numberedList', 'blockQuote', 'fileUpload', ],

  },
  'extends': {
      'blockToolbar': [
          'paragraph', 'heading1', 'heading2', 'heading3',
          '|',
          'bulletedList', 'numberedList',
          '|',
          'blockQuote',
      ],
      'toolbar': ['heading', '|', 'outdent', 'indent', '|', 'bold', 'italic', 'link', 'underline', 'strikethrough',
      'code','subscript', 'superscript', 'highlight', '|', 'codeBlock', 'sourceEditing', 'insertImage',
                  'bulletedList', 'numberedList', 'todoList', '|',  'blockQuote', 'fileUpload', '|',
                  'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', 'mediaEmbed', 'removeFormat',
                  'insertTable',],
      'image': {
          'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft',
                      'imageStyle:alignRight', 'imageStyle:alignCenter', 'imageStyle:side',  '|'],
          'styles': [
              'full',
              'side',
              'alignLeft',
              'alignRight',
              'alignCenter',
          ]

      },
      'table': {
          'contentToolbar': [ 'tableColumn', 'tableRow', 'mergeTableCells',
          'tableProperties', 'tableCellProperties' ],
          'tableProperties': {
              'borderColors': customColorPalette,
              'backgroundColors': customColorPalette
          },
          'tableCellProperties': {
              'borderColors': customColorPalette,
              'backgroundColors': customColorPalette
          }
      },
      'heading' : {
          'options': [
              { 'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph' },
              { 'model': 'heading1', 'view': 'h1', 'title': 'Heading 1', 'class': 'ck-heading_heading1' },
              { 'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2' },
              { 'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3' }
          ]
      }
  },
  'list': {
      'properties': {
          'styles': 'true',
          'startIndex': 'true',
          'reversed': 'true',
      }
  }
}


# Define a constant in settings.py to specify file upload permissions
#CKEDITOR_5_FILE_UPLOAD_PATH = f"/subdomain_data/{SUBDOMAIN}/media/"  # Possible values: "staff", "authenticated", "any"
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "any"
CKEDITOR_5_FILE_STORAGE = "backend.util.CustomStorage" # optional

#CKEDITOR_5_CONFIGS  = 'extended'
CKEDITOR_ALLOW_NONIMAGE_FILES = True
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'pdf', 'png','csv','xlsx','doc','docx','zip','tex','py','tgz','xmind'] # optional
CKEDITOR_5_MAX_FILE_SIZE = 50
AUTHENTICATION_BACKENDS = [
  'django.contrib.auth.backends.ModelBackend',
  'lti_provider.auth.LTIBackend',
]

LTI_TOOL_CONFIGURATION = {
    'title': 'OpenTA-blog',
    'description': 'Blog to support OpenTA',
    'launch_url': 'lti/',
    'embed_url': '',
    'embed_icon_url': '',
    'embed_tool_id': 'openta-blog-0',
    #'landing_url': 'http://localhost:8000/lti_landing',
    'course_aware': False,
    'course_navigation': False,
    'new_tab': True,
    'frame_width': 1024,
    'frame_height': 960,
    'custom_fields': None,
    'allow_ta_access': False,
}

#SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
#SESSION_COOKIE_SAMESITE = 'None'
#SESSION_COOKIE_SECURE = True
LTI_KEY =  os.environ.get('LTI_KEY', 'lti-key')
LTI_SECRET = os.environ.get('LTI_SECRET', 'lti-secret')

PYLTI_CONFIG = {
    'consumers': {
        LTI_KEY : {
            'secret': LTI_SECRET
        }
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
LTI_EXTRA_PARAMETERS = ["custom_canvas_login_id"]
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['null'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
print(f"PGDATABAS {PGDATABASE}")
HIDE_UUID = True
