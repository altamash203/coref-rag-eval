# Coreference-Aware RAG Benchmark

**Does resolving coreference (pronouns → entity names) before embedding improve retrieval?**

- **Coref:** replacing pronouns (*he*, *it*, *they*) with the entity they refer to (*Armstrong*, *Apollo 11*, *the Allies*) before indexing.
- **The problem:** a dense retriever matches on what's in the chunk — if the chunk says *"he resigned"* but the query says *"Armstrong"*, there is no shared entity string to match on.
- **Small chunks lose context:** at sentence level, the antecedent (*"Armstrong joined NASA in 1962"*) lives in a different chunk, so *"He resigned in 1971"* has no entity name left in it.

## Abstract

We evaluate whether resolving coreference — rewriting pronouns to their antecedent entity names
before dense embedding — improves passage retrieval in RAG. Across five experiments we compare a
dense baseline against coref-augmented indexing using automated coreference (`fastcoref` LingMess)
and manual LLM-quality resolution, on paragraph- and sentence-level chunks from Wikipedia excerpts
and public DAPR benchmarks.

**Smaller chunks lose context.** Sentence-level chunking produces pronoun-only passages with no
entity string for the retriever to match. On coref-critical questions, baseline Recall@5 was 0.77
(100 chunks, Test 4) and 0.91 (414 chunks, Test 5) — well below paragraph-benchmark baselines
where the entity is usually named in the same chunk (Tests 2–3).

**LLM coref outperformed the neural coref model** on sentence-level evals: +17pp Recall@5 with
zero regressions (Test 4) vs +5pp with 1 regression for LingMess (Test 1) and flat results on
DAPR despite 77–89% pronoun reduction (Tests 2–3). LingMess rewrites often pointed to common
nouns or duplicated text already in the passage, adding no retrieval signal.

**Improvement is conditional, not universal.** At 414 sentence chunks (Test 5), dense-only coref
stayed flat (0.93 → 0.93), but coref + hybrid fusion recovered hard pronoun queries (+10pp on
critical Recall@5, 2 recovered / 1 hurt). Test 4's larger dense gain (+17pp) did not fully
replicate at scale — baseline headroom and corpus size matter.

**Bottom line:** Coref-before-embed is a valid technique for pronoun-only sentence chunks when
resolution quality is high, but it is not a default ingestion step for paragraph-level RAG with a
modern dense model.

---

## What's in this repo

| Path | What it does |
|------|--------------|
| `test-1/coref_rag_benchmark.ipynb` | **Test 1** — stress test on one Wikipedia article (20 pronoun-targeted questions). Automated coref helps (+5pp recall). |
| `test-2/coref_public_eval.ipynb` | **Test 2** — public benchmark (DAPR ConditionalQA). Automated coref is flat. |
| `test-3/coref_public_eval_v3.ipynb` | **Test 3** — entity-rich Wikipedia (DAPR NaturalQuestions) + selective coref. Still flat. |
| `test-4/coref_public_eval_v4.ipynb` | **Test 4** — manual (LLM) coref on sentence-level Apollo 11 chunks. Clear win (+17pp recall). |
| `test-5/coref_public_eval_v5.ipynb` | **Test 5** — manual coref on sentence-level WW2 chunks (414 chunks). Dense flat; hybrid +3pp overall, +10pp on critical. |
| `coref-rag-hypothesis-and-findings.md` | Full research write-up: hypothesis, all five tests, synthesis |
| `test-*/test-*-findings.md` | Per-test detailed results |

---

## Quick start (Kaggle GPU)

1. Upload the notebook you want to run to a Kaggle notebook (GPU T4 accelerator).
2. Run the **install cell**, then **restart the kernel** (one-time, needed for `transformers<5` on Tests 1–3).
3. Run all remaining cells top-to-bottom. Results appear inline + a findings `.md` is written.

**Tests 4–5:** Run `test-4/coref_public_eval_v4.ipynb` or `test-5/coref_public_eval_v5.ipynb` locally or on Kaggle. Data is bundled in `test-4-data/` and `test-5-data/` — no API keys needed.

---

## The five tests at a glance

