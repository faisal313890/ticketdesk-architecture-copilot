"""Build the index, or ask a cited question from the terminal."""
import argparse
import json
from pathlib import Path

from .core import Copilot, Snapshot

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--cache", default=".cache/index.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("index", help="Build or reuse the committed-source index")
    ask = sub.add_parser("ask", help="Ask one question")
    ask.add_argument("question")
    ask.add_argument("--json", action="store_true")
    args = parser.parse_args()
    snapshot = Snapshot(args.repo, args.cache)
    if args.command == "index":
        print(json.dumps(dict(commit=snapshot.commit, files=len(snapshot.objects),
              source_spans=len(snapshot.spans), searchable_symbols=len(snapshot.vectors),
              cache=str(Path(args.cache)), **snapshot.stats, notes=snapshot.notes), indent=2))
        return
    result, decision = Copilot(snapshot).ask(args.question)
    if args.json:
        print(json.dumps(dict(response=result, decision=decision), indent=2))
        return
    print(f"Snapshot: {snapshot.commit}")
    if result["status"] != "answered":
        print("Feature not found")
    print(result["answer"])
    for c in result["citations"]:
        print(f"\n[{c['id']}] {c['file_path']}:{c['start_line']}-{c['end_line']}")
        for i,line in enumerate(c["code_snippet"].splitlines(),c["start_line"]):
            print(f"{i:>4} | {line}")
    if result["status"] != "answered":
        print("Scope: this result is limited to the indexed snapshot and supported queries.")

if __name__ == "__main__":
    main()
