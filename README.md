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
# clone or cd into the project
cd hrms-lite-project

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

## Assumptions / limitations

- **No auth.** One implicit admin; no user accounts or roles.
- **Employee ID and email** must be unique. Duplicates are rejected with a message.
- **Attendance** is one record per employee per day (present or absent). Re-marking the same day overwrites.
- **Payroll, leave, etc.** are out of scope.
- **Production:** `DEBUG` and `SECRET_KEY` are dev defaults. For deployment you’d set `DEBUG=False`, a proper `SECRET_KEY`, and something like `ALLOWED_HOSTS` and static-file serving (e.g. WhiteNoise or a reverse proxy).
