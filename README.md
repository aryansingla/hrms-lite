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
<img width="1910" height="982" alt="Screenshot From 2026-02-19 22-28-18" src="https://github.com/user-attachments/assets/957cf395-7868-49ea-ac7f-8348fab68ae9" />

<img width="1910" height="982" alt="Screenshot From 2026![Uploading Screenshot From 2026-02-19 22-28-37.png…]()
-02-19 22-28-25" src="https://github.com/user-attachments/assets/4556ffff-d57b-4c57-9a6d-3c0c64142d87" />

<img width="1910" height="982" alt="Screenshot From 2026-02-19 22-28-37" src="https://github.com/user-attachments/assets/f175e1cc-d4dc-4ade-bbe0-dc016e665f4f" />

<img width="1910" height="982" alt="Screenshot From 2026-02-19 22-28-47" src="https://github.com/user-attachments/assets/d58f2f35-f4c4-49af-b54c-840b3c38bbc6" />

<img width="1910" height="982" alt="Screenshot From 2026-02-19 22-29-03" src="https://github.com/user-attachments/assets/392f9b38-053b-474d-b9bb-ed7a407ff9f3" />


## Assumptions / limitations


- **No auth.** One implicit admin; no user accounts or roles.

- **Employee ID and email** must be unique. Duplicates are rejected with a message.
- **Attendance** is one record per employee per day (present or absent). Re-marking the same day overwrites.
- **Payroll, leave, etc.** are out of scope.
- **Production:** `DEBUG` and `SECRET_KEY` are dev defaults. For deployment you’d set `DEBUG=False`, a proper `SECRET_KEY`, and something like `ALLOWED_HOSTS` and static-file serving (e.g. WhiteNoise or a reverse proxy).


