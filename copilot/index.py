"""Read-only Git snapshot index with a bounded, content-addressed local cache."""
import ast
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from math import sqrt
from pathlib import Path
import json
import re
import sqlite3
import subprocess
import sys
import tokenize

PIN = "53353f52eefe1fdb81e4803d099000267fb3100f"
LIMIT = 128 * 1024
SPAN_LINES = 240
VERSION = f"ticketdesk-v1-py{sys.version_info.major}.{sys.version_info.minor}"
JS_SPANS = {
    "74781aec74a1d88a1671a2ce22164e18460ed224": ("ticketRequest", 2, 12),
    "3c7191a34ec26892101869a2ccad6d6518f1691e": ("submitHandler", 22, 32),
}

class EvidenceError(ValueError):
    pass

@dataclass(frozen=True, slots=True)
class Span:
    path: str
    first: int
    last: int
    symbol: str
    snippet: str

def parse(path, oid, raw):
    if b"\0" in raw:
        return [[], [], ["binary"]]
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError:
        return [[], [], ["invalid_utf8"]]
    lines = source.splitlines()
    if path.endswith(".js"):
        spec = JS_SPANS.get(oid)
        imports = [[0,m,[]] for m in re.findall(r'^import .* from ["\'](\./[^"\']+)["\']',source,re.M)]
        if not spec:
            return [[], imports, ["unsupported_javascript_blob"]]
        name, start, end = spec
        snippet = "\n".join(lines[start-1:end])
        return [[[name,start,end,snippet,snippet]],imports,[]]
    try:
        tree = ast.parse(source,filename=path)
    except (SyntaxError, RecursionError):
        return [[], [], ["syntax_error"]]
    imports, spans, notes = [], [], []
    comments = {}
    for token in tokenize.tokenize(BytesIO(raw).readline):
        if token.type == tokenize.COMMENT:
            comments[token.start[0]] = token.start[1]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            imports.extend([0,a.name,[]] for a in node.names)
        elif isinstance(node,ast.ImportFrom):
            imports.append([node.level,node.module or "",[a.name for a in node.names]])
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            name = node.name
            start = min([node.lineno]+[d.lineno for d in node.decorator_list])
        elif isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name,start = node.targets[0].id,node.lineno
        else:
            continue
        end = node.end_lineno
        if end-start+1 > SPAN_LINES:
            notes.append("oversized_symbol:"+name)
            continue
        snippet = "\n".join(lines[start-1:end])
        search = "\n".join(lines[i-1][:comments.get(i)] for i in range(start,end+1))
        spans.append([name,start,end,snippet,search])
    return [spans,imports,notes]

