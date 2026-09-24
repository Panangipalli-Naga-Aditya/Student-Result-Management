# Physics Results Hub
*One Platform. Every Result. Shared with the Class.*

A Flask + SQLAlchemy web app where students upload, search, view and download physics results; faculty moderate from an admin dashboard.

## Features
Registration/login (hashed passwords, session auth, CSRF), drag-and-drop upload with progress, extension + MIME + signature validation, UUID stored filenames, controlled view/download routes (login required), search/filter/sort on the backend, My Uploads with owner-only delete, Faculty dashboard (stats, recent uploads, delete with confirmation), responsive UI.

## Stack
Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF), python-dotenv · SQLite (dev) → PostgreSQL (set `DATABASE_URL`) · vanilla HTML/CSS/JS.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env  (then set SECRET_KEY)
python run.py                   # tables are created automatically; open http://127.0.0.1:5000
```
Environment variables: `SECRET_KEY`, `DATABASE_URL`, `MAX_UPLOAD_MB`.

## Admin account
Register normally, then run `python create_admin.py` (promotes/creates a faculty admin).

## Testing
`python -m unittest tests.test_app` (registration, login/logout, PDF/TXT/PNG/DOCX upload, invalid + oversized rejection, search, filter, view, download, student vs admin deletion). To test manually: register two accounts, upload a file with one, download it with the other.

## Deployment
```bash
pip install gunicorn psycopg2-binary
export SECRET_KEY=... DATABASE_URL=postgresql+psycopg2://user:pass@host/db
gunicorn "run:app"
```
Serve over HTTPS, and keep `uploads/` on persistent storage (or swap `app/utils/files.py` for S3). For schema changes later, add Flask-Migrate.
