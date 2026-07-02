# Coreference-Aware RAG Benchmark

**Does resolving coreference (pronouns → entity names) before embedding improve retrieval?**

This repo tests a simple idea: if a passage says *"he won the Nobel Prize"* instead of
*"Marie Curie won the Nobel Prize,"* a dense retriever might miss it when you search for
"Marie Curie." So we rewrite pronouns to entity names before embedding — and measure whether
retrieval actually gets better.

**TL;DR:** The mechanism works in theory, but on real public benchmarks with a competent dense
model it makes no measurable difference. Standard passages already name their entities, and
standard models already capture them.

---

## What's in this repo

| File | What it does |
|------|--------------|
| `coref_rag_benchmark.ipynb` | **Test 1** — stress test on one Wikipedia article (20 pronoun-targeted questions). Shows coref *can* help (+5pp recall). |
| `coref_public_eval.ipynb` | **Test 2** — public benchmark (DAPR ConditionalQA). Coref is flat. |
| `coref_public_eval_v3.ipynb` | **Test 3** — entity-rich Wikipedia (DAPR NaturalQuestions) + selective coref. Still flat. |
| `coref-rag-hypothesis-and-findings.md` | Full research write-up: hypothesis, all results, analysis |
| `test-1-findings.md` | Test 1 detailed results |
| `test-2-findings.md` | Test 2 detailed results |
| `test-3-findings.md` | Test 3 detailed results |

---

## Quick start (Kaggle GPU)

1. Upload the notebook you want to run to a Kaggle notebook (GPU T4 accelerator).
2. Run the **install cell**, then **restart the kernel** (one-time, needed for `transformers<5`).
3. Run all remaining cells top-to-bottom. Results appear inline + a findings `.md` is written.

**No API keys needed.** Everything runs locally (embedding model, coref model, BM25).

---

## The three tests at a glance

| Test | Corpus | Coref | Baseline Recall@5 | Coref Recall@5 | Verdict |
|------|--------|-------|-------------------|----------------|---------|
| 1 | 1 Wikipedia article, custom questions | Full | 0.50 | **0.55** | ✅ Helps |
| 2 | DAPR ConditionalQA (gov guidance) | Full | 0.29 | 0.29 | ❌ No change |
| 3 | DAPR NaturalQuestions (Wikipedia) | Selective | 0.80 | 0.78 | ❌ No change |

**Pattern:** coref helps in the narrow, constructed case (passage hides the entity behind a
pronoun, query names the entity, baseline is weak). On real benchmarks it's flat.

---

## How it works

```
Original passage:  "He won the Nobel Prize in 1921."
                        ↓ LingMess coreference resolution
Coref rewrite:     "Albert Einstein won the Nobel Prize in 1921."
                        ↓ embed the rewrite (but return the original to the user)
Dense vector:      now captures "Albert Einstein" for query matching
```

**Three retrieval variants compared:**
- `baseline` — embed the original text as-is
- `coref_dense` — embed the coref-rewritten text
- `coref_hybrid` — fuse BM25(original) + dense(coref) via reciprocal rank fusion

---

## Key insight

The reason coref doesn't help on public benchmarks isn't that the technique is broken — it's
that the scenario it targets is **rare in standard text**:

- Wikipedia passages usually **already name the entity** somewhere (not only pronouns).
- A competent dense model captures entity semantics from those explicit mentions.
- So coref adds redundant information the model already has.

**Where it *would* help:** transcripts, interview text, legal documents — anywhere entities
are named once and then referred to only by pronouns for many paragraphs.

---

## Tech stack

| Component | Choice |
|-----------|--------|
| Embedding | `BAAI/bge-small-en-v1.5` (Tests 2–3) / `Qwen3-Embedding-8B` (Test 1) |
| Coreference | `fastcoref` LingMessCoref (local, GPU) |
| Lexical | `rank_bm25` (BM25 Okapi) |
| Metrics | `pytrec_eval` (Recall@5, nDCG@10, MRR) |
| Datasets | DAPR (`UKPLab/dapr`), BEIR |
| Runtime | Kaggle free T4 GPU, no paid APIs (Tests 2–3) |

---

## Repo structure

```
corefernce/
├── README.md                          ← you are here
├── coref-rag-hypothesis-and-findings.md  ← full research write-up
├── coref_rag_benchmark.ipynb          ← Test 1 notebook
├── coref_public_eval.ipynb            ← Test 2 notebook
├── coref_public_eval_v3.ipynb         ← Test 3 notebook
├── test-1-findings.md                 ← Test 1 results
├── test-2-findings.md                 ← Test 2 results
├── test-3-findings.md                 ← Test 3 results
└── embed_cache*/                      ← cached vectors (gitignored, created on run)
```

---

## License & citation

This is a research proof-of-concept. The datasets used (DAPR, BEIR) have their own licenses
(see their respective HuggingFace pages). The code in this repo is free to use and adapt.

If referencing this work:
> Coreference-aware RAG ingestion: a three-test evaluation showing that pronoun→entity
> rewriting before embedding is mechanistically valid but produces no net retrieval gain on
> standard informative-text benchmarks with a competent dense model.