| Test | Corpus | Coref | Chunks | Baseline R@5 | Best variant | Δ R@5 | Verdict |
|------|--------|-------|--------|--------------|--------------|-------|---------|
| 1 | 1 Wikipedia article, custom questions | LingMess (auto) | 117 para | 0.50 | coref_dense | **+0.05** | ✅ Helps |
| 2 | DAPR ConditionalQA (gov guidance) | LingMess (auto) | 8,093 para | 0.29 | baseline | 0.00 | ❌ Flat |
| 3 | DAPR NaturalQuestions (Wikipedia) | Selective auto | 8,000 para | 0.80 | baseline | −0.01 | ❌ Flat |
| 4 | Apollo 11 Wikipedia, sentence chunks | Manual (LLM) | 100 sent | 0.82 | coref_dense | **+0.17** | ✅ Win (N=30; did not replicate in Test 5) |
| 5 | WW2 Wikipedia (~10k words), sentence chunks | Manual (LLM) | 414 sent | 0.93 | coref_hybrid | **+0.03** (crit **+0.10**) | ⚠️ Dense flat; hybrid improved critical queries |

**Pattern:** Smaller chunks expose pronoun-only gold passages that hurt retrieval. LLM coref
recovers that gap when baseline headroom exists (Test 4). LingMess on paragraph corpora does not
move metrics (Tests 2–3). At larger scale with a strong baseline, even LLM coref stops helping
dense retrieval (Test 5).

---

## Three honest takeaways

### 1. Smaller chunks hurt retrieval (when pronouns replace entity names)

Sentence-level chunking strips away surrounding context. A chunk like *"He resigned from NASA
in 1971"* has no entity string for dense matching — the query names "Armstrong" but the index
does not.

Measured impact on **coref-critical** questions (gold chunk uses pronouns, query names entity):

| Test | Chunk size | Baseline R@5 (critical) | Notes |
|------|------------|-------------------------|-------|
| 2–3 | Paragraph | N/A (entity usually named in same chunk) | Baseline already ~0.29–0.80 overall |
| 4 | Sentence (100 chunks) | **0.773** | ~23% of critical queries missed without coref |
| 5 | Sentence (414 chunks) | **0.905** | Smaller chunks still lose context, but dense retrieval finds most gold anyway at this corpus size |

Smaller chunks do hurt — but the **magnitude depends on corpus size and query overlap**. On
100 chunks the damage is clear; on 414 chunks the same embedding model already retrieves 90%+
of pronoun-only gold passages without any coref rewrite.

### 2. LLM-based coref worked better than the LingMess coref model

We did not run LingMess and LLM coref on identical sentence-level data, so this is a
cross-test comparison, not a controlled A/B. Still, the pattern is consistent:

| | LingMess (Tests 1–3) | Manual LLM (Tests 4–5) |
|--|---------------------|------------------------|
| **Best Δ Recall@5** | +0.05 (Test 1 only) | +0.167 (Test 4) |
| **Public benchmarks** | Flat (Tests 2–3), despite 77–89% pronoun reduction | — |
| **Regressions** | 1 hurt (Test 1); 4 hurt / 4 recovered (Test 2) | 0 hurt (Test 4); 0 hurt (Test 5 dense) |
| **Quality issues** | Grammar artifacts (*"Marcel Mauss's writes"*), occasional bad rewrites | Clean entity injection; no regressions in Test 4 |

On the evals designed to stress pronoun-only chunks, LLM coref improved metrics where LingMess
either barely moved the needle (Test 1: +5pp on 20 questions) or did not help at all on
paragraph corpora (Tests 2–3). Test 5 shows LLM quality alone is not enough when baseline
recall is already high — the improvement is real but conditional.

### 3. Do not overstate the win

- Test 4 (+17pp) is a **small micro-benchmark**: 100 chunks, 30 questions, 22 coref-critical,
  one document. ±1 query moves Recall@5 by ~3pp.
- Test 5 **did not replicate** Test 4's dense-only gain (0.93 → 0.93), but **did show improvement**
  via coref_hybrid: critical recall 0.905 → 1.00 (2 Japan pronoun queries recovered), with 1 regression.
- Hybrid fusion is mixed: it helped on hard pronoun queries in Test 5 but hurt one easy query; worse
  than pure coref_dense in Test 4.
- Paragraph-level RAG with a modern dense model does not need coref-before-embed as a default step.

