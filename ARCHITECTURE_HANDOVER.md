# Architecture handover memo
**Faisal Mehmood · 13 November 2026**

The fixture is TicketDesk: FastAPI, SQLite and a small JavaScript client.
The included Git bundle pins the test repository and preserves exact citation
lines. The Copilot can run without starting TicketDesk.

| Component | Responsibility |
|---|---|
| copilot/index.py | Reads Git blobs, builds source spans and import metadata, caches unchanged blobs |
| copilot/core.py | Matches supported intent, scores spans, validates approved claims and citation text |
| copilot/__main__.py | Explicit index build and terminal Q&A |
| copilot/server.py and web/ | Local HTTP endpoint and expandable citation cards |
| copilot/overview.py | Tech stack, entry points and static import graph |
| evaluate.py and stress.py | Repeatable benchmark and isolated stress fixtures |

For the acceptance check, clone ticketdesk.bundle, run the indexer, then ask
an unscripted question on a supported topic and compare the excerpt against
the same commit. Supported topics include authentication, ticket creation
and storage, title validation, listing, database startup and retry,
browser token forwarding, and health checks.

The report documents 10/10 benchmark cases and 17/17 exact citations on the
fixture. The extra demo cases are measured separately. Exact citation
verification confirms where a quote came from; review whether it supports
the claim. This is a curated prototype; broader retrieval and live-model
behavior still need separate evaluation.

GitHub publication: this package is ready for a GitHub repository, but no
remote has been configured or pushed here. Use the team-approved destination
and share its URL after the push. Keep the test fixture as the supplied
bundle; do not commit a nested Git clone or the cache.
