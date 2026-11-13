# Live demo — 6 minutes

Run from the extracted folder. Clone the bundled fixture before screen sharing
if desired. Open CMD and have the repository file open in VS Code.

| Time | Do this | Explain |
|---|---|---|
| 0:00–0:45 | Run `python -m copilot --repo ticketdesk index` twice. | The index reads one Git commit. Show 13 files and the warm cache hit count. |
| 0:45–1:20 | Ask `Trace the user login flow from endpoint to DB`. | TicketDesk has no login-to-DB path. Its actual authentication is a Bearer token dependency. |
| 1:20–3:30 | Ask `Trace ticket creation from endpoint to database`. Scroll through C1–C6. | C1–C2 show the auth gate, C3–C4 route and service, C5–C6 the parameterized INSERT and SQLite transaction. |
| 3:30–4:10 | Open app/repository.py at line 6, or run `git -C ticketdesk show HEAD:app/repository.py`. | Match C5 lines 6–15 to the committed file; line 10 contains the INSERT and line 15 calls run_db. |
| 4:10–4:50 | Ask `Show billing webhook`. | Show Feature not found and that no citation is printed. |
| 4:50–6:00 | Let the team lead try their own question, then open the audit. | Example: Where is the Bearer token checked? Compare C2 to app/auth.py lines 9–16. Show the 10/10 cases and 17/17 exact spans. |

CLI syntax: `python -m copilot --repo ticketdesk ask "YOUR QUESTION"`.
The supplied video is a silent walkthrough assembled from actual CLI output.
The live acceptance step is for the team lead to run independently.
