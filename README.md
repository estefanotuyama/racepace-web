# RacePace Web v0.7

![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/fastapi-0.115-green)
![React](https://img.shields.io/badge/react-19-blue)
![TypeScript](https://img.shields.io/badge/typescript-4.9-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)

A web application for exploring Formula 1 driver data, sessions, lap times, and results — powered by OpenF1 data.

Live at [https://f1racepace.vercel.app](https://f1racepace.vercel.app)

---

## Features

- Browse F1 events by year and location
- View session info (FP1, FP2, FP3, Qualifying, Sprint, Race)
- Compare lap times across multiple drivers with interactive charts
- View session results with finishing positions, gaps, and DNF/DNS/DSQ status
- Team color identification throughout the UI
- Automated weekly database updates via GitHub Actions
- Backfill for incomplete sessions with missing lap data

---

## Tech Stack

**Backend**: FastAPI, SQLModel, PostgreSQL (Supabase), uv

**Frontend**: React 19, TypeScript, Recharts

**Infrastructure**: Render (backend), Vercel (frontend), GitHub Actions (scheduled DB updates)

---

## Project Structure

```
racepace-web/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API route definitions
│   ├── models/              # SQLModel ORM classes
│   ├── crud/                # Database access logic
│   ├── db/                  # DB engine, sessions, data population
│   ├── schemas/             # Pydantic request/response models
│   ├── service/             # Business logic
│   ├── repository/          # Data access layer
│   ├── scripts/             # Utility scripts
│   ├── tests/               # pytest tests
│   └── utils/               # Helpers
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client
│   │   ├── types.ts         # TypeScript type definitions
│   │   ├── App.tsx          # Main app component
│   │   └── index.tsx        # Entry point
│   └── package.json
├── .github/workflows/       # GitHub Actions (scheduled DB update)
├── static/                  # Static assets (favicon)
├── Dockerfile               # Docker image for backend
├── docker-compose.yml       # Local multi-container setup
├── pyproject.toml           # Python project config (uv)
├── Makefile                 # Development commands
└── README.md
```

---

## Setup & Usage

### 1. Clone the repo

```bash
git clone git@github.com:estefanotuyama/racepace-web.git
cd racepace-web
```

### 2. Install uv

Follow the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 3. Install dependencies

```bash
uv sync
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://user:password@host:port/database
ADMIN_SECRET=your-secret-key
```

### 5. Populate the database

Fetches data from the OpenF1 API and populates the database. May take up to 20 minutes on the first run.

```bash
uv run python -m backend.ingestion.update_service
```

### 6. Run the backend

```bash
make backend
# or
uv run uvicorn backend.main:app --reload
```

API docs available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 7. Run the frontend

Create `frontend/.env`:

```
REACT_APP_API_URL=http://localhost:8000
```

Then:

```bash
make frontend
# or
cd frontend && npm install && npm start
```

The app will be available at [http://localhost:3000](http://localhost:3000).

### Run both concurrently

```bash
make dev
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET, HEAD | `/` | Health check |
| GET | `/events/{year}` | All events for a given year |
| GET | `/events/years/` | All available years |
| GET | `/sessions/{meeting_key}` | Sessions for an event |
| GET | `/session_result/{session_key}` | Session finishing results |
| GET | `/drivers/{session_key}` | Drivers in a session |
| GET | `/laps/{session_key}/{driver_number}` | Lap times for a driver |
| GET | `/teams/` | Team color mapping |
| POST | `/admin/update` | Trigger DB update (requires `ADMIN_SECRET` header) |

---

## Deployment

- **Frontend**: Deployed on [Vercel](https://vercel.com)
- **Backend**: Deployed on [Render](https://render.com)
- **Database**: Hosted on [Supabase](https://supabase.com) (PostgreSQL)
- **Data updates**: GitHub Actions runs `backend.ingestion.update_service` weekly (Tuesdays 18:00 UTC), configurable via `.github/workflows/update_db.yml`

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string (Supabase) |
| `ADMIN_SECRET` | Secret for the `/admin/update` endpoint |
| `REACT_APP_API_URL` | Backend URL for the frontend (in `frontend/.env`) |

---

## Author

Built by **Estefano Tuyama Gerassi**

---

## License

This project is for educational purposes only. Data is sourced from the public [OpenF1 API](https://openf1.org/).
