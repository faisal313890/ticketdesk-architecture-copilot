# TicketDesk Architecture Copilot

Local, read-only architecture Q&A for a pinned TicketDesk Git fixture. This is
a handover-ready prototype, not a production deployment.

## Installation and first run

Install Git and Python 3.10 or later. Extract the handover and open CMD or a
terminal in the folder containing ticketdesk.bundle. The default Copilot has
no pip dependencies, and the TicketDesk API does not need to run.

```cmd
git clone ticketdesk.bundle ticketdesk
git -C ticketdesk rev-parse HEAD
python -m copilot --repo ticketdesk index
python -m copilot --repo ticketdesk index
```

Expected snapshot: 53353f52eefe1fdb81e4803d099000267fb3100f. A fresh cache
reports 13 misses; the second build reports 13 hits. It indexes 13 files,
22 source spans and 15 searchable symbols. Use an existing clone only if
its HEAD matches. Uncommitted changes are not indexed.

## Ask and verify

```cmd
python -m copilot --repo ticketdesk ask "Trace ticket creation from endpoint to database"
python -m copilot --repo ticketdesk ask "Where is the Bearer token checked?"
python -m copilot --repo ticketdesk ask "Show billing webhook"
git -C ticketdesk show HEAD:app/repository.py
```

Compare the numbered C5 excerpt to lines 6–15 of the committed repository
file. Try an unscripted question within the supported topics. The billing
query should show **Feature not found** and emit no citations. The fixture
does not implement database-backed login; its Bearer dependency validates a
configured demo token. Use the authenticated ticket flow for the DB trace.

For expandable citations, start `python -m copilot.server --repo ticketdesk`
and open http://127.0.0.1:8765. The CLI provides the same cited responses and
supports `ask "question" --json`. See DEMO_RUNBOOK.md for the live demo.

## Language coverage and trade-offs

| Language | Coverage |
|---|---|
| Python | AST spans for top-level functions, classes and named assignments, including decorators; static import graph |
| JavaScript | Two reviewed citation spans keyed to exact fixture blobs; relative import detection |
| HTML/CSS and other languages | No general citation indexing; HTML contributes to the fixture stack overview |

Retrieval uses an intent vocabulary and lexical cosine similarity (0.10
cutoff), followed by verification of curated claims against pinned Git
source spans. It does not use embeddings or general-purpose inference.
This makes the demo repeatable, but unfamiliar wording and multi-topic
requests may be refused. A refusal is scoped to the indexed fixture and
supported questions. The optional Ollama server adapter was not used in
acceptance testing. No source is executed by the indexer.

SQLite caches up to 256 versioned path/blob entries in .cache/index.sqlite3.
Use --cache before the CLI subcommand to select a different file. Stop the
server before deleting a cache. Cache entries contain code; exclude them
from handover and source control. The file cap is 128 KiB and symbols over
240 lines are skipped. Dynamic imports and runtime calls are not inferred.

## Reproduce the audit

```cmd
python evaluate.py --repo ticketdesk
python stress.py --repo ticketdesk
python -m copilot.overview --repo ticketdesk --out rerun-evidence/architecture-overview.md
python measure.py --repo ticketdesk --out rerun-evidence/performance.json
```

See evidence/acceptance-results.md, evidence/citation-accuracy.md and
evidence/handover-audit.md. Historical performance numbers are labeled
separately from the final regression run. For handover ownership and
next steps, read ARCHITECTURE_HANDOVER.md.
