# api/wsgi.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hootel.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()  # Vercel looks for `app`
