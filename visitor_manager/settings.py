import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# Security Key
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key_here")

DEBUG = False
ALLOWED_HOSTS = ['sarasotagospeltemple.com', 'www.sarasotagospeltemple.com', 'localhost', '127.0.0.1']

# Custom User Model
AUTH_USER_MODEL = 'visitors.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
# Installed Apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',  
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'visitors.apps.VisitorsConfig',  
    'crispy_forms',  
    'crispy_bootstrap5', 
    'compressor',  
    'whitenoise.runserver_nostatic', 
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL Configuration
ROOT_URLCONF = 'visitor_manager.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "visitors/templates", BASE_DIR / "templates"],  # Allow templates in both app and project levels
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            'builtins': ['crispy_forms.templatetags.crispy_forms_tags'],  # Enable crispy_forms tags globally
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'visitor_manager.wsgi.application'

# Database Configuration (MySQL on AWS RDS)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'church_visitors',
        'USER': 'admin',
        'PASSWORD': 'T5lDt7r4DFvoLymHzG0X',
        'HOST': 'database-1.c7kgaguqi1f0.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'init_command': "SET CHARACTER SET utf8mb4",  # Ensure UTF-8 encoding
        },
        'CONN_MAX_AGE': 600,  # Persistent connections for performance (optional)
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,  # Ensure passwords are at least 8 characters
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'  # Updated to Sarasota, FL timezone for relevance

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "node_modules",  # Include node_modules for local Font Awesome
]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compressor Settings
COMPRESS_URL = STATIC_URL  # Add this line to fix the AttributeError
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_ENABLED = True

# Media Files (Optional, for user-uploaded content)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media"

# Crispy Forms Settings
CRISPY_TEMPLATE_PACK = 'bootstrap5'  # Use Bootstrap 5 for crispy_forms

# Static File Compression and WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Firebase Settings
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS_PATH", str(BASE_DIR / "firebase-adminsdk.json"))  # Use Path for consistency

# SendGrid Settings
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "visit@sarasotagospeltemple.com")  # Default value for safety

# Clearstream Settings
CLEARSTREAM_API_KEY = os.getenv("CLEARSTREAM_API_KEY")
CLEARSTREAM_LIST_ID = os.getenv("CLEARSTREAM_LIST_ID", 284041)  # Default to integer if not set

# Authentication Settings
LOGIN_REDIRECT_URL = "/admin/"
LOGOUT_REDIRECT_URL = "/"  # Redirects users back to the visitor form after logout

# Security Settings
CSRF_COOKIE_SECURE = False  # Set to True for production with HTTPS
SESSION_COOKIE_SECURE = False  # Set to True for production with HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_SSL_REDIRECT = False  # Set to True for production with HTTPS
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (optional, for session duration)
SESSION_SAVE_EVERY_REQUEST = True  # Save session on every request for better tracking

# CORS Settings (Optional, if you need cross-origin requests)
# CORS_ALLOW_ALL_ORIGINS = False  # Set to True for development, False for production
# CORS_ALLOWED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Logging Configuration (Updated for Python 3.11 compatibility with workaround)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'encoding': 'utf-8',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'visitors': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Ensure UTF-8 encoding for console output globally (workaround for Python 3.11 issue)
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cache Settings (Optional for performance)
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
#         'LOCATION': 'unique-snowflake',
#     }
# }

# Debug Toolbar (Optional for Development)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
# INTERNAL_IPS = ['127.0.0.1']