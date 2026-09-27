# Physics Results Hub

A Flask + SQLAlchemy web app where students upload, search, view and download physics results; faculty/teachers have a separate administrator login.

## What was changed
- Student registration and student login are separate from Teacher/Admin login.
- Teacher/Admin accounts can manage the home-page notice.
- The home page now displays a persistent notice/reminder box for comments, submission dates and announcements.
- Student accounts are database records and are not recreated after the session expires.
- Login uses a 30-day remember cookie so students can return later without being forced to log in again during that period.
- Uploaded results remain linked to the student's account through `student_id` and appear in **My Uploads** after later logins.
- Results remain shared in the class Results page, as in the original application.

## IMPORTANT: persistence when deployed
The database and uploaded files must be placed on persistent storage. A normal SQLite file and `uploads/` directory can disappear if your hosting provider rebuilds/restarts an ephemeral server.

For production, preferably set:
```text
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST/DATABASE
DATA_DIR=/path/to/persistent/disk
UPLOAD_FOLDER=/path/to/persistent/disk/uploads
SECRET_KEY=<long-random-value>
```

If you are running the project locally on your computer, the default `data/physics_hub.db` and `data/uploads/` are persistent files and will remain after closing/restarting the app.

## Setup
```bash
python -m venv venv
venv\\Scripts\\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
python run.py
```
Then open `http://127.0.0.1:5000`.

## Teacher/Admin account
Register a normal student account first, then run:
```bash
python create_admin.py
```
Use the promoted account through **Teacher/Admin Login**. Do not register a teacher through the public student registration form.
