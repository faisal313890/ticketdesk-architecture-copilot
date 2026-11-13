# Final handover audit — 13 November 2026

- Full HTTP benchmark rerun: 10/10 passed. Eight answers, two correct
  abstentions, and 17/17 exact source spans. See acceptance-results.md for
  the question-by-question benchmark and 12 November performance measurements.
- Live demo rehearsal: authenticated ticket creation produced six cited spans.
  The alternate Bearer-token question produced two. All 8/8 demo citations
  were independently matched to the Git source. The billing webhook and
  database-backed login questions returned no citations. See demo-query-audit.json.
- Indexer: 13 indexed files and 22 source spans. A fresh build and a warm
  rebuild were exercised. See demo-index.json and demo-index-cold.json.
- Stress tests rerun with the deterministic renderer. Live Ollama and
  independent team lead acceptance were not performed here.
