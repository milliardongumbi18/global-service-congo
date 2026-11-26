# Global Service Congo

Plateforme de mise en relation entre clients, freelances et entreprises en RDC :
missions, candidatures, messagerie, avis et paiement avec séquestre (simulé en V1).

## Stack
Django 6.1 · Python 3.14 · PostgreSQL (Neon) · Tailwind CSS · HTMX · Render

## Lancer en local (Windows)
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # puis renseigner SECRET_KEY
python manage.py migrate
python manage.py runserver
```