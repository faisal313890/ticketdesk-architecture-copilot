# Citation accuracy table

Snapshot: `53353f52eefe1fdb81e4803d099000267fb3100f`

| Case | Citation | Source | Inclusive lines | Exact snippet match |
|---|---|---|---|---|
| Q01 | C1 | `app/routes.py` | 11–11 | Pass |
| Q01 | C2 | `app/auth.py` | 9–16 | Pass |
| Q02 | C1 | `app/db.py` | 13–25 | Pass |
| Q02 | C2 | `app/config.py` | 7–14 | Pass |
| Q03 | C1 | `app/service.py` | 10–15 | Pass |
| Q03 | C2 | `app/routes.py` | 14–20 | Pass |
| Q04 | C1 | `app/routes.py` | 14–20 | Pass |
| Q04 | C2 | `app/service.py` | 10–15 | Pass |
| Q04 | C3 | `app/repository.py` | 6–15 | Pass |
| Q05 | C1 | `app/routes.py` | 23–26 | Pass |
| Q05 | C2 | `app/repository.py` | 18–28 | Pass |
| Q06 | C1 | `app/main.py` | 13–17 | Pass |
| Q06 | C2 | `app/main.py` | 20–20 | Pass |
| Q06 | C3 | `app/db.py` | 28–34 | Pass |
| Q07 | C1 | `web/app.js` | 22–32 | Pass |
| Q07 | C2 | `web/api.js` | 2–12 | Pass |
| Q08 | C1 | `app/health.py` | 7–10 | Pass |

**17/17 exact (100%).** Q09 and Q10 emitted no citations and are excluded from this denominator.
Each span was compared against a fresh Git read; the comparison includes indentation and all lines.
