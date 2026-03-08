# Deploy FERRETEROS en Render

## Stack

Python 3.11
Flask
Gunicorn
PostgreSQL

## Start Command

gunicorn wsgi:app

## Variables de entorno

SECRET_KEY
DATABASE_URL
FLASK_ENV=production

## Migraciones

flask db upgrade

## CI/CD

GitHub → Render auto deploy