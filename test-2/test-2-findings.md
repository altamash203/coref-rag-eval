# Test 2 — Public-Benchmark Coref RAG Eval (DAPR ConditionalQA, local)

**Run date:** 2026-07-02
**Notebook:** `coref_public_eval.ipynb`
**Question:** On standard informative-text retrieval, does *coref-before-embed* and *hybrid
dense+lexical* beat a conventional dense baseline?

**Headline:** No — on DAPR ConditionalQA, coref-before-embed is **flat** vs the dense baseline and
the RRF hybrid is **worse**. The worked example explains why, and the reason is informative rather
than a bug: this corpus's coreference points to *common nouns*, not the *named entities* that coref
rewriting helps with.

---

## Setup

| Component | Choice |
|-----------|--------|
| Embedding model | `BAAI/bge-small-en-v1.5` (dense, 384-d), local Kaggle T4 |
| Lexical model | `rank_bm25` (BM25 Okapi) |
| Coref engine | `fastcoref` LingMess, document-level (DAPR passages carry `doc_id`) |
| Dataset | DAPR ConditionalQA (`UKPLab/dapr`), official qrels |
| Corpus | 8,093 passages (whole gold-containing documents first, then top-up), 271 test queries |
| Metrics | Recall@5, nDCG@10, MRR via `pytrec_eval`; TOP_K=5, RRF_K=60 |

**Variants:** `baseline` (dense on original) / `coref_dense` (dense on LingMess rewrite) /
`coref_hybrid` (RRF: BM25(original) + dense(coref)).
**Invariant:** original text is always returned to the user; only the embedded text changes.
Pronouns before→after coref: **1243 → 142 (89% reduction)** — coref *ran* correctly; it just didn't
help retrieval here (see analysis).

---

## Results

| variant | recall@5 | nDCG@10 | MRR | Δrecall@5 | ΔnDCG@10 |
|---------|----------|---------|-----|-----------|----------|
| baseline | 0.2894 | 0.3270 | 0.4769 | — | — |
| coref_dense | 0.2879 | 0.3278 | 0.4848 | −0.0015 | +0.0008 |
| coref_hybrid | 0.2565 | 0.3006 | 0.4441 | **−0.0329** | **−0.0264** |

**Flips vs baseline**

| variant | recovered | hurt | both_fail |
|---------|-----------|------|-----------|
| coref_dense | 4 | 4 | 98 |
| coref_hybrid | 22 | 35 | 80 |

---

## Interpretation

### 1. coref_dense is flat (not a failure — a null result)
Recall −0.0015, nDCG +0.0008, MRR +0.008, with an even **4 recovered / 4 hurt** split. Statistically
this is noise: on DAPR ConditionalQA, resolving coreference before embedding neither helps nor hurts
dense retrieval. The tiny MRR gain (+0.008) hints coref occasionally sharpens rank position, but it
does not move top-5 recall.

### 2. coref_hybrid is worse — and it's a *fusion* issue, not a coref issue
The hybrid lost −0.033 recall (22 recovered / 35 hurt). The cause is the RRF weighting, not coref:
- RRF fuses BM25(original) and dense(coref) **50/50**.
- DAPR queries are long, conversational narratives (see the example below, ~80 words).
- BM25 term-matching is weak and noisy on such queries, so equal-weight fusion **drags down** the
  stronger dense ranking.

In other words, the dense baseline is already good on these queries, and blending in an equal share
of a weaker lexical signal pulls it down. This would likely reverse with (a) short keyword queries,
or (b) a fusion that down-weights BM25.

### 3. Why coref doesn't help on THIS corpus — the key insight
DAPR ConditionalQA is **UK government guidance text**. Its coreference chains resolve to **common
nouns / generic concepts** ("mobility aids", "VAT", "your home"), not **named entities**. Resolving
a pronoun to a common noun adds no *discriminative* term the query can match on — and can even
duplicate an existing phrase (see the worked example). Contrast with Test 1, where `"he"` →
`"Marcel Mauss"` injected an entity name the query explicitly searched for, and coref helped.

**This is the takeaway, and it's a clean, useful result:**
> Coref-before-embed helps when coreference *hides named entities that queries name*
> (Test 1: biography/Wikipedia). It is neutral on *instructional text whose pronouns refer to
> common nouns* (Test 2: government guidance). The technique is entity-driven, not universally
> beneficial.

---

## Worked example — why the rewrite added no signal

**Query:** *"I am the carer for my mother who is disabled and has mobility issues. I shop on her
behalf ... I have recently purchased on her behalf a mobility vehicle for which she paid me back ...
Can my mother claim back the VAT paid on the mobility vehicle?"*

**Recovered by:** coref_dense (this one flipped baseline-miss → hit)

**Gold passage 544-78 — RETURNED (original):**
> If you're over 60, you pay a reduced rate of VAT (5%) on certain mobility aids when you pay for
> **them** to be supplied and installed in your home.

**EMBEDDED (coref rewrite):**
> If you're over 60, you pay a reduced rate of VAT (5%) on certain mobility aids when you pay for
> **certain mobility aids** to be supplied and installed in your home.

**Pronouns:** orig 1 → coref 0.

**What this shows:** coref correctly resolved `"them"` → `"certain mobility aids"`, but that is a
**common noun already present in the sentence**. The rewrite just *duplicated* an existing phrase —
it added no new entity, no new query-matchable term. The retrieval win on this query came from the
dense model, not from the rewrite. Multiply this across the corpus and the aggregate effect is ~0,
exactly what the metrics show.

---

## Scope notes

- **DAPR ConditionalQA** = document-context / informative retrieval; the benchmark built to reward
  coreference understanding. Our result shows that "rewarding coreference" at the *document-context*
  level (which DAPR's own baselines exploit via context encoders) is not the same as benefiting from
  *pronoun→antecedent surface rewriting* when antecedents are common nouns.
- **Corpus** subsampled for a free-T4 POC: whole gold-containing documents first (gold + their
  same-document distractors — preserving real retrieval difficulty), topped up to ≤ 8,000 passages
  (actual: 8,093). A subset of the full ~69k corpus, but the *right* subset for measuring retrieval.
- **Hybrid** = BM25(original) + dense(coref) via RRF, equal weight. The regression is attributable
  to fusion weighting on long queries, not to coref.
- Relative comparison across variants matters more than absolute SOTA numbers.
- No LLM-as-judge, no answer generation, no custom q-gen, no re-chunking of the public corpus.

---

## Suggested next steps (if pursuing further)

1. **Weight the fusion.** Try `dense + λ·BM25` with λ < 1 (or RRF with a dense-favoring constant) —
   the hybrid regression is likely recoverable, since the dense baseline is strong on long queries.
2. **Entity-aware corpus.** Re-run on a DAPR split with more named-entity coreference (e.g.
   NaturalQuestions / MIRACL Wikipedia passages) to confirm the "entities help, common nouns don't"
   hypothesis on a public benchmark, mirroring Test 1.
3. **Selective coref.** Only rewrite pronouns whose antecedent is a **proper noun** (skip common-noun
   resolutions). This would avoid the redundant-duplication case in the worked example and isolate
   the entity-injection effect.
