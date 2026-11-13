# TicketDesk architecture overview

Snapshot: `53353f52eefe1fdb81e4803d099000267fb3100f`

## Tech stack

- Python, FastAPI and Uvicorn (requirements.txt)
- SQLite persistence (app/db.py imports sqlite3)
- HTML/CSS with browser JavaScript modules (web/index.html)

## Key entry points

- python -m app starts Uvicorn (app/__main__.py).
- FastAPI application registration: `app/main.py:20–20`.
- Database startup: `app/main.py:13–17`.
- POST /api/tickets: `app/routes.py:14–20`.
- GET /api/tickets: `app/routes.py:23–26`.
- GET /health: `app/health.py:7–10`.
- Browser ticket submission: `web/app.js:22–32`.

## Local module dependencies

Arrows point from the importer to the imported module. This is a static graph.

```mermaid
flowchart TD
  n0["app/__init__.py"]
  n1["app/__main__.py"]
  n2["app/auth.py"]
  n3["app/config.py"]
  n4["app/db.py"]
  n5["app/health.py"]
  n6["app/main.py"]
  n7["app/repository.py"]
  n8["app/routes.py"]
  n9["app/schemas.py"]
  n10["app/service.py"]
  n11["web/api.js"]
  n12["web/app.js"]
  n1 --> n3
  n2 --> n3
  n4 --> n3
  n6 --> n4
  n6 --> n5
  n6 --> n8
  n7 --> n4
  n7 --> n9
  n8 --> n2
  n8 --> n7
  n8 --> n9
  n8 --> n10
  n10 --> n7
  n10 --> n9
  n12 --> n11
```

### Import edges

- `app/__main__.py` → `app/config.py`
- `app/auth.py` → `app/config.py`
- `app/db.py` → `app/config.py`
- `app/main.py` → `app/db.py`, `app/health.py`, `app/routes.py`
- `app/repository.py` → `app/db.py`, `app/schemas.py`
- `app/routes.py` → `app/auth.py`, `app/repository.py`, `app/schemas.py`, `app/service.py`
- `app/service.py` → `app/repository.py`, `app/schemas.py`
- `web/app.js` → `web/api.js`

## Coverage

- 13 indexed modules; 15 local import edges.
- Cycles: none detected.
- Dynamic imports and runtime dependencies are outside this static view.