class Snapshot:
    def __init__(self, repo, cache=None, *, require_pin=True, tokenize_search=None, vector_symbols=None):
        self.repo = Path(repo).resolve(strict=True)
        self.commit = self.git("rev-parse","HEAD").decode().strip()
        if require_pin and self.commit != PIN:
            raise EvidenceError("Use the pinned TicketDesk fixture commit.")
        self.spans, self.vectors, self.imports, self.objects = {}, {}, {}, {}
        self.notes = []
        self.stats = {"hits":0,"misses":0}
        self.verified_paths = set()
        self.norms = {}
        self.vector_symbols = vector_symbols
        self.tokenize_search = tokenize_search or (lambda value: re.findall(r"[a-z0-9]+",value.lower()))
        for rec in self.git("ls-tree","-rz","-l",self.commit).split(b"\0"):
            if not rec:
                continue
            meta, raw_path = rec.split(b"\t",1)
            mode,kind,oid,size = meta.decode().split()
            path = raw_path.decode("utf-8")
            parts = path.split("/")
            if (kind != "blob" or mode not in {"100644","100755"}
                or any(p.startswith(".") or p in {"venv","node_modules","__pycache__"} for p in parts)
                or not ((parts[0]=="app" and path.endswith(".py")) or (parts[0]=="web" and path.endswith(".js")))):
                continue
            if int(size)>LIMIT:
                self.notes.append((path,"file_too_large"))
                continue
            self.objects[path] = oid
        if cache is None:
            self._load(None)
        else:
            cache = Path(cache)
            cache.parent.mkdir(parents=True,exist_ok=True)
            conn = sqlite3.connect(cache)
            try:
                with conn:
                    conn.execute("CREATE TABLE IF NOT EXISTS files (version TEXT, path TEXT, oid TEXT, payload TEXT, PRIMARY KEY(version,path,oid))")
                    self._load(conn)
                    conn.execute("DELETE FROM files WHERE rowid NOT IN (SELECT rowid FROM files ORDER BY rowid DESC LIMIT 256)")
            finally:
                conn.close()

    def _load(self, db):
        parsed, missing = {}, {}
        for path,oid in self.objects.items():
            row = db.execute("SELECT payload FROM files WHERE version=? AND path=? AND oid=?",(VERSION,path,oid)).fetchone() if db else None
            if row is None:
                missing[path] = oid
            else:
                try:
                    spans, imports, notes = json.loads(row[0])
                    if not all(isinstance(v,list) for v in (spans,imports,notes)):
                        raise ValueError()
                except (ValueError,TypeError):
                    missing[path] = oid
                    continue
                parsed[path] = (spans,imports,notes)
        self.stats.update(hits=len(parsed), misses=len(missing))
        if missing:
            raw_blobs = self.blobs(list(dict.fromkeys(missing.values())))
            for path,oid in missing.items():
                result = parse(path,oid,raw_blobs[oid])
                parsed[path] = result
                if db:
                    db.execute("INSERT OR REPLACE INTO files VALUES (?,?,?,?)",(VERSION,path,oid,json.dumps(result,separators=(",",":"))))
        for path,(spans,imports,notes) in parsed.items():
            self.imports[path] = imports
            self.notes.extend((path,note) for note in notes)
            module = path.rsplit(".",1)[0].replace("/",".")
            for name,start,end,snippet,search in spans:
                symbol = module+"."+name
                if symbol in self.spans:
                    self.notes.append((path,"duplicate_symbol:"+name))
                    continue
                self.spans[symbol] = Span(path,start,end,symbol,snippet)
                if self.vector_symbols is not None and symbol not in self.vector_symbols:
                    continue
                vector = Counter(self.tokenize_search(symbol+" "+search))
                norm = sqrt(sum(x*x for x in vector.values()))
                self.vectors[symbol] = vector
                self.norms[symbol] = norm

    def git(self,*args,input=None):
        return subprocess.check_output(["git","-C",str(self.repo),*args],input=input,timeout=10,stderr=subprocess.PIPE)

    def blobs(self, oids):
        data = self.git("cat-file","--batch",input=("".join(oid+"\n" for oid in oids)).encode("ascii"))
        out,offset = {},0
        for oid in oids:
            end = data.index(b"\n",offset)
            obj,kind,size = data[offset:end].decode().split()
            if obj!=oid or kind!="blob" or int(size)>LIMIT:
                raise EvidenceError("Unexpected Git object.")
            n = int(size)
            out[oid] = data[end+1:end+1+n]
            offset = end+n+2
        return out

    def similarity(self, query, symbol):
        vector = self.vectors[symbol]
        return sum(vector.get(t,0) for t in query)/(sqrt(len(query))*self.norms[symbol]) if query and self.norms[symbol] else 0

    def resolve_many(self,symbols):
        spans = [self.spans[s] for s in symbols]
        paths = {s.path for s in spans} - self.verified_paths
        if paths:
            raw = self.blobs(list(dict.fromkeys(self.objects[p] for p in sorted(paths))))
            for path in paths:
                lines = raw[self.objects[path]].decode().splitlines()
                for s in self.spans.values():
                    if s.path == path and (not 1 <= s.first <= s.last <= len(lines)
                            or "\n".join(lines[s.first-1:s.last]) != s.snippet):
                        raise EvidenceError("Cached span does not match committed code.")
            self.verified_paths.update(paths)
        return spans
