"""Retrieval evaluation for the semantic corpus: lexical vs semantic vs hybrid.

The rescue floor is chosen on the 'dev' split only. 'heldout' (round 1, seen
before the hints/hybrid change) and 'heldout2' (fresh, never used to tune) are
then reported at that floor. Output is retrieval quality only, NOT answer
correctness on the web.
"""
import argparse
import json
import math
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from semantic_service import Index, MODEL, ROOT

DOCS = ROOT / "docs/rag"
K = 3        # top-k used for recall and for the rescue rule
K_PLAN = 5   # candidates handed to the planner
MODES = ("lexical", "semantic", "hybrid")
# Noise cut for candidates passed to the planner (hybrid scale). Not a relevance
# claim: the sweep below shows no floor separates adversarial from valid questions.
CANDIDATE_FLOOR = 0.4


def recall(rows, search, k, floor=None):
    ok = 0
    for row in rows:
        found = [h["id"] for h in search(row["q"], max(k, 1))[:k] if floor is None or h["score"] >= floor]
        ok += any(r in found for r in row["relevant"])
    return round(ok / len(rows), 3)


def leaks(rows, search, floor):
    bad = []
    for row in rows:
        shown = [h["id"] for h in search(row["q"], K)[:K] if h["score"] >= floor]
        if any(i not in row["acceptable_ids"] for i in shown):
            bad.append({"q": row["q"], "surfaced": shown})
    return round(len(bad) / len(rows), 3), bad


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    v1 = json.loads((DOCS / "semantic-eval-questions.json").read_text(encoding="utf-8"))
    v2 = json.loads((DOCS / "semantic-eval-questions-v2.json").read_text(encoding="utf-8"))
    index = Index()
    by = lambda mode: (lambda q, k: index.search(q, k, mode))
    pick = lambda rows, name: [r for r in rows if r["split"] == name]
    sets = {"dev": (pick(v1["paraphrase"], "dev"), pick(v1["adversarial"], "dev")),
            "heldout_round1": (pick(v1["paraphrase"], "heldout"), pick(v1["adversarial"], "heldout")),
            "heldout2": (v2["paraphrase"], v2["adversarial"])}

    hybrid = by("hybrid")
    sweep = []
    for n in range(0, 41):
        floor = round(0.3 + 0.025 * n, 3)
        leak, _ = leaks(sets["dev"][1], hybrid, floor)
        sweep.append({"floor": floor, "dev_recall_at_3": recall(sets["dev"][0], hybrid, K, floor), "dev_adversarial_leak": leak})
    clean = [s for s in sweep if s["dev_adversarial_leak"] == 0]
    chosen = (max(clean, key=lambda s: (s["dev_recall_at_3"], -s["floor"])) if clean else sweep[-1])["floor"]

    report = {}
    for name, (para, adv) in sets.items():
        report[name] = {"n_paraphrase": len(para), "n_adversarial": len(adv)}
        for mode in MODES:
            s = by(mode)
            entry = {"recall_at_1": recall(para, s, 1), "recall_at_3": recall(para, s, K), "recall_at_5": recall(para, s, K_PLAN)}
            if mode == "hybrid":
                entry["recall_at_5_above_candidate_floor"] = recall(para, s, K_PLAN, CANDIDATE_FLOOR)
                entry["recall_at_3_above_floor"] = recall(para, s, K, chosen)
                leak, bad = leaks(adv, s, chosen)
                entry["adversarial_leak_above_floor"] = leak
                entry["adversarial_leaks"] = bad
            report[name][mode] = entry

    questions = [r["q"] for r in sets["heldout2"][0] + sets["heldout2"][1]]
    lat = []
    for q in questions * 3:
        t = time.perf_counter(); index.search(q, K_PLAN, "hybrid"); lat.append((time.perf_counter() - t) * 1000)
    lat.sort()
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "retrieval quality over the semantic corpus only; not answer correctness on the web",
        "model": MODEL, "dimensions": index.dimensions, "metric": "cosine", "lexical_weight": 0.5,
        "corpus_version": index.version, "chunks": len(index.chunks), "k": K, "k_planner_candidates": K_PLAN,
        "chosen_rescue_floor": chosen, "threshold_sweep_dev": sweep, "results": report,
        "latency_ms_in_process": {"n": len(lat), "median": round(statistics.median(lat), 1),
                                  "p95": round(lat[math.ceil(0.95 * len(lat)) - 1], 1)},
        "heldout2_detail": [{"q": r["q"], "relevant": r["relevant"], "hybrid_top5": by("hybrid")(r["q"], 5)}
                            for r in sets["heldout2"][0]],
    }
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("corpus_version", "chosen_rescue_floor", "results", "latency_ms_in_process")},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
