"""
WSGI entrypoint para producción.

Gunicorn ejecuta:
gunicorn wsgi:app
"""

from app import create_app

app = create_app()