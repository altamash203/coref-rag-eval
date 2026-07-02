# Test 3 — Selective Coref + Entity-Rich Retrieval (DAPR NaturalQuestions)

**Run date:** 2026-07-02
**Notebook:** `coref_public_eval_v3.ipynb`
**Hypothesis:** coref-before-embed helps retrieval only when it injects a named entity a query
searches for (not a common noun).

**Headline:** The hypothesis is **not confirmed**. Even with selective (proper-noun-only) coref on an
entity-rich Wikipedia corpus, coref_dense is **flat-to-slightly-worse** than baseline (−0.014
Recall@5, +0.01 nDCG@10, +0.012 MRR). The hybrid is worse (−0.078 Recall@5). Coref *ran correctly*
(77% pronoun reduction, 4237/8000 passages changed), but the dense baseline is already strong enough
on NQ Wikipedia passages that coref rewrites add no net retrieval signal.

---

## What changed vs Test 2

- **Selective coref:** rewrite a pronoun only when its antecedent is a proper noun (named entity);
  common-noun antecedents are left untouched.
- **Entity-rich dataset:** DAPR NaturalQuestions (Wikipedia), instead of gov-guidance ConditionalQA.
- **Weighted RRF hybrid:** 0.7 * dense(coref) + 0.3 * BM25(original) (aimed to fix Test 2's
  equal-weight hybrid regression).

## Setup

- **Embedding model:** BAAI/bge-small-en-v1.5 (dense, local GPU) + rank_bm25 (lexical)
- **Coref:** fastcoref LingMess, document-level, SELECTIVE_COREF=True, batched (512 windows/chunk)
- **Metrics:** Recall@5, nDCG@10, MRR (pytrec_eval); TOP_K=5, RRF_K=60
- **Subsampling (free-T4 POC):** first 200 test queries; document-aware corpus cap ≤ 8000 passages.

---

## Results — DAPR NaturalQuestions

Passages: 8000 | Queries: 200
Passages changed by selective coref: **4237/8000 (53%)** | pronouns 25,897 → 5,861 (**77% reduction**)

| variant | recall@5 | nDCG@10 | MRR | Δrecall@5 | ΔnDCG@10 |
|---------|----------|---------|-----|-----------|----------|
| baseline | 0.7967 | 0.6745 | 0.6241 | — | — |
| coref_dense | 0.7825 | 0.6845 | 0.6360 | −0.0142 | +0.0099 |
| coref_hybrid | 0.7192 | 0.6456 | 0.6021 | −0.0775 | −0.0289 |

---

## Interpretation

### 1. coref_dense: mixed signal, net flat

- **Recall@5 dropped** slightly (−0.014, ~3 queries lost from top-5).
- **nDCG@10 and MRR improved** slightly (+0.01, +0.012) — coref sometimes sharpens rank positions.
- Net: this is **noise/wash** rather than a real gain. On 200 queries, a ±0.014 swing is within
  random variance (1–3 queries flipping changes the number).

### 2. coref_hybrid: still worse (−0.078 Recall@5)

Even at 0.7/0.3 dense-favoring weight, the hybrid hurts. BM25 is *particularly weak on NQ* — its
queries are short factoid questions that need semantic matching, not keyword overlap. Even a
30% BM25 weight drags down the strong dense signal. (Contrast with e.g. keyword-heavy web queries
where BM25 shines.)

### 3. Why coref didn't help even on entity-rich Wikipedia

This is the important question. Two reasons emerge:

**a) The baseline is already very strong (R@5 = 0.80).**
bge-small on Wikipedia passages already captures entity-passage semantic matching well. There's
little headroom for coref to exploit — the baseline already gets 80% of queries right in the top 5.
Coref is trying to improve on a high bar where most improvements are marginal.

**b) NQ gold passages often already name the entity.**
Unlike the DAPR ConditionalQA "the venue" pattern (where the gold passage *only* uses a reference
noun), NQ gold passages frequently **already mention the entity by name** somewhere in the passage —
so the dense model already has the entity signal even without coref. The pronoun-only case (entity
named nowhere in the passage) is rarer than we assumed.

### 4. When coref *does* help (Test 1, revisited)

Test 1's +5pp Recall@5 gain worked because:
- The baseline was weaker (~0.50 recall) → more headroom.
- The gold chunk genuinely contained *only* pronouns for the entity.
- The queries were explicitly designed to name the entity (Q-gen targeted this).

That's a narrow, constructed scenario. On real public benchmarks with a reasonable baseline model,
the pronoun-only pattern is too rare to move aggregate metrics.

---

## What the three tests together show

| Test | Corpus | Coref | Baseline R@5 | Δ coref_dense |
|------|--------|-------|-------------|---------------|
| 1 | 1 Wikipedia article, q-gen (pronoun-targeted) | Full | 0.50 | **+0.05** |
| 2 | DAPR ConditionalQA (gov guidance, common-noun coref) | Full | 0.29 | −0.002 (flat) |
| 3 | DAPR NaturalQuestions (Wikipedia, entity-rich) | Selective | 0.80 | −0.014 (flat) |

**Pattern:** coref-before-embed helps in the **low-baseline, pronoun-only, targeted-query** scenario
(Test 1), but is **flat on real public benchmarks** regardless of whether the corpus is entity-rich
(Test 3) or not (Test 2). The effect is real but too rare in practice to move aggregate retrieval.

---

## Honest conclusion

Coreference resolution before embedding is a **valid technique with a real mechanism** (entity
injection into the embedded text), but it produces **no measurable retrieval gain on public
benchmarks with a competent dense model**. The cases where it helps — pronoun-only gold passages
with entity queries and a weak baseline — are too rare in standard informative-text corpora to move
aggregate metrics.

**Practical recommendation:** coref-before-embed is not worth the complexity/runtime for general
informative retrieval. It may have value in specific domains where:
- The passage genuinely never names the entity (e.g. legal transcripts, interview transcripts).
- The baseline dense model is weak (e.g. out-of-domain or very short passages).
- Combined with other document-context techniques (title prepending, section headers) that similarly
  inject missing context.

---

## Scope notes

- DAPR NaturalQuestions subsampled for a free-T4 POC (first 200 queries, document-aware corpus cap
  ≤ 8,000 passages, whole gold-containing documents first, 202 docs). A subset, not the full corpus.
- Original text always returned to the user; official qrels only (`score > 0`); 1:1 coref alignment
  asserted.
- The hybrid regression is a **BM25/fusion** problem (weak on short factoid NQ queries), not a coref
  problem. A learned re-ranker or adaptive-weight fusion would likely resolve it, but that's outside
  the scope of this coref-focused test.
- Relative comparison across variants matters more than absolute SOTA numbers.
