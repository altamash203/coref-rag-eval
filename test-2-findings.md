# Test 2 — Public-Benchmark Coref RAG Eval (BGE-M3 local)

**Notebook:** `coref_public_eval.ipynb`
**Question:** On standard informative-text retrieval, does *coref-before-embed* and *hybrid
sparse+dense* beat a conventional dense baseline?

> This file is a template. The notebook's final cell (`write_findings()`) **overwrites** it with
> the actual result tables, Δ-vs-baseline, flip counts, and a worked example after a run on Kaggle
> GPU. The sections below describe what gets filled in.

---

## Setup

| Component | Choice |
|-----------|--------|
| Embedding model | `BAAI/bge-m3` via FlagEmbedding, local Kaggle GPU, `use_fp16=True` |
| Representations | Dense + **learned-sparse** (BGE-M3 `lexical_weights`) — sparse is *not* BM25 |
| Coref engine | `fastcoref` LingMess (transformers<5 patch, eager attention) — reused from Test 1 |
| Coref scope | Document-level where `doc_id` available (DAPR); passage-level otherwise (BEIR) |
| Metrics | Recall@5, nDCG@10, MRR via `pytrec_eval` |
| Gold | Official qrels only (`score > 0`), passage IDs identical across variants (1:1 asserted) |
| Fusion | RRF, `RRF_K=60` |
| Fallback | If BGE-M3 OOMs: `bge-small-en-v1.5` dense + `rank_bm25` sparse (path logged) |

**Three ingestion variants**

| Label | Retrieval |
|-------|-----------|
| `baseline` | Dense on original passage text |
| `coref_dense` | Dense on LingMess coref rewrite (same `_id`) |
| `coref_hybrid` | RRF fuse: BGE-M3 sparse(original) + dense(coref) |

**Invariant:** text returned to the user is always the **original** passage, never the coref rewrite.

## Datasets

| Priority | Dataset | Source | Notes |
|----------|---------|--------|-------|
| Smoke | BEIR nfcorpus | `BeIR/nfcorpus` | Consumer-health, ~3.6k passages, ~300 test Qs, full index |
| Main 1 | DAPR ConditionalQA | `UKPLab/dapr` | 271 Qs / 69,199 passages, document-context, full index |
| Main 2 (optional) | DAPR nq-hard | `UKPLab/dapr` | 516 hard NQ queries, inline gold passages |
| Standard (optional) | BEIR hotpotqa | `BeIR/hotpotqa` | Subsampled to gold + candidate pool (`HOTPOTQA_MAX_CORPUS`) |

Skipped (too scientific): scifact, bioasq, trec-covid.

---

## Results — per dataset

_Populated by the notebook. One table per dataset:_

| variant | recall@5 | nDCG@10 | MRR | Δrecall@5 | ΔnDCG@10 |
|---------|----------|---------|-----|-----------|----------|
| baseline | — | — | — | — | — |
| coref_dense | — | — | — | — | — |
| coref_hybrid | — | — | — | — | — |

**Flips vs baseline** (recovered / hurt / both-fail) per coref variant — populated by the notebook.

## Worked example

_Populated by the notebook:_ a query where a coref variant recovered a baseline miss, showing the
gold passage's original text (returned to user) vs its coref rewrite (embedded), with pronoun
counts. This is the DAPR "the venue" → "the Half Moon, Putney" document-context pattern.

---

## Scope notes

- **DAPR** = document-context / informative Wikipedia-style retrieval.
- **BEIR** = standard comparability (nfcorpus smoke; hotpotqa subsampled — documented in run logs).
- **Hybrid** = BGE-M3 sparse(original) + dense(coref) via RRF, **not** BM25 (unless the OOM
  fallback path was used, which the report records).
- Relative comparison across variants matters more than absolute SOTA numbers.
- No LLM-as-judge, no answer generation, no custom q-gen, no re-chunking of public corpora.
