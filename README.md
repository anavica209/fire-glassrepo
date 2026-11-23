# Fire glass

Fire glass is a standalone FastAPI tarot web app. It has a demo admin login, optional Google OAuth, and a guided five-screen session: take a breath, choose a topic, shuffle and pick three cards, explore their interpretations, and close or save the reading. Saved readings are stored in the browser's local diary on that device.

Application code lives under `app/`: `api/` contains the HTTP routers, `core/` contains configuration and shared constants, `domain/` contains tarot models and shared application logic, and `services/` contains the chatbot and PDF retrieval code. Templates and static assets are stored alongside the app. The tarot guide lives in `data/raw/`, and analytics are stored in PostgreSQL using SQLAlchemy 2.0 Core and its async engine.

## Run locally

Open a PowerShell terminal in the `fire-glass` directory. If the terminal is at the workspace root, first run:

```powershell
Set-Location ".\fire-glass"
```

Create an isolated environment and install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Configure `.env` with the Supabase session pooler URL and database password. Copy the pooler host and username from Supabase's **Connect** panel. Keep the password in `POSTGRES_DB_PASS`; do not include it in `DATABASE_URL`:

```env
DATABASE_URL=postgresql://postgres.<project-ref>@<pooler-host>:5432/postgres?sslmode=require
POSTGRES_DB_PASS=<your-supabase-database-password>
```

Apply migrations and start the app directly against Supabase (no local Docker database is needed):

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Keep `.env` private and out of version control. If a database password is exposed, rotate it in Supabase and update `.env`.

### Supabase connection troubleshooting

The `POSTGRES_DB_*` lines are `.env` entries; do not run them as PowerShell commands. Save them in the project-root `.env` file, then restart Alembic or the app so `python-dotenv` reloads the settings.

If Alembic reports `getaddrinfo failed`, the configured database hostname could not be resolved. Copy the complete session pooler URL from the Supabase project's **Connect** panel into `DATABASE_URL`.

You can check that a host resolves from PowerShell with `Resolve-DnsName <host-from-supabase>`. Run `alembic upgrade head` only after that succeeds.

Using the environment's Python to launch Uvicorn avoids relying on a globally installed `uvicorn` command or activating the environment in PowerShell.
From the project root, `app.main:app` is the canonical import path. The root-level `main.py` also keeps the older `main:app` command working.

Open [http://localhost:8000](http://localhost:8000). Demo credentials: `admin` / `admin`.

## Tarot chat

The expandable chat drawer on the reading page explains tarot basics and the past, present, and future positions using `data/raw/guia_completa_tarot-v2.pdf` as reference. To enable responses, set `GROQ_API_KEY` in `.env`; without it, the drawer remains available and explains how to configure the service.

## Tests

Install the development dependencies and run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

## Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
OpenAPI Schema JSON: http://localhost:8000/openapi.json

## API authentication

Reading and reading-download API routes require a signed JWT bearer token. The app obtains short-lived tokens through the signed-in web session. Tokens expire after 30 minutes. Before deployment, configure a unique random `JWT_SECRET` separate from `SESSION_SECRET`; if omitted, a temporary process-local signing secret is generated and tokens expire when the process restarts. Deploy with HTTPS and replace the demo password with real user accounts and securely hashed passwords.

## Downloading a reading

At the end of a reading, choose **Descargar mis cartas** to download a ZIP containing one SVG image for each of the three cards. Each image includes the card, its position, keywords, interpretation, and focus for the selected topic.

## Google OAuth

Create OAuth 2.0 credentials in Google Cloud Console, add `http://localhost:8000/auth/google/callback` as an authorized redirect URI, and set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`. For a deployed site, set `GOOGLE_REDIRECT_URI` to its HTTPS callback URL, configure the OAuth consent screen, set a unique `SESSION_SECRET`, and set `COOKIE_SECURE=true`.

The `admin` / `admin` credentials are intentionally for local demonstration only. Replace the demo authentication with managed user accounts and a strong password policy before deployment.

## Admin analytics

The demo `admin` account sees an Analytics link in the top navigation. It shows each user's accumulated visible time in the first four reading sections (welcome, focus, card draw, and interpretation). A FastAPI middleware records each section transition in PostgreSQL; tracking pauses when the tab is hidden or the page is left. User names are shown to the admin, while account emails are represented by a keyed HMAC so they are not stored in plain text.

Analytics use the `section_time_events` table. The application requires `DATABASE_URL` and uses `POSTGRES_DB_PASS` as its password when the URL omits it. It uses the `postgresql+asyncpg` driver. The Docker image runs `alembic upgrade head` before starting the application, so the analytics table is created or upgraded during deployment. When starting the app directly (outside Docker), run `alembic upgrade head` first. New schema changes should be created as Alembic revisions and committed with the application code.

Docker Compose starts PostgreSQL with a persistent named volume and uses `POSTGRES_DB_PASS` from `.env`. If `data/fire_glass_analytics.db` contains existing analytics, run the Alembic upgrade and then import the records once with `.\.venv\Scripts\python.exe -m scripts.import_sqlite_analytics`. The SQLite file is retained as a backup; the importer skips records whose primary keys already exist.

When running in Docker, the equivalent import command is `docker compose run --build --rm fire-glass python -m scripts.import_sqlite_analytics`.

## Docker useful commands

In GitHub, create a Codespace from the repository. Run the following commands in its terminal; the app link will appear in the Ports tab.

This project uses **Docker** and **Docker Compose** to run the FastAPI application and PostgreSQL in containers. PostgreSQL data is persisted in a named volume.

### Prerequisites
* [Docker](https://docker.com) and Docker Compose installed.
* A `.env` file in the root directory (you can copy `.env.example` as a starting point) containing your PostgreSQL password and API keys:
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```

### Quick Start

1. **Start PostgreSQL and apply the database migration:**
   ```bash
   docker compose up -d postgres
   docker compose run --build --rm fire-glass alembic upgrade head
   ```
2. **Build and start the app in detached mode:**
   ```bash
   docker compose up -d --build
   ```

3. **Check container status and healthcheck:**
   ```bash
   docker compose ps
   ```
   Once ready, the app will be available at **`http://localhost:8000`**.

### Useful Commands

* **View real-time logs:**
  ```bash
  docker compose logs -f
  ```
* **Rebuild after code changes:**
  ```bash
  docker compose up -d --build
  ```
* **Stop the application (keeps PostgreSQL data):**
  ```bash
  docker compose down
  ```

## CI/CD & Automation

This repository uses **GitHub Actions** (`.github/workflows/ci.yml`) to automate testing, security checks, and deployment:

- **Triggers:** Runs automatically on every `push` or `pull_request` to `main`, on a monthly schedule (`cron`), or manually via `workflow_dispatch` from the **Actions** tab.
- **Quality & Security:** Checks code formatting with `black`, runs static security analysis with `bandit`, audits dependencies with `safety`, executes the `pytest` suite, and validates the `Dockerfile` build.
- **Deployment:** On a successful `push` to `main`, triggers a webhook to automatically redeploy the updated container in **Dokploy**.
- **Dependency Updates:** Configured with **Dependabot** (`.github/dependabot.yml`) to open weekly Pull Requests for Python and GitHub Actions updates.
