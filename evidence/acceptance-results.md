# Complete 10-question benchmark report
Faisal Mehmood · 12 November 2026

**Snapshot:** `53353f52eefe1fdb81e4803d099000267fb3100f`  
**Method:** one local HTTP request per question, no retries. Default
deterministic claim renderer. Required facts were reviewed against the
pinned source; the runner independently checked status, gold line coverage,
exact snippets, citation IDs and the pre-generation rejection behavior.

| ID | Benchmark question | Observed answer / decision | Exact citations | Result |
|---|---|---|---|---|
| Q01 | Where is the authentication token validated, and what happens when it is missing or invalid? | Router requires the token dependency. It checks Bearer and compares the configured token; invalid or missing credentials return 401. | 2/2 | Pass |
| Q02 | How does database retry work when SQLite is locked? | Fresh connection and transaction per attempt. Only lock errors retry; three default attempts, with 50 ms and 100 ms delays. Unrelated or final errors propagate. | 2/2 | Pass |
| Q03 | What happens to a ticket title that is too short after whitespace is trimmed? | The service strips whitespace, rejects titles under five characters, and the POST handler maps the error to HTTP 422. | 2/2 | Pass |
| Q04 | Trace a ticket creation request from the POST endpoint to storage. What status does the new ticket get? | POST 201 calls the service then repository; the parameterized insert sets status to open. | 3/3 | Pass |
| Q05 | How is the ticket listing filtered and ordered? | Optional open/closed filter is bound as a parameter; results sort by descending ID. | 2/2 | Pass |
| Q06 | Where and when is the SQLite schema initialized? | The registered FastAPI lifespan initializes the schema before yielding; the table is created if absent. | 3/3 | Pass |
| Q07 | How does the browser send the demo token when creating a ticket? | The form submits JSON via ticketRequest, which sets the Authorization: Bearer header for /api/tickets. | 2/2 | Pass |
| Q08 | Does the health endpoint verify the database connection? | No; it returns a static ok response without checking dependencies. | 1/1 | Pass |
| Q09 | How are Stripe payments processed, and where are payment webhooks verified? | Rejected before generation using the required absence message. | None emitted | Pass |
| Q10 | How are Okta groups mapped to application roles during SSO? | Rejected before generation using the required absence message. | None emitted | Pass |

**Overall:** 10/10 evaluated and passed. **Answerable:** 8/8.
**Correct abstentions:** 2/2. **Citation precision:** 17/17 (100%) exact
path, inclusive line bounds and snippet matches; unsupported cases are
excluded. See citation-accuracy.md for every cited range.

## Performance

| Metric | Previous implementation | Updated implementation |
|---|---:|---:|
| Median index startup, no cache | 39.756 ms | 8.830 ms |
| Median startup with a populated cache | N/A | 3.936 ms |
| Retained Python allocations after index construction | 55,251 B | 51,186 B |
| Median warmed Q&A latency on six shared questions | 52.63 µs | 23.13 µs |

Measured locally on one fixture, with 12 startup repetitions per mode and
200 warmed rounds per query set. Q&A timing is in-process and excludes
HTTP, browser and LLM latency. Retained bytes are Python allocations tracked
by tracemalloc, not process RSS. Cold cache creation took 9.109 ms median;
the populated cache was 28,672 bytes on disk. These are fixture measurements,
not performance guarantees for larger repositories.
