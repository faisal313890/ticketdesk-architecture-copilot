"""Generate a static Markdown architecture overview for a local Git snapshot."""
import argparse
from pathlib import Path, PurePosixPath

from .index import Snapshot

def dependency_graph(index):
    graph = {p:set() for p in index.imports}
    modules = {p[:-3].replace("/",".").removesuffix(".__init__"):p for p in graph if p.endswith(".py")}
    for source, imports in index.imports.items():
        for level, module, names in imports:
            if source.endswith(".js"):
                dest = str(PurePosixPath(source).parent / module)
                if dest in graph:
                    graph[source].add(dest)
                continue
            package = source[:-3].replace("/",".").split(".")[:-1]
            if level and level > len(package):
                continue
            base = ".".join((package[:len(package)-level+1] if level else []) + ([module] if module else []))
            targets = [base] if module else []
            targets += [f"{base}.{name}" for name in names if name != "*"]
            for target in targets:
                if target in modules and modules[target] != source:
                    graph[source].add(modules[target])
    return graph

def cycles(graph):
    """Report DFS back-edge cycles without importing modules or looping."""
    done, active, found = set(), {}, []
    for root in sorted(graph):
        if root in done:
            continue
        stack = [(root,iter(sorted(graph[root])))]
        active[root] = 0
        while stack:
            node, children = stack[-1]
            child = next(children,None)
            if child is None:
                done.add(node)
                del active[node]
                stack.pop()
            elif child in active:
                found.append([n for n,_ in stack[active[child]:]]+[child])
            elif child not in done:
                active[child] = len(stack)
                stack.append((child,iter(sorted(graph[child]))))
    return found

def overview(index):
    graph = dependency_graph(index)
    dependencies = index.git("show",f"{index.commit}:requirements.txt").decode().splitlines()
    tech = []
    if {"fastapi","uvicorn"} <= set(dependencies):
        tech.append("Python, FastAPI and Uvicorn (requirements.txt)")
    if any(module == "sqlite3" for _,module,_ in index.imports.get("app/db.py",[])):
        tech.append("SQLite persistence (app/db.py imports sqlite3)")
    web = index.git("show",f"{index.commit}:web/index.html").decode()
    if 'type="module"' in web:
        tech.append("HTML/CSS with browser JavaScript modules (web/index.html)")
    startup = index.git("show",f"{index.commit}:app/__main__.py").decode()
    entries = ["python -m app starts Uvicorn (app/__main__.py)."] if 'uvicorn.run("app.main:app"' in startup else []
    for symbol, description in [
        ("app.main.app","FastAPI application registration"),
        ("app.main.lifespan","Database startup"),
        ("app.routes.create_ticket","POST /api/tickets"),
        ("app.routes.list_tickets","GET /api/tickets"),
        ("app.health.health","GET /health"),
        ("web.app.submitHandler","Browser ticket submission"),
    ]:
        if symbol in index.spans:
            s, = index.resolve_many([symbol])
            entries.append(f"{description}: `{s.path}:{s.first}–{s.last}`.")
    ids = {p:f"n{i}" for i,p in enumerate(sorted(graph))}
    lines = ["# TicketDesk architecture overview","",f"Snapshot: `{index.commit}`","",
             "## Tech stack","",*[f"- {x}" for x in tech],"","## Key entry points","",
             *[f"- {x}" for x in entries],"","## Local module dependencies","",
             "Arrows point from the importer to the imported module. This is a static graph.","",
             "```mermaid","flowchart TD",*[f'  {ids[p]}["{p}"]' for p in ids]]
    lines += [f"  {ids[p]} --> {ids[q]}" for p in ids for q in sorted(graph[p])]
    lines += ["```","", "### Import edges",""]
    lines += [f"- `{p}` → " + ", ".join(f"`{q}`" for q in sorted(graph[p])) for p in ids if graph[p]]
    lines += ["","## Coverage","",f"- {len(graph)} indexed modules; {sum(map(len,graph.values()))} local import edges.",
              "- Cycles: "+("; ".join(" → ".join(c) for c in cycles(graph)) or "none detected")+".",
              "- Dynamic imports and runtime dependencies are outside this static view."]
    lines += [f"- Index note: `{p}` — {note}" for p,note in index.notes]
    return "\n".join(lines)+"\n"

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo",required=True)
    p.add_argument("--cache",default=".cache/index.sqlite3")
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(overview(Snapshot(args.repo,args.cache,vector_symbols=frozenset())),encoding="utf-8")
    print(out)
