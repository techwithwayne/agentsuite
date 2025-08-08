from pathlib import Path
import os
from dotenv import load_dotenv

project_folder = os.path.expanduser('~/agentsuite')  # This works on PythonAnywhere
load_dotenv(os.path.join(project_folder, '.env'))

# Then, set SECRET_KEY
DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not DJANGO_SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY must be set in .env file")
SECRET_KEY = DJANGO_SECRET_KEY

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent



DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "apps.techwithwayne.com",
    "techwithwayne.pythonanywhere.com",
] + (os.getenv("ADDITIONAL_HOSTS", "").split(",") if os.getenv("ADDITIONAL_HOSTS") else [])

# ✅ CSRF Trusted Origins for iframe/subdomain POST support
CSRF_TRUSTED_ORIGINS = [
    "https://promptopilot.com",
    "https://tools.promptopilot.com",
    "https://ai.promptopilot.com",
    "https://showcase.techwithwayne.com",
    "https://apps.techwithwayne.com",
]

# Installed apps
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "webdoctor",
    "captcha",

    # Apps being built
    "personal_coach",
    "promptopilot",

    "website_analyzer",
    "barista_assistant",
    "barista_assistant.menu",
    "barista_assistant.orders",
    "content_strategy_generator_agent",
    "rest_framework",
]
INSTALLED_APPS += ["django_extensions"]

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # ✅ required before CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL configuration
ROOT_URLCONF = "agentsuite.urls"

# Template configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = "agentsuite.wsgi.application"

# ✅ DATABASE WITH OPTIMIZATIONS
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
        "OPTIONS": {
            "timeout": 30,
        }
    }
}

# Password validation
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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ✅ ENHANCED SECURITY SETTINGS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'ALLOW-FROM https://showcase.techwithwayne.com'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"

# Add this for local development to serve app-level static files like PromptoPilot
# STATICFILES_DIRS = [
#     BASE_DIR / "promptopilot" / "static",
# ]

# Where collectstatic will place files for production
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise for static file serving in production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

def set_cors_headers(headers, path, url):
    """Enhanced CORS headers for static files"""
    if path.endswith((".css", ".js")):
        headers["Access-Control-Allow-Origin"] = "*"
        headers["Cache-Control"] = "public, max-age=31536000"

WHITENOISE_ADD_HEADERS_FUNCTION = set_cors_headers

def set_custom_headers(headers, path, url):
    if path.endswith(".css") or path.endswith(".js"):
        headers["Access-Control-Allow-Origin"] = "*"

WHITENOISE_ADD_HEADERS_FUNCTION = set_custom_headers

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

if not all([EMAIL_HOST_USER, EMAIL_HOST_PASSWORD]):
    print("⚠️  EMAIL configuration incomplete - email features will be disabled")

# ✅ OPENAI CONFIGURATION WITH VALIDATION
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

CORS_ALLOWED_ORIGINS = [
    "https://showcase.techwithwayne.com",
    "https://apps.techwithwayne.com",
    "https://promptopilot.com",
    "https://tools.promptopilot.com",
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]

CORS_ALLOW_CREDENTIALS = True  # ✅ Allow cookies/auth headers across domains
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS


# ✅ Extra Security Headers for production
SESSION_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_SSL_REDIRECT = not DEBUG  # redirect only if in prod

# ✅ SESSION CONFIGURATION
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ✅ Logging for production diagnostics
# ✅ COMPREHENSIVE LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'webdoctor.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'webdoctor': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Stripe configuration (commented out if unused)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
