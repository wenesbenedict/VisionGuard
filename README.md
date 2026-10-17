# VisionGuard AI

AI-powered workplace safety monitoring & incident intelligence platform.

Tagline: **See the risk. Detect the incident. Protect the workplace.**

## Stack

- Frontend: React + TypeScript + Vite + Tailwind CSS + Recharts
- Backend: FastAPI + SQLAlchemy + Pydantic
- CV: YOLO (Ultralytics) + OpenCV + PyTorch + ByteTrack
- DB: PostgreSQL for Compose deployments; SQLite for local demos
- AI: LLM incident summarization
- Realtime: WebSockets
- Deploy: Docker Compose

## Phases

- Phase 0: Git repo setup
- Phase 1 (MVP): dashboard, backend, DB, video upload, YOLO detection, PPE violations, incident storage
- Phase 2: tracking, restricted zones, realtime processing, WS alerts, snapshots, analytics
- Phase 3: fall detection, AI summaries, camera management, RBAC, clips, advanced analytics
- Phase 4: Docker, cloud deploy, multi-camera, optimization


## Local development (Windows)

The local demo uses SQLite at `backend/visionguard.db` by default. If that file already exists, the app reuses it; otherwise SQLAlchemy creates the database and tables on startup. The current models use standard scalar columns, foreign keys, and JSON fields supported by SQLite. PostgreSQL remains available by setting `DATABASE_URL` to a PostgreSQL SQLAlchemy URL. Run the backend from `backend/` so the relative SQLite URL resolves there. Back up any existing database before making schema changes.

### Prerequisites

- Python 3.11 (the backend Docker image and existing pinned dependency set target this version; use the same version locally).
- Node.js 20.19+ and npm (Vite 8 requires a recent Node 20 or newer runtime).
- The model weights file `backend/yolov8n.pt`. The SQLite database is local/ignored and is created on first run if absent.

Do not use the existing `backend/.venv` if its configured Python installation no longer exists. Create a fresh environment with the supported Python installation; this leaves the old environment and database untouched:

```powershell
py -3.11 -m venv backend\.venv-local
backend\.venv-local\Scripts\python.exe -m pip install -r backend\requirements.txt
```

### Start the backend

```powershell
# Keep this PowerShell window open; the backend reads the key from this process environment.
$env:JWT_SECRET = (& python -c "import secrets; print(secrets.token_urlsafe(48))").Trim()
Set-Location backend
.venv-local\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: `http://127.0.0.1:8000/api/health`.

### Start the frontend

In a second PowerShell window:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Open the Vite URL printed in the terminal. Vite proxies `/api` and `/ws` to the backend on port 8000.

### Optional PostgreSQL / Docker path

Set `DATABASE_URL` to a PostgreSQL URL for a PostgreSQL-backed run. The existing `docker-compose.yml` remains the PostgreSQL deployment path:

```powershell
docker compose up --build
```

The Compose build requires a running Docker engine. Dependency versions are pinned in `backend/requirements.txt`; this setup does not upgrade or downgrade them. The local SQLite mode is for development/demo use, not a recommendation for concurrent production workloads.

### Checks

```powershell
# Frontend type-check and production bundle
Set-Location frontend
npm run build
npm run lint
```

No automated backend test suite is currently defined in the repository. The frontend build and lint checks do not exercise backend authentication, database writes, WebSockets, or model inference.


## Security setup and current detection limits

The backend refuses to start unless `JWT_SECRET` is set to at least 32 random bytes. In the same PowerShell window used to start the local backend, set one without putting it in source control:

```powershell
$env:JWT_SECRET = (& python -c "import secrets; print(secrets.token_urlsafe(48))").Trim()
```

Startup no longer creates an administrator or uses a built-in account. On a new, empty database, create the initial administrator interactively (the password is entered with hidden terminal input):

```powershell
Set-Location backend
.venv-local\Scripts\python.exe -m app.create_admin
```

The existing local database already has an administrator record from the former insecure bootstrap. Its data has been preserved and its password has not been changed automatically. If you are authorized to administer this local instance, rotate that account’s password before deployment:

```powershell
.venv-local\Scripts\python.exe -m app.reset_admin_password
```

The reset updates only that administrator’s password hash and invalidates their existing JWT sessions. Do not run it if you do not control the account.

For Docker Compose, copy `.env.example` to `.env`, set a unique random `JWT_SECRET` and URL-safe random `POSTGRES_PASSWORD`, then run `docker compose up --build`. Published Compose ports bind to localhost. Keep `.env` private and do not commit it.

For a new, empty Compose database, create the first administrator interactively with `docker compose exec backend python -m app.create_admin`. To rotate an existing Compose administrator password, run `docker compose exec backend python -m app.reset_admin_password` from a trusted machine.

Video analysis only processes uploaded video. PPE checks require a custom PPE model file configured with `PPE_MODEL`; absent or unloadable weights mean no PPE determination is made, and the UI/API report whether PPE inference actually ran. Fall alerts are a bounding-box aspect-ratio heuristic; zone alerts use person-box centers against configured pixel-coordinate polygons plus a dwell threshold. Both are potential alerts requiring human review. LLM incident summaries are optional; if Ollama is unavailable, the service returns a templated summary rather than a generated model summary. Continuous CCTV/RTSP processing and overcrowding detection are not implemented.
