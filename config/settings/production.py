from .base import *
DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS = [value.strip() for value in os.environ['DJANGO_ALLOWED_HOSTS'].split(',') if value.strip()]
CSRF_TRUSTED_ORIGINS = [value.strip() for value in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if value.strip()]
STORAGES['staticfiles']['BACKEND'] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'true').lower() == 'true'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# Enable only behind a trusted proxy that overwrites X-Forwarded-Proto.
if os.getenv('TRUST_PROXY_HEADERS', 'false').lower() == 'true':
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
