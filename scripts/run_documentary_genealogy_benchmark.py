#!/usr/bin/env python3
"""LTMD Documentary Genealogy Benchmark 0.2.

Computes reproducible documentary continuity metrics from a private LTMD Universal
Index without emitting source/text hashes, page identifiers, OCR, or object IDs.

This is a documentary/technical benchmark. Exact hash equality is evidence of
representation identity under the declared hash channel; approximate similarity is
reported separately and never establishes semantic, curricular, pedagogical, or
historical equivalence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

BENCHMARK_VERSION = "LTMD_DOCUMENTARY_GENEALOGY_BENCHMARK_0.2"
INDEX_VERSION = "LTMD_U1_UNIVERSAL_INDEX_0.1"
REUSE_VERSION = "LTMD_U1_REUSE_SIMILARITY_0.1"
TEXT_MIN_CHARS = 200
TEXT_MIN_WORDS = 30
DEFAULT_BOOTSTRAP_REPS = 2000
DEFAULT_PERMUTATIONS = 2000
DEFAULT_SEED = 20260901
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _decode(raw: str) -> Any:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return raw


def _ratio(num: int | float, den: int | float) -> float | None:
    if not den:
        return None
    return round(float(num) / float(den), 8)


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(ordered[0], 8)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return round(ordered[lo], 8)
    frac = pos - lo
    return round(ordered[lo] * (1 - frac) + ordered[hi] * frac, 8)


def _bootstrap_transition(
    both: int,
    previous_only: int,
    current_only: int,
    *,
    reps: int,
    rng: random.Random,
) -> dict[str, list[float | None]]:
    """Multinomial bootstrap over the union's three observable membership classes.

    Python 3.12's Random.binomialvariate lets us draw a multinomial efficiently
    without materializing individual hashes. This bootstraps representation-level
    membership, not semantic content.
    """
    union = both + previous_only + current_only
    if union <= 0 or reps <= 0:
        return {"persistence": [], "novelty": [], "turnover": []}
    p_both = both / union
    remaining_prob = 1.0 - p_both
    p_previous_conditional = (previous_only / union) / remaining_prob if remaining_prob else 0.0
    persistence: list[float] = []
    novelty: list[float] = []
    turnover: list[float] = []
    for _ in range(reps):
        b = rng.binomialvariate(union, p_both)
        remaining = union - b
        po = rng.binomialvariate(remaining, p_previous_conditional) if remaining else 0
        co = remaining - po
        prev_n = b + po
        curr_n = b + co
        persistence.append(b / prev_n if prev_n else 0.0)
        novelty.append(co / curr_n if curr_n else 0.0)
        turnover.append((po + co) / union)
    return {"persistence": persistence, "novelty": novelty, "turnover": turnover}


def _ci(values: list[float], confidence: float = 0.95) -> list[float] | None:
    if not values:
        return None
    alpha = (1.0 - confidence) / 2.0
    lo = _percentile(values, alpha)
    hi = _percentile(values, 1.0 - alpha)
    assert lo is not None and hi is not None
    return [lo, hi]


def load_index(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not path.is_file():
        raise RuntimeError("Universal Index artifact is unavailable")
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")}
        if not {"index_meta", "pages"}.issubset(tables):
            raise RuntimeError("not an LTMD Universal Index")
        columns = {row[1] for row in con.execute("PRAGMA table_info(pages)")}
        required = {
            "id", "canonical_viewer_key", "catalog_generation", "source_sha256",
            "search_text_sha256", "ocr_char_count", "ocr_word_count",
        }
        missing = sorted(required - columns)
        if missing:
            raise RuntimeError("Universal Index pages table missing: " + ", ".join(missing))
        meta = {key: _decode(value) for key, value in con.execute("SELECT key,value FROM index_meta")}
        if meta.get("builder_version") != INDEX_VERSION:
            raise RuntimeError("unsupported Universal Index version")
        rows = [dict(row) for row in con.execute(
            """
            SELECT id,canonical_viewer_key,catalog_generation,source_sha256,
                   search_text_sha256,ocr_char_count,ocr_word_count
            FROM pages ORDER BY id
            """
        )]
    finally:
        con.close()
    if not rows:
        raise RuntimeError("Universal Index contains no pages")
    return meta, rows


def load_reuse(path: Path | None) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if path is None:
        return None, []
    if not path.is_file():
        raise RuntimeError("reuse/similarity artifact is unavailable")
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"meta", "similarity_candidates"}.issubset(tables):
            raise RuntimeError("not an LTMD reuse/similarity artifact")
        meta = {key: _decode(value) for key, value in con.execute("SELECT key,value FROM meta")}
        version = meta.get("artifact_version")
        if version != REUSE_VERSION:
            raise RuntimeError("unsupported reuse/similarity artifact version")
        candidates = [dict(row) for row in con.execute(
            "SELECT page_a,page_b,jaccard,tier FROM similarity_candidates ORDER BY page_a,page_b"
        )]
    finally:
        con.close()
    return meta, candidates


def _channel_maps(
    rows: list[dict[str, Any]], channel: str
) -> tuple[list[int], dict[int, Counter[str]], dict[int, set[str]], int]:
    generations = sorted({int(row["catalog_generation"]) for row in rows if row["catalog_generation"] is not None})
    counts: dict[int, Counter[str]] = {g: Counter() for g in generations}
    invalid_hash_rows = 0
    for row in rows:
        gen = row["catalog_generation"]
        if gen is None:
            continue
        if channel == "source":
            value = row.get("source_sha256")
        elif channel == "text_admissible":
            if int(row.get("ocr_char_count") or 0) < TEXT_MIN_CHARS or int(row.get("ocr_word_count") or 0) < TEXT_MIN_WORDS:
                continue
            value = row.get("search_text_sha256")
        elif channel == "text_all":
            value = row.get("search_text_sha256")
        else:
            raise ValueError(channel)
        if not isinstance(value, str) or not SHA256_RE.fullmatch(value.lower()):
            invalid_hash_rows += 1
            continue
        counts[int(gen)][value.lower()] += 1
    sets = {g: set(counter) for g, counter in counts.items()}
    return generations, counts, sets, invalid_hash_rows


def _transition_records(
    generations: list[int],
    counts: dict[int, Counter[str]],
    sets: dict[int, set[str]],
    *,
    bootstrap_reps: int,
    seed: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    rng = random.Random(seed)
    for previous, current in zip(generations, generations[1:]):
        a = sets[previous]
        b = sets[current]
        both_set = a & b
        previous_only = a - b
        current_only = b - a
        both = len(both_set)
        po = len(previous_only)
        co = len(current_only)
        union_n = both + po + co
        bootstrap = _bootstrap_transition(both, po, co, reps=bootstrap_reps, rng=rng)

        previous_occurrences = sum(counts[previous].values())
        current_occurrences = sum(counts[current].values())
        matched_occurrences = sum(min(counts[previous][h], counts[current][h]) for h in both_set)
        occurrence_union = previous_occurrences + current_occurrences - matched_occurrences

        records.append({
            "previous_generation": previous,
            "current_generation": current,
            "generation_gap": current - previous,
            "distinct_representations": {
                "previous": len(a),
                "current": len(b),
                "shared": both,
                "previous_only": po,
                "current_only": co,
                "union": union_n,
                "persistence_rate": _ratio(both, len(a)),
                "novelty_rate": _ratio(co, len(b)),
                "turnover_rate": _ratio(po + co, union_n),
                "persistence_rate_bootstrap_95ci": _ci(bootstrap["persistence"]),
                "novelty_rate_bootstrap_95ci": _ci(bootstrap["novelty"]),
                "turnover_rate_bootstrap_95ci": _ci(bootstrap["turnover"]),
            },
            "page_occurrences": {
                "previous": previous_occurrences,
                "current": current_occurrences,
                "matched_by_exact_representation": matched_occurrences,
                "persistence_rate": _ratio(matched_occurrences, previous_occurrences),
                "novelty_rate": _ratio(current_occurrences - matched_occurrences, current_occurrences),
                "turnover_rate": _ratio(
                    previous_occurrences + current_occurrences - 2 * matched_occurrences,
                    occurrence_union,
                ),
            },
        })
    return records


def _survival_summary(generations: list[int], sets: dict[int, set[str]]) -> dict[str, Any]:
    if not generations:
        return {"cohorts": [], "kaplan_meier": [], "median_survival_steps": None}
    presence: dict[str, list[int]] = defaultdict(list)
    for pos, gen in enumerate(generations):
        for value in sets[gen]:
            presence[value].append(pos)

    durations: list[tuple[int, bool]] = []
    cohorts: Counter[int] = Counter()
    for positions in presence.values():
        first = positions[0]
        cohorts[generations[first]] += 1
        position_set = set(positions)
        end = first
        while end + 1 < len(generations) and (end + 1) in position_set:
            end += 1
        duration = end - first + 1
        censored = end == len(generations) - 1
        durations.append((duration, censored))

    # Kaplan-Meier in discrete generation-presence steps. A representation present only
    # in its entry generation has duration=1; failure at t means absence by next step.
    km: list[dict[str, Any]] = []
    survival = 1.0
    max_t = max((d for d, _ in durations), default=0)
    for t in range(1, max_t + 1):
        at_risk = sum(1 for d, _ in durations if d >= t)
        failures = sum(1 for d, censored in durations if d == t and not censored)
        censored_n = sum(1 for d, censored in durations if d == t and censored)
        if at_risk and failures:
            survival *= (1.0 - failures / at_risk)
        km.append({
            "step": t,
            "at_risk": at_risk,
            "failures": failures,
            "censored": censored_n,
            "survival_probability": round(survival, 8),
        })
    median = next((row["step"] for row in km if row["survival_probability"] <= 0.5), None)
    return {
        "cohorts": [{"entry_generation": gen, "distinct_representations": n} for gen, n in sorted(cohorts.items())],
        "kaplan_meier": km,
        "median_survival_steps": median,
        "interpretation": "Discrete exact-representation survival from first appearance until first observed generation gap; right-censored at the final corpus generation.",
    }


def _temporal_negative_control(
    generations: list[int],
    sets: dict[int, set[str]],
    *,
    permutations: int,
    seed: int,
) -> dict[str, Any]:
    def mean_adjacent(order: list[int]) -> float:
        vals = []
        for a, b in zip(order, order[1:]):
            vals.append(len(sets[a] & sets[b]) / len(sets[a]) if sets[a] else 0.0)
        return statistics.fmean(vals) if vals else 0.0

    observed = mean_adjacent(generations)
    if len(generations) < 3 or permutations <= 0:
        return {
            "observed_mean_adjacent_persistence": round(observed, 8),
            "permutations": 0,
            "null_mean": None,
            "null_95_interval": None,
            "upper_tail_p_value": None,
        }
    rng = random.Random(seed)
    null: list[float] = []
    for _ in range(permutations):
        order = generations[:]
        rng.shuffle(order)
        null.append(mean_adjacent(order))
    upper = (1 + sum(value >= observed for value in null)) / (len(null) + 1)
    return {
        "observed_mean_adjacent_persistence": round(observed, 8),
        "permutations": permutations,
        "null_mean": round(statistics.fmean(null), 8),
        "null_95_interval": [_percentile(null, 0.025), _percentile(null, 0.975)],
        "upper_tail_p_value": round(upper, 8),
        "interpretation": "Permutation control asks whether chronological adjacency carries more exact documentary continuity than arbitrary generation ordering; it is not a causal or historical-significance test.",
    }


def _near_exact_sensitivity(
    rows: list[dict[str, Any]], candidates: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if not candidates:
        return None
    page_generation = {int(row["id"]): int(row["catalog_generation"]) for row in rows if row["catalog_generation"] is not None}
    generation_order = sorted(set(page_generation.values()))
    adjacency = {(a, b) for a, b in zip(generation_order, generation_order[1:])}
    counts: Counter[tuple[int, int, str]] = Counter()
    skipped = 0
    for candidate in candidates:
        ga = page_generation.get(int(candidate["page_a"]))
        gb = page_generation.get(int(candidate["page_b"]))
        if ga is None or gb is None or ga == gb:
            continue
        pair = tuple(sorted((ga, gb)))
        if pair not in adjacency:
            continue
        tier = str(candidate["tier"])
        if tier not in {"near_exact_candidate", "similarity_candidate"}:
            skipped += 1
            continue
        counts[(pair[0], pair[1], tier)] += 1
    transitions = []
    for a, b in sorted(adjacency):
        near = counts[(a, b, "near_exact_candidate")]
        similar = counts[(a, b, "similarity_candidate")]
        transitions.append({
            "previous_generation": a,
            "current_generation": b,
            "near_exact_candidate_pairs": near,
            "similarity_candidate_pairs": similar,
            "all_verified_nonexact_pairs": near + similar,
        })
    return {
        "state": "sensitivity_signal_only",
        "transitions": transitions,
        "skipped_unknown_tier_rows": skipped,
        "guard": "near_exact_candidate != exact_identity; similarity_candidate != semantic_equivalence",
    }


def benchmark(
    index_path: Path,
    *,
    reuse_path: Path | None = None,
    bootstrap_reps: int = DEFAULT_BOOTSTRAP_REPS,
    permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    meta, rows = load_index(index_path)
    reuse_meta, candidates = load_reuse(reuse_path)
    declared_pages = int(meta.get("unique_pages", len(rows)))
    if declared_pages != len(rows):
        raise RuntimeError("Universal Index unique_pages does not match pages table")

    channels: dict[str, Any] = {}
    for offset, channel in enumerate(("source", "text_admissible", "text_all")):
        generations, counts, sets, invalid_hash_rows = _channel_maps(rows, channel)
        if invalid_hash_rows:
            raise RuntimeError(f"{channel} contains {invalid_hash_rows} rows with invalid SHA-256")
        channels[channel] = {
            "generations": generations,
            "generation_count": len(generations),
            "transitions": _transition_records(
                generations, counts, sets,
                bootstrap_reps=bootstrap_reps,
                seed=seed + offset * 100003,
            ),
            "survival": _survival_summary(generations, sets),
            "temporal_negative_control": _temporal_negative_control(
                generations, sets,
                permutations=permutations,
                seed=seed + offset * 200003,
            ),
        }

    near_exact = _near_exact_sensitivity(rows, candidates)
    result = {
        "benchmark_version": BENCHMARK_VERSION,
        "status": "PASS",
        "scope": "automated_documentary_genealogy_without_human_validation",
        "parameters": {
            "bootstrap_reps": bootstrap_reps,
            "temporal_permutations": permutations,
            "seed": seed,
            "text_admissibility": {"min_ocr_chars": TEXT_MIN_CHARS, "min_ocr_words": TEXT_MIN_WORDS},
        },
        "corpus": {
            "pages": len(rows),
            "canonical_objects": len({row["canonical_viewer_key"] for row in rows}),
            "generations": sorted({int(row["catalog_generation"]) for row in rows if row["catalog_generation"] is not None}),
        },
        "channels": channels,
        "near_exact_sensitivity": near_exact,
        "sources": {
            "universal_index_sha256": sha256_file(index_path),
            "reuse_similarity_sha256": sha256_file(reuse_path) if reuse_path else None,
            "reuse_similarity_version": reuse_meta.get("artifact_version") if reuse_meta else None,
        },
        "privacy": {
            "hash_values_emitted": False,
            "page_identifiers_emitted": False,
            "object_identifiers_emitted": False,
            "ocr_text_emitted": False,
        },
        "scientific_state": {
            "human_validation": False,
            "construct_validity_claimed": False,
            "text_verified": False,
            "semantic_ready": False,
            "historical_truth_claimed": False,
            "causal_replacement_claimed": False,
            "near_exact_is_exact_identity": False,
            "similarity_is_semantic_equivalence": False,
        },
        "interpretation_guard": (
            "Rates quantify exact documentary representation continuity/novelty/turnover under declared hash channels. "
            "They do not establish semantic equivalence, curricular intent, pedagogical meaning, construct validity, or historical truth."
        ),
    }
    return result


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run LTMD Documentary Genealogy Benchmark 0.2")
    parser.add_argument("--index", type=Path, required=True, help="Private LTMD Universal Index SQLite")
    parser.add_argument("--reuse", type=Path, help="Optional private LTMD reuse/similarity SQLite")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--bootstrap-reps", type=int, default=DEFAULT_BOOTSTRAP_REPS)
    parser.add_argument("--permutations", type=int, default=DEFAULT_PERMUTATIONS)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.bootstrap_reps < 0 or args.permutations < 0:
        raise SystemExit("bootstrap/permutation counts must be non-negative")
    result = benchmark(
        args.index,
        reuse_path=args.reuse,
        bootstrap_reps=args.bootstrap_reps,
        permutations=args.permutations,
        seed=args.seed,
    )
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
