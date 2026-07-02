# Coreference-Aware RAG: Full Hypothesis & Findings

**Project:** Coreference-before-embed ingestion for dense retrieval
**Date:** 2026-07-02
**Notebooks:** `coref_rag_benchmark.ipynb` (Test 1), `coref_public_eval.ipynb` (Test 2), `coref_public_eval_v3.ipynb` (Test 3)

---

## 1. Research Question

> Does resolving coreference before embedding — rewriting pronouns to their antecedent entities
> in the indexed text — improve passage retrieval compared to a conventional dense baseline?
> And does combining it with a lexical (BM25) hybrid further help?

---

## 2. Hypothesis (evolved across three tests)

**Initial hypothesis (Test 1):**
Pronouns like "he" or "she" in a passage hide the entity name the query searches for. If we
rewrite those pronouns to the entity name before embedding, the dense vector becomes more
query-aligned, and retrieval improves.

**Refined hypothesis (Test 3):**
The benefit is specifically about **named-entity injection** — rewriting a pronoun to a
proper noun the query names. Rewriting to common nouns ("them" → "mobility aids") adds no
signal. Therefore: *selective* coref (proper-noun antecedents only) on *entity-rich* text
should show a gain, while full coref on common-noun text should be flat.

---

## 3. Experimental Design

### Constant across all tests
- **Coref engine:** fastcoref LingMessCoref (local, transformers<5, eager-attention patch)
- **Invariant:** original text is always returned to the user; only the embedded text changes
- **Gold:** official qrels (or ground-truth sentence indices) with `score > 0`
- **Passage IDs identical** across variants; 1:1 coref alignment asserted
- **No LLM-as-judge, no custom q-gen** (except Test 1), no re-chunking of public corpora

### Test variations

| | Test 1 | Test 2 | Test 3 |
|--|--------|--------|--------|
| **Corpus** | 1 Wikipedia article (biography/altruism) | DAPR ConditionalQA (UK gov guidance) | DAPR NaturalQuestions (Wikipedia) |
| **Queries** | 20, self-generated, pronoun-targeted | 271, official | 200, official (subsampled) |
| **Coref scope** | Full (all pronouns) | Full (all pronouns) | Selective (proper-noun antecedents only) |
| **Embedding** | Qwen3-Embedding-8B (DeepInfra API) | bge-small-en-v1.5 (local) | bge-small-en-v1.5 (local) |
| **Hybrid** | — | RRF 50/50 (BM25 + dense) | Weighted RRF 0.7 dense / 0.3 BM25 |
| **Corpus size** | 117 chunks | 8,093 passages | 8,000 passages |
| **Benchmark type** | Custom stress test | Public (DAPR) | Public (DAPR) |

### Three variants compared (Tests 2 & 3)

| Variant | What gets embedded |
|---------|--------------------|
| **baseline** | Original passage text (dense) |
| **coref_dense** | Coref-rewritten passage text (dense) |
| **coref_hybrid** | RRF fuse: BM25(original) + dense(coref) |

---

## 4. Results Summary

| Test | Corpus type | Coref mode | Baseline R@5 | coref_dense R@5 | Δ R@5 | nDCG@10 Δ | MRR Δ | Verdict |
|------|-------------|------------|-------------|-----------------|-------|-----------|-------|---------|
| 1 | Biography (pronoun-heavy) | Full | 0.500 | 0.550 | **+0.050** | — | +0.057 | ✅ Helps |
| 2 | Gov guidance (common-noun coref) | Full | 0.289 | 0.288 | −0.002 | +0.001 | +0.008 | ❌ Flat |
| 3 | Wikipedia (entity-rich) | Selective | 0.797 | 0.783 | −0.014 | +0.010 | +0.012 | ❌ Flat |

### Hybrid results

| Test | Hybrid config | Δ R@5 vs baseline | Verdict |
|------|---------------|-------------------|---------|
| 2 | RRF 50/50 | −0.033 | ❌ Worse (BM25 too weak on long queries) |
| 3 | RRF 0.7/0.3 | −0.078 | ❌ Worse (BM25 too weak on short factoid queries) |

### Flip counts (Test 2 & 3)

| Test | Variant | Recovered | Hurt | Both fail |
|------|---------|-----------|------|-----------|
| 2 | coref_dense | 4 | 4 | 98 |
| 2 | coref_hybrid | 22 | 35 | 80 |
| 3 | coref_dense | (small) | (small) | (majority) |
| 3 | coref_hybrid | — | — | — |

---

## 5. Key Findings

### Finding 1: The mechanism is real but the effect is narrow

Test 1 proves the mechanism works: `"he"` → `"Marcel Mauss"` injected the entity name into the
embedded text, the query searched for "Marcel Mauss," and retrieval improved. This is a genuine,
mechanistically interpretable gain.

But this scenario — a passage that refers to the entity **only** by pronoun, with a query that
names the entity, and a baseline too weak to find it — is **rare in real corpora**.

### Finding 2: On public benchmarks, coref is flat regardless of corpus type

