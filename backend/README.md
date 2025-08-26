# GMC SYSTEM Backend (Flask + MySQL)

## Setup

1) Create virtual environment (already created by tooling as `backend/venv`):

```
python -m venv venv
venv\\Scripts\\activate
```

2) Install dependencies:

```
pip install -r requirements.txt
```

3) Configure environment variables. Create a `.env` file next to `app.py`:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=gmc_system
PORT=5000
```

4) Create database and schema (adjust credentials as needed):

```
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS gmc_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p gmc_system < schema.sql
```

5) Run the server:

```
venv\\Scripts\\python.exe app.py
```

6) Test endpoints:

- GET http://127.0.0.1:5000/api/ping
- GET http://127.0.0.1:5000/api/health

## Notes

- CORS is open for dev. Restrict origins in production.
- Switch to full SQLAlchemy ORM models as needed.

## Deploy

### Heroku
1) Ensure you have a Heroku account and CLI installed.
2) From repo root (where `Procfile` is):
```
heroku create gmc-system
heroku buildpacks:set heroku/python
heroku config:set PYTHONUNBUFFERED=1
heroku config:set DB_URL="sqlite:///gmc.db"  # or your MySQL URL
git add -A && git commit -m "Deploy" || true
git push heroku HEAD:main
```
Open app URL printed by Heroku. Update `DB_URL` to a managed MySQL when ready.

### Render
1) Push this repo to GitHub.
2) In Render, create a new Web Service from the repo. It will read `render.yaml`.
3) Set `DB_URL` or individual MySQL env vars in the dashboard.
4) Deploy.

