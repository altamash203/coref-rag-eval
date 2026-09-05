#!/usr/bin/env python3
"""Audit the `coref_critical` flags in tests 4-7, and measure query-term injection.

Two questions, both answered from the committed JSON only (no models, no retrieval, no notebook):

1. **Is the flag supported by the data?** A question is only genuinely coref-critical if the
   coref rewrite of its gold chunk(s) *adds* content words the original chunk did not have.
   Some flagged questions have rewrites that add nothing — the entity was already in the chunk
   (test-5 q3: "Chiang Kai-shek deployed his best army" -> "Chiang Kai-shek deployed
   Chiang Kai-shek's best army"). Those are reported as `critical_unsupported`.

2. **Does the rewrite inject the query's own terms?** If the tokens the rewrite added to the gold
   chunk also appear in the question, then improved recall on that question is partly mechanical:
   the rewrite handed the retriever the exact string the query was searching for. Reported as
   `injection` counts.

Two tokenisers are computed for every question, because the choice changes the answer:

* `hyphenated` (primary) — keeps hyphenated alphanumeric identifiers whole, so `F-1` and `S-II`
  survive as tokens.
* `strict` (sensitivity check) — splits on every non-alphanumeric character, so `F-1` becomes
  `f` + `1` and both are discarded by the length filter.

The primary rule is the hyphen-aware one: under `strict`, test-4 q15 ("These engines" -> "The F-1
engines") and q16 ("It" -> "The S-II") are misclassified as adding nothing, when the rewrite plainly
introduced a new entity string. Both counts are reported so the difference is auditable.

Outputs:
  * `analysis/relabel_report.md`   — per-test counts, the full unsupported list, injection lists
  * `analysis/relabel_report.json` — the same data, machine-readable
  * adds a `critical_confirmed` boolean to each question in every `eval_questions.json`
    (with `--write-flags`), alongside — never replacing — the original `coref_critical` flag.

Usage:
    python analysis/relabel_critical.py                # report only
    python analysis/relabel_critical.py --write-flags  # report + annotate eval_questions.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "analysis"
TESTS = ["test-4", "test-5", "test-6", "test-7"]

# Self-contained stopword list so the script needs no NLTK download and stays deterministic.
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "also", "am", "an", "and", "any",
    "are", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "cannot", "could", "did", "do", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "just", "me", "more", "most", "must", "my", "myself", "no", "nor", "not", "now",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shall", "she", "should", "so", "some", "such", "than", "that", "the",
    "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "will", "with", "would", "you", "your",
    "yours", "yourself", "yourselves",
}

# Primary: keep hyphenated alphanumeric identifiers (f-1, s-ii, bge-small) as one token.
HYPHENATED_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Sensitivity check: split on every non-alphanumeric character.
STRICT_RE = re.compile(r"[a-z0-9]+")

TOKENISERS = {"hyphenated": HYPHENATED_RE, "strict": STRICT_RE}
PRIMARY = "hyphenated"

# Queries the notebooks reported as recovered (baseline miss -> coref hit), transcribed from the
# committed findings files. The notebooks ship with outputs stripped, so these lists are the only
# committed record of *which* queries flipped. test-6 names counts but not q_ids, so it is unknown.
RECOVERED = {
    "test-4": {
        "variant": "coref_dense",
        "q_ids": [2, 4, 19, 26],
        "source": "test-4/test-4-findings.md (flips table)",
    },
    "test-5": {
        "variant": "coref_hybrid",
        "q_ids": [16, 17],
        "source": "test-5/test-5-findings.md (Recovered by coref_hybrid)",
    },
    "test-6": {
        "variant": "coref_dense",
        "q_ids": None,
        "source": "test-6/test-6-findings.md reports 3 recovered but does not name them",
    },
    "test-7": {
        "variant": "coref_dense",
        "q_ids": [1, 9, 10, 12],
        "source": "test-7/test-7-findings.md (per-query recovered table)",
    },
}


def content_tokens(text: str, tokeniser: str = PRIMARY) -> set[str]:
    """Lowercased content words: drop stopwords and tokens of length <= 2."""
    return {
        tok
        for tok in TOKENISERS[tokeniser].findall(text.lower())
        if len(tok) > 2 and tok not in STOPWORDS
    }


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def chunk_index(chunks: list[dict]) -> dict[int, str]:
    return {c["chunk_id"]: c["text"] for c in chunks}


def analyse_test(test: str) -> dict:
    data_dir = REPO_ROOT / test / f"{test}-data"
    originals = chunk_index(load_json(data_dir / "original_chunks.json"))
    corefs = chunk_index(load_json(data_dir / "coref_chunks.json"))
    questions = load_json(data_dir / "eval_questions.json")

    per_question = []
    for q in questions:
        gold_ids = q["gold_chunk_ids"]
        orig_text = " ".join(originals[g] for g in gold_ids)
        coref_text = " ".join(corefs[g] for g in gold_ids)
        flagged = bool(q.get("coref_critical"))

        record = {
            "q_id": q["q_id"],
            "question": q["question"],
            "gold_chunk_ids": gold_ids,
            "coref_critical": flagged,
            "original_gold_text": orig_text,
            "coref_gold_text": coref_text,
        }

        for name in TOKENISERS:
            added = content_tokens(coref_text, name) - content_tokens(orig_text, name)
            injected = added & content_tokens(q["question"], name)
            record[name] = {
                "added_tokens": sorted(added),
                "injected_tokens": sorted(injected),
                "critical_confirmed": flagged and bool(added),
                "injection": flagged and bool(injected),
            }

        # Second sensitivity axis: `added` computed per gold chunk rather than over their union.
        # For a multi-gold question, a term added to chunk A can already be present in chunk B, so
        # the union hides it. Primary tokeniser only.
        per_chunk_added: set[str] = set()
        for g in gold_ids:
            per_chunk_added |= content_tokens(corefs[g]) - content_tokens(originals[g])
        record["per_chunk"] = {
            "added_tokens": sorted(per_chunk_added),
            "injected_tokens": sorted(per_chunk_added & content_tokens(q["question"])),
            "critical_confirmed": flagged and bool(per_chunk_added),
            "injection": flagged and bool(per_chunk_added & content_tokens(q["question"])),
        }

        # Flatten the primary tokeniser's verdict to the top level for convenience.
        record["added_tokens"] = record[PRIMARY]["added_tokens"]
        record["injected_tokens"] = record[PRIMARY]["injected_tokens"]
        record["critical_confirmed"] = record[PRIMARY]["critical_confirmed"]
        record["injection"] = record[PRIMARY]["injection"]
        per_question.append(record)

    flagged_qs = [r for r in per_question if r["coref_critical"]]
    counts = {}
    for name in list(TOKENISERS) + ["per_chunk"]:
        counts[name] = {
            "confirmed": sum(1 for r in flagged_qs if r[name]["critical_confirmed"]),
            "unsupported": sum(1 for r in flagged_qs if not r[name]["critical_confirmed"]),
            "injection": sum(1 for r in flagged_qs if r[name]["injection"]),
        }

    disagree = sorted(
        r["q_id"]
        for r in flagged_qs
        if r["hyphenated"]["critical_confirmed"] != r["strict"]["critical_confirmed"]
    )
    per_chunk_disagree = sorted(
        r["q_id"]
        for r in flagged_qs
        if r["per_chunk"]["critical_confirmed"] != r[PRIMARY]["critical_confirmed"]
    )

    return {
        "test": test,
        "tokeniser_primary": PRIMARY,
        "n_chunks": len(originals),
        "n_questions": len(questions),
        "n_flagged_critical": len(flagged_qs),
        "n_critical_confirmed": counts[PRIMARY]["confirmed"],
        "n_critical_unsupported": counts[PRIMARY]["unsupported"],
        "n_injection": counts[PRIMARY]["injection"],
        "counts_by_tokeniser": counts,
        "tokeniser_disagreement_q_ids": disagree,
        "per_chunk_disagreement_q_ids": per_chunk_disagree,
        "questions": per_question,
        "unsupported": [r for r in flagged_qs if not r["critical_confirmed"]],
        "injection_questions": [r for r in flagged_qs if r["injection"]],
    }


def write_flags(results: list[dict]) -> list[str]:
    """Add `critical_confirmed` to each question, preserving `coref_critical` untouched."""
    touched = []
    for res in results:
        test = res["test"]
        path = REPO_ROOT / test / f"{test}-data" / "eval_questions.json"
        questions = load_json(path)
        by_id = {r["q_id"]: r for r in res["questions"]}
        for q in questions:
            r = by_id[q["q_id"]]
            # Never modify `coref_critical`; only annotate alongside it.
            q["critical_confirmed"] = r["critical_confirmed"]
            q["critical_added_tokens"] = r["added_tokens"]
            q["query_term_injection"] = r["injection"]
        with path.open("w", encoding="utf-8") as fh:
            json.dump(questions, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        touched.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
    return touched


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def build_report(results: list[dict], flags_written: bool) -> str:
    out: list[str] = []
    add = out.append

    add("# Coref-critical relabelling and query-term injection audit")
    add("")
    add("Generated by `analysis/relabel_critical.py`. Reads only the committed JSON in")
    add("`test-*/test-*-data/`; no notebook, model, or retrieval run is involved.")
    add("")

    add("## Method")
    add("")
    add("For every question flagged `coref_critical: true` in tests 4-7:")
    add("")
    add("1. Concatenate the question's gold chunk(s), once from `original_chunks.json` and once")
    add("   from `coref_chunks.json`.")
    add("2. Tokenise both into lowercased content words, dropping a fixed English stopword list and")
    add("   every token of length <= 2.")
    add("3. `added = coref_tokens - original_tokens`.")
    add("4. `critical_confirmed` if `added` is non-empty (the rewrite genuinely introduced entity")
    add("   information the original gold chunk lacked); `critical_unsupported` if `added` is empty.")
    add("5. `injection` if `added` intersects the question's own content-word tokens — the rewrite")
    add("   inserted into the gold chunk a term the query is searching for.")
    add("")
    add("### Two tokenisers, because the choice changes the answer")
    add("")
    add("| tokeniser | pattern | `F-1` becomes |")
    add("| --- | --- | --- |")
    add("| `hyphenated` (**primary**) | `[a-z0-9]+(?:-[a-z0-9]+)*` | `f-1` (kept) |")
    add("| `strict` (sensitivity check) | `[a-z0-9]+` | `f` + `1` (both dropped, length <= 2) |")
    add("")
    add("A second axis: `added` is computed over the **union** of a question's gold chunks. For a")
    add("question with more than one gold chunk, a term the rewrite added to chunk A may already be")
    add("present in chunk B, so the union hides it. The `per_chunk` variant takes the union of the")
    add("per-chunk differences instead. Both are reported.")
    add("")
    add("The hyphen-aware rule is primary. Under `strict`, test-4 q15 (*\"These engines\"* ->")
    add("*\"The F-1 engines\"*) and q16 (*\"It provided thrust\"* -> *\"The S-II provided thrust\"*)")
    add("are counted as adding nothing, even though the rewrite plainly introduced a new entity")
    add("string that the query names. That is a tokenisation artefact, not a finding. Both counts")
    add("are reported below so the difference is visible; they differ only on test-4.")
    add("")
    add("**Important scope limit:** every Recall@5 / R@5_crit number reported in the")
    add("`test-*-findings.md` files and in the README was computed against the **original**")
    add("`coref_critical` labels. Nothing here re-runs retrieval, so no per-test \"critical\" metric")
    add("has been recomputed against the `critical_confirmed` labels. Treat the counts below as an")
    add("audit of the label set, not as corrected metrics. Recomputing the critical-subset metrics")
    add("would require re-running the notebooks.")
    add("")

    add("## Summary (primary `hyphenated` tokeniser)")
    add("")
    add("| test | questions | flagged `coref_critical` | `critical_confirmed` | `critical_unsupported` (rewrite added nothing) | query-term injection |")
    add("| --- | --- | --- | --- | --- | --- |")
    for r in results:
        add(
            f"| {r['test']} | {r['n_questions']} | {r['n_flagged_critical']} | "
            f"{r['n_critical_confirmed']} | {r['n_critical_unsupported']} | "
            f"{r['n_injection']}/{r['n_flagged_critical']} |"
        )
    add("")
    add("`critical_unsupported` = the coref rewrite of the gold chunk(s) adds **no new content word**")
    add("at all, so the entity the question names was already present in the original chunk. Coref")
    add("cannot have helped retrieval on those questions by the mechanism the hypothesis proposes.")
    add("")
    add("`query-term injection` = the tokens the rewrite added to the gold chunk overlap the")
    add("question's own content words. On these questions any recall gain is partly mechanical:")
    add("the rewrite put the query's search term into the indexed text.")
    add("")

    add("### Sensitivity: the same counts under the other two rules")
    add("")
    add("| test | unsupported (hyphenated, primary) | unsupported (strict) | unsupported (per_chunk) | injection (hyphenated) | injection (strict) | injection (per_chunk) |")
    add("| --- | --- | --- | --- | --- | --- | --- |")
    for r in results:
        c = r["counts_by_tokeniser"]
        add(
            f"| {r['test']} | {c['hyphenated']['unsupported']} | {c['strict']['unsupported']} | "
            f"{c['per_chunk']['unsupported']} | {c['hyphenated']['injection']} | "
            f"{c['strict']['injection']} | {c['per_chunk']['injection']} |"
        )
    add("")
    add("Questions where the rules disagree:")
    add("")
    add("| test | hyphenated vs strict | union vs per_chunk |")
    add("| --- | --- | --- |")
    for r in results:
        tok = ", ".join(f"q{q}" for q in r["tokeniser_disagreement_q_ids"]) or "—"
        pc = ", ".join(f"q{q}" for q in r["per_chunk_disagreement_q_ids"]) or "—"
        add(f"| {r['test']} | {tok} | {pc} |")
    add("")
    add("Only test-4 is affected by either. Its unsupported count is **7** under the primary rule,")
    add("**9** under `strict`, and **4** under `per_chunk` — the spread is worth knowing before")
    add("quoting any single number.")
    add("")

    if flags_written:
        add("A `critical_confirmed` field (plus `critical_added_tokens` and `query_term_injection`,")
        add("all from the primary tokeniser) has been added to each question in")
        add("`test-*/test-*-data/eval_questions.json`. The original `coref_critical` flags are")
        add("untouched, so the relabelling is auditable.")
        add("")

    add("---")
    add("")
    add("## Cross-reference: were the queries coref actually recovered injection cases?")
    add("")
    add("This is the sharpest form of the question. The findings files record which queries flipped")
    add("from baseline-miss to coref-hit. If those specific queries are also the ones whose rewrite")
    add("inserted the query's own search term into the gold chunk, the measured gain is hard to")
    add("separate from a lexical term match.")
    add("")
    add("| test | variant | recovered q_ids | injection (union rule) | injection (per_chunk rule) |")
    add("| --- | --- | --- | --- | --- |")
    for r in results:
        meta = RECOVERED[r["test"]]
        if meta["q_ids"] is None:
            add(f"| {r['test']} | {meta['variant']} | not recorded | — | — |")
            continue
        by_id = {q["q_id"]: q for q in r["questions"]}
        ids = ", ".join(f"q{i}" for i in meta["q_ids"])
        n_union = sum(1 for i in meta["q_ids"] if by_id[i]["injection"])
        n_pc = sum(1 for i in meta["q_ids"] if by_id[i]["per_chunk"]["injection"])
        total = len(meta["q_ids"])
        add(
            f"| {r['test']} | {meta['variant']} | {ids} | {n_union}/{total} | {n_pc}/{total} |"
        )
    add("")
    for r in results:
        meta = RECOVERED[r["test"]]
        add(f"- **{r['test']}** — source: {meta['source']}")
    add("")
    add("Read this carefully in both directions:")
    add("")
    add("- **test-7**: every one of the four queries coref recovered is a query-term injection case.")
    add("  Three of the four resolve a pronoun to `Lincoln`, which the query also names.")
    add("- **test-4**: all four recovered queries are injection cases under the `per_chunk` rule")
    add("  (three of four under the union rule, where q2's added tokens are masked by its second")
    add("  gold chunk).")
    add("- **test-5**: the two queries the hybrid recovered are **not** injection cases — their")
    add("  rewrites added terms the query does not contain. This is the counterexample, and it is")
    add("  the test where the dense-only gain was zero.")
    add("- **test-6**: cannot be checked. The findings file reports 3 recovered queries without")
    add("  naming them, and the notebook ships with outputs stripped, so the q_ids are not in the")
    add("  repository. This gap is not an inference either way.")
    add("")
    add("---")
    add("")
    add("## Per-test detail")
    add("")

    for r in results:
        add(f"### {r['test']}")
        add("")
        add(
            f"{r['n_chunks']} chunks, {r['n_questions']} questions, "
            f"{r['n_flagged_critical']} flagged coref-critical."
        )
        add("")
        add(f"- confirmed: **{r['n_critical_confirmed']}/{r['n_flagged_critical']}**")
        add(
            f"- unsupported (rewrite added no new content word): "
            f"**{r['n_critical_unsupported']}/{r['n_flagged_critical']}**"
        )
        add(f"- query-term injection: **{r['n_injection']}/{r['n_flagged_critical']}**")
        add("")

        if r["unsupported"]:
            add("#### Unsupported coref-critical questions")
            add("")
            add("| q_id | gold | question | original gold chunk | coref gold chunk |")
            add("| --- | --- | --- | --- | --- |")
            for u in r["unsupported"]:
                gold = ", ".join(str(g) for g in u["gold_chunk_ids"])
                add(
                    f"| q{u['q_id']} | {gold} | {md_escape(u['question'])} | "
                    f"{md_escape(u['original_gold_text'])} | {md_escape(u['coref_gold_text'])} |"
                )
            add("")
        else:
            add("No unsupported coref-critical questions: every flagged question's rewrite adds at")
            add("least one new content word to the gold chunk.")
            add("")

        if r["injection_questions"]:
            add("#### Coref-critical questions where the rewrite injected a query term")
            add("")
            add("| q_id | gold | question | injected tokens | original gold chunk | coref gold chunk |")
            add("| --- | --- | --- | --- | --- | --- |")
            for i in r["injection_questions"]:
                gold = ", ".join(str(g) for g in i["gold_chunk_ids"])
                add(
                    f"| q{i['q_id']} | {gold} | {md_escape(i['question'])} | "
                    f"`{', '.join(i['injected_tokens'])}` | "
                    f"{md_escape(i['original_gold_text'])} | {md_escape(i['coref_gold_text'])} |"
                )
            add("")
        else:
            add("No coref-critical question's rewrite injected a token that appears in its query.")
            add("")

        add("---")
        add("")

    add("## Caveats on this audit itself")
    add("")
    add("- The stopword list and the length-2 cutoff are heuristics. The test-4 q15 / q16 cases show")
    add("  the cutoff is not neutral: it decides whether a short entity string counts as added")
    add("  information. Both tokenisations are reported for that reason.")
    add("- `added` is a set difference over the union of a question's gold chunks, so for a")
    add("  multi-gold question a term added to one chunk can be masked by its presence in another.")
    add("  The `per_chunk` column in the sensitivity table shows the effect; it changes only test-4")
    add("  (q2, q3, q13), all three of which have two gold chunks.")
    add("- Injection is measured as token overlap, not as evidence of intent. A rewrite that resolves")
    add("  a pronoun to the entity a natural question would also name will register as injection; the")
    add("  point is that on those questions the recall gain cannot be separated from the term match.")
    add("- `critical_unsupported` does not mean the question is bad, only that coref cannot explain")
    add("  any retrieval change on it. The rewrite may still have altered the embedding.")
    add("- No retrieval metric in this repo has been recomputed. See the scope limit above.")

    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-flags",
        action="store_true",
        help="annotate eval_questions.json with critical_confirmed (originals preserved)",
    )
    args = parser.parse_args()

    results = [analyse_test(t) for t in TESTS]

    touched = write_flags(results) if args.write_flags else []

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "relabel_report.md").write_text(
        build_report(results, flags_written=args.write_flags), encoding="utf-8"
    )
    with (OUT_DIR / "relabel_report.json").open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"{'test':8} {'flagged':>8} {'confirmed':>10} {'unsupported':>12} {'injection':>10}   (strict: unsup/inj)")
    for r in results:
        s = r["counts_by_tokeniser"]["strict"]
        print(
            f"{r['test']:8} {r['n_flagged_critical']:>8} {r['n_critical_confirmed']:>10} "
            f"{r['n_critical_unsupported']:>12} {r['n_injection']:>10}   "
            f"({s['unsupported']}/{s['injection']})"
        )
    print()
    print("wrote analysis/relabel_report.md and analysis/relabel_report.json")
    for path in touched:
        print(f"annotated {path}")


if __name__ == "__main__":
    main()