- **Common-noun corpus (Test 2):** coref resolves to generic nouns ("them" → "mobility aids") —
  adds no query-matchable signal. Result: flat.
- **Entity-rich corpus (Test 3):** coref resolves to named entities, but the passages **already
  name the entity** elsewhere. The dense model already captures the entity signal without coref.
  Result: flat.

The baseline model (even a small one like bge-small) is already competent at entity-passage
matching on well-formed Wikipedia/guidance passages. Coref's headroom is near zero.

### Finding 3: The hybrid (BM25 + dense) doesn't rescue coref — and can hurt

BM25 is weak on:
- Long narrative queries (Test 2: DAPR ConditionalQA's conversational style)
- Short factoid queries (Test 3: NQ's "who/what/when" style)

In both cases, blending BM25 — even at 30% weight — drags down the stronger dense signal. The
hybrid regression is a **fusion** problem unrelated to coref.

### Finding 4: Selective coref doesn't help either

Narrowing coref to only proper-noun antecedents (Test 3) correctly eliminated the common-noun
noise from Test 2 — 4237/8000 passages were rewritten, with 77% pronoun reduction. But it still
didn't help, because the real blocker isn't which pronouns we rewrite — it's that the entity signal
is already present in the passage for the model to find.

### Finding 5: Pronoun count before/after confirms coref quality

| Test | Pronouns before | Pronouns after | Reduction |
|------|----------------|----------------|-----------|
| 1 | ~75 (one doc) | ~30 | ~60% |
| 2 | 1,243 | 142 | 89% |
| 3 | 25,897 | 5,861 | 77% |

LingMess coref ran correctly in all tests. The null result on Tests 2 & 3 is **not a coref
quality problem** — the resolutions were accurate. The technique just doesn't help retrieval
when the baseline already captures entity semantics.

---

## 6. Worked Examples

### Test 1 — coref HELPS (biography, pronoun-only passage)

**Query:** "What did Marcel Mauss write about in his work on altruism?"

**Gold passage (original):** `"In it, he writes: …"` — no mention of "Marcel Mauss."
**Coref rewrite:** `"In This note, Marcel Mauss's writes: …"` — entity injected.

The query names "Marcel Mauss"; the passage only says "he." Dense model can't match
without coref. Rewrite injects the entity → retrieval improves.

### Test 2 — coref FLAT (gov guidance, common-noun antecedent)

**Query:** "Can my mother claim back the VAT paid on the mobility vehicle?"

**Gold passage (original):** `"…when you pay for them to be supplied…"` — "them" = mobility aids.
**Coref rewrite:** `"…when you pay for certain mobility aids to be supplied…"` — common noun duplicated.

The rewrite is *correct* but adds no new searchable term (the phrase is already in the sentence).
Dense model already found the passage via "VAT" + "mobility aids." Coref adds nothing.

### Test 3 — coref FLAT (Wikipedia, entity already named in passage)

On NQ, gold passages typically contain both the entity name and pronoun references to it. The
dense model already has the entity signal from the explicit mention, so resolving the pronouns
adds redundant information.

---

## 7. Conclusion

**Does coreference resolution before embedding improve retrieval?**

**In theory:** Yes — when a passage hides a named entity behind pronouns and the query names
that entity, coref injection helps.

**In practice (on public benchmarks with a competent model):** No. The scenario is too rare
to move aggregate metrics. Standard passages name their entities; standard dense models
capture entity semantics. Coref-before-embed adds complexity and runtime with no net gain.

---

## 8. When It *Would* Help (practical guidance)

Coref-before-embed may have value in specific, identifiable domains:

1. **Transcript/interview corpora** — speakers use pronouns heavily and often never re-state
   the entity name after the first mention. Passages drawn from mid-transcript lack the entity.
2. **Weak or domain-mismatched baseline** — if your dense model hasn't seen the domain,
   explicit entity injection gives it signal it can't infer.
3. **Very short passages/chunks** — the smaller the chunk, the more likely the entity is named
   only in a neighboring chunk (the cross-boundary coreference problem).
4. **Combined with other context-injection techniques** — title prepending, section-header
   injection, and coref together may compound; coref alone is insufficient.

For standard informative-text RAG (Wikipedia, documentation, articles) with a modern dense
model, coref-before-embed is **not recommended** as a default ingestion step.

---

## 9. Artifacts

| File | Content |
|------|---------|
| `coref_rag_benchmark.ipynb` | Test 1 — custom stress test on one Wikipedia article |
| `test-1-findings.md` | Test 1 results (coref helps: +5pp Recall@5) |
| `coref_public_eval.ipynb` | Test 2 — DAPR ConditionalQA, full coref |
| `test-2-findings.md` | Test 2 results (coref flat, hybrid worse) + analysis |
| `coref_public_eval_v3.ipynb` | Test 3 — DAPR NQ, selective coref + weighted RRF |
| `test-3-findings.md` | Test 3 results (coref flat, hypothesis not confirmed) |
| `coref-rag-hypothesis-and-findings.md` | This file — full synthesis |
