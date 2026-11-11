# Fire glass

Fire glass is a standalone FastAPI tarot web app. It has a demo admin login, optional Google OAuth, and a guided five-screen session: take a breath, choose a topic, shuffle and pick three cards, explore their interpretations, and close or save the reading. Saved readings are stored in the browser's local diary on that device.

HTTP endpoints are grouped into `APIRouter` modules under `routers/` by page, authentication, analytics, and reading domain. `main.py` configures the app and includes those routers; `core.py` holds shared models, dependencies, and services.

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
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Using the environment's Python to launch Uvicorn avoids relying on a globally installed `uvicorn` command or activating the environment in PowerShell.

Open [http://localhost:8000](http://localhost:8000). Demo credentials: `admin` / `admin`.

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

The demo `admin` account sees an Analytics link in the top navigation. It shows each user's accumulated visible time in the first four reading sections (welcome, focus, card draw, and interpretation). A FastAPI middleware records each section transition in `fire_glass_analytics.db`; tracking pauses when the tab is hidden or the page is left. User names are shown to the admin, while account emails are represented by a keyed HMAC so they are not stored in plain text. This local SQLite file is excluded from version control.
