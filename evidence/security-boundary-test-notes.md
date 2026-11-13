# Stress and security boundary checks
12 November 2026 · Run using stress.py against a disposable local clone.

| Stress case | Observed result |
|---|---|
| Large multi-line function | A function with 6,000 repeated body statements exceeded the 240-line span budget. It was excluded with an oversized-symbol note; the smaller sibling function was still indexed. |
| Circular imports | Both imports were captured; the dependency graph identified the cycle and traversal terminated without importing either module. |
| Syntax error | The malformed Python file was skipped and recorded; indexing continued. |
| Empty query | A whitespace-only request returned HTTP 400 and did not invoke generation. |
| Prompt injection in a Python comment | The test confirmed the injected comment reached the renderer as quoted source data but was excluded from search tokens. It did not change the answer. A simulated model that returned the injected marker as a claim was rejected without citations. The marker can remain visible in the exact source excerpt because a quotation is evidence, not an instruction. |
| Low similarity and mixed topic | Both queries were rejected without invoking the renderer. |
| Altered cached snippet | A deliberately altered span was rejected when checked against committed Git source. |
| Cache invalidation | The changed fixture reused 12 unchanged blobs and parsed 5 changed/new files. A repeat load reused all 17 eligible files without parsing. |

The server reads tracked regular Git blobs only, with a 128 KiB file limit.
It does not run repository code or follow symlinks. The live local model
adapter was not exercised; the injection evidence covers the default
renderer and simulated nonconforming model output. This bounded fixture test
does not establish a general injection resistance or hallucination rate.
