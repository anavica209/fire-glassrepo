# Fire glass

Fire glass is a standalone FastAPI tarot web app. It has a demo admin login, optional Google OAuth, and a guided five-screen session: take a breath, choose a topic, shuffle and pick three cards, explore their interpretations, and close or save the reading. Saved readings are stored in the browser's local diary on that device.

Application code lives under `app/`: `api/` contains the HTTP routers, `core/` contains configuration and shared constants, `domain/` contains tarot models and shared application logic, and `services/` contains the chatbot and PDF retrieval code. Templates and static assets are stored alongside the app. The tarot guide lives in `data/raw/`, and local analytics are stored in the ignored `data/fire_glass_analytics.db`.

## Run locally

Open a PowerShell terminal in the `fire-glass` directory. If the terminal is at the workspace root, first run:

```powershell
Set-Location ".\fire-glass"
```

Create an isolated environment, install the dependencies, and start the server:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

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

The demo `admin` account sees an Analytics link in the top navigation. It shows each user's accumulated visible time in the first four reading sections (welcome, focus, card draw, and interpretation). A FastAPI middleware records each section transition in `data/fire_glass_analytics.db`; tracking pauses when the tab is hidden or the page is left. User names are shown to the admin, while account emails are represented by a keyed HMAC so they are not stored in plain text. This local SQLite file is excluded from version control.

## Docker userful commands:

In Github, over the repository -> code -> codespaces new and in the terminal execute the following commands. In tab ports is left the link to the web in the container.
Need to modify app\main.py to support postgres appuser credentials.

This project uses **Docker** and **Docker Compose** to run the FastAPI application in a lightweight, isolated environment while persisting the local SQLite database (`data/`) across container rebuilds.

### Prerequisites
* [Docker](https://docker.com) and Docker Compose installed.
* A `.env` file in the root directory (you can copy `.env.example` as a starting point) containing your API keys:
  ```env
  GROQ_API_KEY=your_groq_api_key_here
  ```

### Quick Start

1. **Build and start the container in detached mode:**
   ```bash
   docker compose up -d --build
   ```

2. **Check container status and healthcheck:**
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
* **Stop the application (keeps `data/` intact):**
  ```bash
  docker compose down
  ```