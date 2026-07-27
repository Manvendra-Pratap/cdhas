# CDHAS frontend

React/Vite dashboard for Cowrie honeypot session monitoring. It starts with realistic mock responses so the interface can be developed before the FastAPI endpoints are ready.

## Run locally

```powershell
cd frontend
pnpm install
pnpm dev
```

Open `http://localhost:5173`.

## Connect the backend

The dashboard uses mock data by default. Once the API is ready, create `frontend/.env.local`:

```text
VITE_USE_MOCK_API=false
```

It will then request:

- `GET /api/dashboard` for overview, activity, sessions, and intelligence data
- `GET /api/sessions/:id` for a session detail record

The Vite development proxy forwards `/api` calls to `http://localhost:8000`.
