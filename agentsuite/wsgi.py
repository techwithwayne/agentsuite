import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# ✅ Define project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Set default settings module for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agentsuite.settings')

# ✅ Load secrets from .env manually (if needed)
env_path = BASE_DIR / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ.setdefault(key, value)

# ✅ ENVIRONMENT VARIABLES (from your .env)
os.environ['OPENAI_API_KEY'] = "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"
os.environ['DJANGO_SECRET_KEY'] = "taxz2b2nb4a45%w0k9tau@x4a&o-mvfi)&s%swb05uab*()*5a"
os.environ['DEBUG'] = "False"
os.environ['STRIPE_SECRET_KEY'] = "sk_test_51RgzhFQI8qTNz4xlz055Q5TY6D9HDAS9ofVvewQ0SXT9ltxjA3M2isa4tjIw6d5scsSGdtQQWNEOA5f2jE3cb0HV00jwIDf9C6"
os.environ['STRIPE_PUBLISHABLE_KEY'] = "pk_test_51RgzhFQI8qTNz4xldneGig5GmOcpuOF9LmDK5lVECfitbFd32J3erY4ycLeA8erfYNSW3nQKa7Ta8IvBXmNidotI00T7Ciqjui"
os.environ['STRIPE_SUCCESS_URL'] = "https://apps.techwithwayne.com/success/"
os.environ['STRIPE_CANCEL_URL'] = "https://apps.techwithwayne.com/cancel/"
os.environ['STRIPE_WEBHOOK_SECRET'] = "whsec_2cc0efe64e1d8055f643f17d13a4c5a4d027717208d7de5e5a71d345ac58be58"
os.environ['EMAIL_HOST_PASSWORD'] = "Tylerhaller!23"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