---

## How it works

```
Original passage:  "He won the Nobel Prize in 1921."
                        ↓ coreference resolution (LingMess or manual LLM)
Coref rewrite:     "Albert Einstein won the Nobel Prize in 1921."
                        ↓ embed the rewrite (but return the original to the user)
Dense vector:      now captures "Albert Einstein" for query matching
```

**Three retrieval variants compared (Tests 2–5):**
- `baseline` — embed the original text as-is
- `coref_dense` — embed the coref-rewritten text
- `coref_hybrid` — fuse BM25(original) + dense(coref) via reciprocal rank fusion

---

## Key insight

Two separate problems, two separate answers:

**Problem A — smaller chunks lose entity context.** Sentence-level chunking creates
pronoun-only passages that paragraph chunking usually avoids (the entity is named elsewhere
in the same paragraph). Tests 4–5 measured this directly: without coref, critical-question
recall was 0.77–0.91 depending on corpus size.

**Problem B — LingMess could not reliably fix it at scale.** On paragraph benchmarks (Tests 2–3),
LingMess reduced pronouns by 77–89% but retrieval stayed flat — wrong antecedent types (common
nouns), redundant rewrites, or entity already present in the chunk. On a pronoun-targeted stress
test (Test 1), LingMess helped modestly (+5pp) but introduced 1 regression and grammar artifacts.

**LLM coref did better on the sentence-level evals** (Test 4: +17pp dense, 0 regressions; Test 5:
+10pp on critical questions via hybrid, 2 recovered / 1 hurt). Dense-only coref did not move Test 5
metrics — improvement there required combining coref embeddings with BM25.

**Practical guidance (conservative):**
- If you chunk at sentence level, expect pronoun-only chunks to hurt retrieval — measure baseline
  R@5 on coref-critical queries before adding coref.
- Prefer LLM-based coref over LingMess for entity injection; do not expect LingMess to move
  metrics on paragraph corpora.
- Do not assume coref fixes small-chunk retrieval automatically — validate on your corpus size
  and baseline, as Test 5 showed.

---

## Tech stack

| Component | Choice |
|-----------|--------|
| Embedding | `BAAI/bge-small-en-v1.5` (Tests 2–5) / `Qwen3-Embedding-8B` (Test 1) |
| Coreference | `fastcoref` LingMessCoref (Tests 1–3, local GPU) / manual LLM (Tests 4–5) |
| Lexical | `rank_bm25` (BM25 Okapi) |
| Metrics | `pytrec_eval` (Recall@5, nDCG@10, MRR) |
| Datasets | DAPR (`UKPLab/dapr`), BEIR, custom Wikipedia excerpts |
| Runtime | Kaggle free T4 GPU, no paid APIs (Tests 2–5) |

---

## Repo structure

```
corefernce/
├── README.md                              ← you are here
├── coref-rag-hypothesis-and-findings.md   ← full research write-up
├── test-1/
│   ├── coref_rag_benchmark.ipynb          ← Test 1 notebook
│   └── test-1-findings.md
├── test-2/
│   ├── coref_public_eval.ipynb            ← Test 2 notebook
│   └── test-2-findings.md
├── test-3/
│   ├── coref_public_eval_v3.ipynb         ← Test 3 notebook
│   └── test-3-findings.md
├── test-4/
│   ├── coref_public_eval_v4.ipynb         ← Test 4 notebook
│   ├── test-4-data/                       ← Apollo 11 chunks + eval questions
│   └── test-4-findings.md
└── test-5/
    ├── coref_public_eval_v5.ipynb         ← Test 5 notebook
    ├── test-5-data/                       ← WW2 chunks + eval questions
    └── test-5-findings.md
```

---

## License & citation

This is a research proof-of-concept. The datasets used (DAPR, BEIR) have their own licenses
(see their respective HuggingFace pages). The code in this repo is free to use and adapt.

If referencing this work:
> Coreference-aware RAG ingestion: a five-test evaluation showing that sentence-level chunking
> hurts retrieval on pronoun-only passages, LLM-based coref outperforms LingMess on targeted evals
> (+17pp vs +5pp/flat), but neither approach reliably improves dense retrieval once baseline
> recall is already high or chunks are paragraph-sized.
