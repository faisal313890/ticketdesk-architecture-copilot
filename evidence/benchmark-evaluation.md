# Developer benchmark evaluation sheet

**Fixture:** TicketDesk · **Snapshot:** `53353f52eefe1fdb81e4803d099000267fb3100f`  
**Suite:** 8 answerable questions + 2 unanswerable questions. Gold answers were
checked against the fixture. Copilot outputs have not been run.

| ID | Developer question | Expected status | Required facts | Gold evidence (inclusive lines) | Result |
|---|---|---|---|---|---|
| Q01 | Where is the authentication token validated, and what happens when it is missing or invalid? | answered | Ticket router requires the dependency. It checks Bearer and compares the token to the configured value; failure is 401. | app/routes.py:11; app/auth.py:9–16 | Not run |
| Q02 | How does database retry work when SQLite is locked? | answered | Fresh connection and transaction per attempt; only lock-related OperationalError is retried; three attempts total; delays 50 ms then 100 ms; final or unrelated errors propagate. | app/db.py:13–25; app/config.py:13–14 | Not run |
| Q03 | What happens to a ticket title that is too short after whitespace is trimmed? | answered | The service strips whitespace and rejects fewer than five characters; the POST handler converts InvalidTitle to 422. | app/service.py:10–15; app/routes.py:14–20 | Not run |
| Q04 | Trace a ticket creation request from the POST endpoint to storage. What status does the new ticket get? | answered | POST returns 201; handler delegates to submit_ticket, then insert_ticket; INSERT is parameterized and sets ticket status to open. | app/routes.py:14–20; app/service.py:10–15; app/repository.py:6–15 | Not run |
| Q05 | How is the ticket listing filtered and ordered? | answered | GET accepts optional open/closed status; repository adds a bound WHERE parameter only when a filter is supplied and sorts by descending ID. | app/routes.py:23–26; app/repository.py:18–28 | Not run |
| Q06 | Where and when is the SQLite schema initialized? | answered | FastAPI registers lifespan, which calls init_db before yielding; init_db creates the tickets table if missing. | app/main.py:13–20; app/db.py:28–34 | Not run |
| Q07 | How does the browser send the demo token when creating a ticket? | answered | Submit handler passes token.value to ticketRequest with POST and a JSON body; ticketRequest sends it as Authorization: Bearer to /api/tickets. | web/app.js:22–32; web/api.js:2–12 | Not run |
| Q08 | Does the health endpoint verify the database connection? | answered | No. GET /health returns a static ok response without checking dependencies. | app/health.py:7–10 | Not run |
| Q09 | How are Stripe payments processed, and where are payment webhooks verified? | insufficient_evidence | Abstain. The snapshot supplies no payment implementation or webhook verification details. | None | Not run |
| Q10 | How are Okta groups mapped to application roles during SSO? | insufficient_evidence | Abstain. Local demo-token validation does not establish Okta integration or group-to-role mapping. | None | Not run |

## How to score

Use the snapshot above and record each response as a new artifact. For Q01–Q08,
pass only if the expected status matches, all required facts are present, every
material claim has a supporting citation, every cited snippet matches the
source, and no unsupported detail is added. Accept equivalent supporting spans.
For Q09–Q10, pass only if the response explicitly abstains, identifies the
missing context, and emits no fabricated claims, references or citations.
Record four outcomes separately: overall cases passed / 10, answerable cases
passed / 8, correct abstentions / 2, and exact citations / all emitted citations.
If no citations are emitted, report the citation rate as N/A. Manual review
decides whether a matching quote actually supports each claim.
