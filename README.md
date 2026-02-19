# HRMS Lite

A small internal HR tool for managing employees and daily attendance. Add/delete employees, mark attendance (present/absent) by date, and filter or paginate lists. No login—single admin use.

---

## Tech stack

- **Backend:** Django 5.1, Python 3
- **Database:** SQLite (default)
- **Frontend:** Django templates, plain CSS, a bit of JS for modals and mobile filter popup
- **APIs:** A few JSON endpoints under `/api/employees/` and `/api/attendance/` for GET/POST if you want to hook something else up

---

## Run locally

```bash
# clone (creates hrms-lite folder)
git clone https://github.com/aryansingla/hrms-lite.git
cd hrms-lite

# optional: use a venv
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate

# install
pip install -r requirements.txt

# DB
python manage.py migrate

# run
python manage.py runserver
```

Open **http://127.0.0.1:8000/**. Dashboard is at `/`, employees at `/employees/`, attendance at `/attendance/`.

---

## Deploy on Railway

1. Push this repo to GitHub (e.g. `hrms-lite`).
2. Go to [railway.app](https://railway.app), sign in (e.g. with GitHub).
3. **New project** → **Deploy from GitHub repo** → choose `hrms-lite`.
4. Railway will detect the `Procfile` and use it. No extra build/start commands needed unless you change the Procfile.
5. In the service → **Settings** → **Networking** → **Generate domain** to get a public URL (e.g. `https://hrms-lite-production-xxxx.up.railway.app`).
6. Optional: set **Environment variables** (e.g. `DEBUG=False`, `SECRET_KEY=your-secret-key`) for production.

The app runs migrations and `collectstatic` on each deploy, then starts Gunicorn. Static files are served via WhiteNoise.

---

## Assumptions / limitations

- **No auth.** One implicit admin; no user accounts or roles.
- **Employee ID and email** must be unique. Duplicates are rejected with a message.
- **Attendance** is one record per employee per day (present or absent). Re-marking the same day overwrites.
- **Payroll, leave, etc.** are out of scope.
- **Production:** `DEBUG` and `SECRET_KEY` are dev defaults. For deployment you’d set `DEBUG=False`, a proper `SECRET_KEY`, and something like `ALLOWED_HOSTS` and static-file serving (e.g. WhiteNoise or a reverse proxy).
