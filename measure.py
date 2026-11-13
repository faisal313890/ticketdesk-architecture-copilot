"""Measure local index startup, retained allocations and warmed in-process Q&A."""
import argparse
import gc
import json
from pathlib import Path
import statistics
import tempfile
from time import perf_counter_ns
import tracemalloc

from copilot.core import Copilot, Snapshot
from evaluate import cases
from tools import prior_core

def elapsed(factory, repeats=12):
    observations=[]
    for _ in range(repeats):
        t=perf_counter_ns()
        result=factory()
        observations.append((perf_counter_ns()-t)/1e6)
        del result
    return round(statistics.median(observations),3)

def retained(factory):
    gc.collect()
    tracemalloc.start()
    index=factory()
    gc.collect()
    n=tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    del index
    return n

def ask_latency(copilot,questions):
    for q in questions:
        copilot.ask(q)
    obs=[]
    for _ in range(200):
        for q in questions:
            t=perf_counter_ns()
            copilot.ask(q)
            obs.append((perf_counter_ns()-t)/1e3)
    return round(statistics.median(obs),2)

def measure(repo):
    old=lambda:prior_core.Snapshot(repo)
    new=lambda:Snapshot(repo)
    # Shared answerable cases and two unsupported cases for an even comparison.
    shared=[q for i,q,*_ in cases() if i in {"Q01","Q02","Q04","Q06","Q09","Q10"}]
    all_q=[q for _,q,*_ in cases()]
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        fixed=folder/"warm.sqlite3"
        index=Snapshot(repo,fixed)
        assert index.stats=={"hits":0,"misses":13}
        assert Snapshot(repo,fixed).stats=={"hits":13,"misses":0}
        count=iter(range(12))
        return dict(repeats_per_startup=12, shared_questions=len(shared), repeated_query_rounds=200,
                    previous_startup_ms=elapsed(old), updated_uncached_startup_ms=elapsed(new),
                    updated_cold_cache_startup_ms=elapsed(lambda:Snapshot(repo,folder/f"cold-{next(count)}.sqlite3")),
                    updated_warm_cache_startup_ms=elapsed(lambda:Snapshot(repo,fixed)),
                    previous_retained_python_bytes=retained(old),updated_retained_python_bytes=retained(new),
                    previous_warm_qa_us=ask_latency(prior_core.Copilot(old()),shared),
                    updated_warm_qa_us=ask_latency(Copilot(new()),shared),
                    updated_full_benchmark_warm_qa_us=ask_latency(Copilot(new()),all_q),
                    warm_cache_bytes=fixed.stat().st_size)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo",required=True)
    p.add_argument("--out")
    args=p.parse_args()
    result=json.dumps(measure(args.repo),indent=2)+"\n"
    if args.out:
        Path(args.out).write_text(result,encoding="utf-8")
    print(result,end="")
