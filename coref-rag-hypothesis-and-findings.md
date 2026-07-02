# Coreference-Aware RAG: Full Hypothesis & Findings

**Project:** Coreference-before-embed ingestion for dense retrieval
**Date:** 2026-07-02
**Notebooks:** `test-1/coref_rag_benchmark.ipynb` (Test 1), `test-2/coref_public_eval.ipynb` (Test 2),
`test-3/coref_public_eval_v3.ipynb` (Test 3), `test-4/coref_public_eval_v4.ipynb` (Test 4),
`test-5/coref_public_eval_v5.ipynb` (Test 5)

## Abstract

We evaluate whether resolving coreference — rewriting pronouns to their antecedent entity names
before dense embedding — improves passage retrieval in RAG. Across five experiments we compare a
dense baseline against coref-augmented indexing using automated coreference (`fastcoref` LingMess)
and manual LLM-quality resolution, on paragraph- and sentence-level chunks from Wikipedia excerpts
and public DAPR benchmarks.

Sentence-level chunking creates pronoun-only passages that lack entity strings for query matching.
On coref-critical questions, baseline Recall@5 was 0.77 (100 chunks, Test 4) and 0.91 (414 chunks,
Test 5). Paragraph benchmarks showed no comparable gap — entities are usually named in the same
chunk — and LingMess coref (77–89% pronoun reduction) did not move retrieval metrics (Tests 2–3).

LLM-based coref outperformed the neural coref model on targeted sentence-level evals: +17pp Recall@5
with zero regressions (Test 4) vs +5pp with 1 regression for LingMess (Test 1). At scale, dense-only
coref stayed flat (Test 5: 0.93 → 0.93), but coref + hybrid fusion recovered hard pronoun queries
(+10pp critical Recall@5; 2 recovered, 1 hurt).

The mechanism is real but conditional. Coref-before-embed helps when chunks are small, resolution
quality is high, and baseline recall on pronoun-only gold passages is low. It is not a default win
for paragraph-level RAG or for automated coref at public-benchmark scale.

---

## 1. Research Question

> Does resolving coreference before embedding — rewriting pronouns to their antecedent entities
> in the indexed text — improve passage retrieval compared to a conventional dense baseline?
> And does combining it with a lexical (BM25) hybrid further help?

---

## 2. Hypothesis (evolved across five tests)

**Initial hypothesis (Test 1):**
Pronouns like "he" or "she" in a passage hide the entity name the query searches for. If we
rewrite those pronouns to the entity name before embedding, the dense vector becomes more
query-aligned, and retrieval improves.

**Refined hypothesis (Test 3):**
The benefit is specifically about **named-entity injection** — rewriting a pronoun to a
proper noun the query names. Rewriting to common nouns ("them" → "mobility aids") adds no
signal. Therefore: *selective* coref (proper-noun antecedents only) on *entity-rich* text
should show a gain, while full coref on common-noun text should be flat.

**Upper-bound hypothesis (Test 4):**
If automated coref quality is the blocker (not the technique itself), then **perfect manual
(LLM) coref** on **sentence-level chunks** — where entities are genuinely hidden behind
pronouns — should produce a clear retrieval win.

**Scale hypothesis (Test 5):**
Test 4's win should replicate on a larger, entity-dense corpus (~10k words, 414 sentence
chunks) with the same manual coref quality.

---

## 3. Experimental Design

### Constant across all tests
- **Invariant:** original text is always returned to the user; only the embedded text changes
- **Gold:** official qrels (or ground-truth chunk IDs) with `score > 0` / explicit gold lists
- **Passage IDs identical** across variants; 1:1 coref alignment asserted
- **No LLM-as-judge, no custom q-gen** (except Tests 1, 4, 5), no re-chunking of public corpora

### Test variations

| | Test 1 | Test 2 | Test 3 | Test 4 | Test 5 |
|--|--------|--------|--------|--------|--------|
| **Corpus** | 1 Wikipedia article | DAPR ConditionalQA | DAPR NaturalQuestions | Apollo 11 Wikipedia | WW2 Wikipedia (~10k words) |
| **Queries** | 20, pronoun-targeted | 271, official | 200, official | 30, entity-targeted | 30, entity-targeted |
| **Coref scope** | Full (LingMess) | Full (LingMess) | Selective proper-noun | Manual LLM | Manual LLM |
| **Chunk size** | Paragraph (~117) | Paragraph (8,093) | Paragraph (8,000) | Sentence (100) | Sentence (414) |
| **Embedding** | Qwen3-Embedding-8B | bge-small-en-v1.5 | bge-small-en-v1.5 | bge-small-en-v1.5 | bge-small-en-v1.5 |
| **Hybrid** | — | RRF 50/50 | RRF 0.7/0.3 | RRF 0.7/0.3 | RRF 0.7/0.3 |

### Three variants compared (Tests 2–5)

| Variant | What gets embedded |
|---------|--------------------|
| **baseline** | Original passage text (dense) |
| **coref_dense** | Coref-rewritten passage text (dense) |
| **coref_hybrid** | RRF fuse: BM25(original) + dense(coref) |

---

## 4. Results Summary

| Test | Corpus type | Coref mode | Chunk | Baseline R@5 | Best variant | Δ R@5 | Δ R@5 (crit) | Verdict |
|------|-------------|------------|-------|-------------|--------------|-------|--------------|---------|
| 1 | Biography (pronoun-heavy) | LingMess auto | Para | 0.500 | coref_dense | **+0.050** | — | ✅ Helps |
| 2 | Gov guidance (common-noun coref) | LingMess auto | Para | 0.289 | baseline | −0.002 | — | ❌ Flat |
| 3 | Wikipedia (entity-rich) | Selective auto | Para | 0.797 | baseline | −0.014 | — | ❌ Flat |
| 4 | Apollo 11 (sentence chunks) | Manual LLM | Sent | 0.817 | coref_dense | **+0.167** | **+0.227** | ✅ Win (N=30) |
| 5 | WW2 (sentence chunks, scaled) | Manual LLM | Sent | 0.933 | coref_hybrid | +0.033 | +0.095 | ⚠️ Flat dense |

### Hybrid results

| Test | Hybrid config | Δ R@5 vs baseline | Verdict |
|------|---------------|-------------------|---------|
| 2 | RRF 50/50 | −0.033 | ❌ Worse (BM25 too weak on long queries) |
| 3 | RRF 0.7/0.3 | −0.078 | ❌ Worse (BM25 too weak on short factoid queries) |
| 4 | RRF 0.7/0.3 | +0.133 | ⚠️ Worse than coref_dense; hurt 1 query |
| 5 | RRF 0.7/0.3 | +0.033 | ⚠️ Partial (2 recovered, 1 hurt) |

### Flip counts

| Test | Variant | Recovered | Hurt | Both fail |
|------|---------|-----------|------|-----------|
| 1 | coref_dense | 2 | 1 | 8 |
| 2 | coref_dense | 4 | 4 | 98 |
| 2 | coref_hybrid | 22 | 35 | 80 |
| 3 | coref_dense | (small) | (small) | (majority) |
| 4 | coref_dense | 4 | 0 | 0 |
| 4 | coref_hybrid | 4 | 1 | 0 |
| 5 | coref_dense | 0 | 0 | 2 |
| 5 | coref_hybrid | 2 | 1 | 0 |

---

## 5. Key Findings

### Finding 1: Smaller chunks hurt retrieval — measurably, but not always fatally

Sentence-level chunking removes the surrounding context that tells a dense retriever who *"he"*
or *"it"* refers to. This is not hypothetical — Tests 4 and 5 measured it on coref-critical
questions (gold chunk uses pronouns, query names the entity):

| Test | Chunk granularity | Chunks | Baseline R@5 (critical) | What it means |
|------|-------------------|--------|-------------------------|---------------|
| 2–3 | Paragraph | 8k+ | (not measured; entity usually in same chunk) | Paragraph chunks often retain entity names |
| 4 | One sentence | 100 | **0.773** | ~5/22 critical queries missed — clear hurt |
| 5 | One sentence | 414 | **0.905** | ~2/21 critical queries missed — hurt exists but smaller |

**Honest read:** Smaller chunks do hurt retrieval when the gold passage is pronoun-only. The
damage is largest on small corpora (Test 4). On a 414-chunk corpus with explicit entity queries,
the same dense model already finds 90%+ of pronoun-only gold without coref — so the "small chunks
hurt" problem is real at the chunk level but partially absorbed at retrieval level when the
corpus is large enough or queries overlap with neighbouring context.

Coref-before-embed can buy back lost context **without enlarging chunks** — Test 4 showed
critical recall 0.773 → 1.000 with LLM coref. Test 5 showed that buy-back does not always
happen (0.905 → 0.905 dense) when baseline is already high.

### Finding 2: LLM-based coref worked better than the LingMess coref model

Tests 1–3 used `fastcoref` LingMessCoref. Tests 4–5 used manual (LLM-performed) coreference.
These are not identical corpora/chunk sizes, so treat this as a cross-test pattern, not a
controlled head-to-head on the same data.

| Dimension | LingMess (Tests 1–3) | Manual LLM (Tests 4–5) |
|-----------|---------------------|------------------------|
| Pronoun reduction | 60–89% | Targeted rewrites on 118/414 chunks (Test 5) |
| Best Δ Recall@5 | +0.05 (Test 1, N=20) | +0.167 (Test 4, N=30) |
| Public benchmark Δ | Flat (Tests 2–3) | Not tested on DAPR |
| Regressions | 1 hurt (Test 1); 4/4 split (Test 2) | 0 hurt (Test 4); 0 hurt (Test 5 dense) |
| Rewrite quality | Grammar errors (*"Mauss's writes"*), occasional wrong antecedent | Clean proper-noun injection in Test 4 |

**What we can honestly claim:**
- On pronoun-stress evals, LLM coref improved retrieval more than LingMess did (+17pp vs +5pp
  on comparable micro-benchmarks; zero vs one regression).
- On paragraph corpora, LingMess ran correctly (77–89% pronoun reduction) but did not improve
  retrieval — wrong rewrite type (common nouns), redundant signal, or entity already in chunk.
- LLM coref is higher quality and safer (no regressions in Tests 4–5 dense), but **Test 5 proves
  quality alone does not guarantee metric improvement** when baseline recall is already 0.93.

**What we cannot claim:** That LLM coref always beats LingMess on the same data at the same
chunk size — we did not run that experiment.

### Finding 3: The mechanism is real but narrow (Test 4)

Test 4 is the strongest evidence that entity injection works: Recall@5 0.82 → 0.98 (+17pp),
coref-critical 0.77 → 1.00, 4 recovered / 0 hurt. But this is a **constructed micro-benchmark**
(100 sentence chunks, 30 questions, 22 coref-critical, one Apollo 11 article). It establishes
an upper bound, not a production guarantee.

### Finding 4: Automated LingMess coref on paragraph benchmarks is flat (Tests 2–3)

- **Test 2 (gov guidance):** pronouns resolve to common nouns — no new searchable entity. Flat.
- **Test 3 (Wikipedia NQ):** selective proper-noun coref, 4237/8000 passages changed, 77%
  pronoun reduction — still flat. Paragraphs already name entities; dense model already captures them.

This is not a LingMess failure — the resolutions ran correctly. The rewrites did not add retrieval
signal that the baseline lacked.

### Finding 5: LLM coref did not replicate at scale (Test 5)

Same manual coref quality as Test 4, same sentence-level granularity, 4× more chunks (414),
entity-dense WW2 text. **coref_dense: 0.933 → 0.933** (0 recovered, 0 hurt). Baseline was
already 0.905 on critical questions — too little headroom for coref to move binary Recall@5.

Hybrid recovered 2 Japan pronoun queries (+3pp overall, +10pp critical) but hurt 1 non-critical
query. Mixed, small, unreliable.

### Finding 6: Hybrid BM25(original) is consistently problematic

Fusing BM25 over **original** pronoun-laden text with dense over coref text either hurts or
underperforms pure coref_dense (Tests 2–5). BM25 reintroduces the ambiguity coref removed.
When coref helps, pure dense on coref text is the better variant (Test 4).

### Finding 7: Pronoun counts confirm both coref engines ran — but only LLM moved evals where it mattered

| Test | Coref engine | Pronouns before → after | Δ Recall@5 |
|------|-------------|------------------------|------------|
| 1 | LingMess | ~75 → ~30 | +0.05 |
| 2 | LingMess | 1,243 → 142 | −0.002 |
| 3 | LingMess | 25,897 → 5,861 | −0.014 |
| 4 | Manual LLM | pronouns removed on critical chunks | **+0.167** |
| 5 | Manual LLM | 118/414 chunks changed | 0.000 (dense) |

High pronoun reduction without retrieval gain (Tests 2–3) = rewrites did not add useful signal.
LLM coref moved metrics only when baseline on critical questions was low enough (Test 4).

---

## 6. Worked Examples

### Test 1 — automated coref helps (biography, pronoun-only passage)

**Query:** "What did Marcel Mauss write about in his work on altruism?"

**Gold passage (original):** `"In it, he writes: …"` — no mention of "Marcel Mauss."
**Coref rewrite:** `"In This note, Marcel Mauss's writes: …"` — entity injected.

### Test 2 — automated coref flat (gov guidance, common-noun antecedent)

**Query:** "Can my mother claim back the VAT paid on the mobility vehicle?"

**Gold passage:** `"…when you pay for them to be supplied…"` — "them" = mobility aids.
**Coref rewrite:** `"…when you pay for certain mobility aids to be supplied…"` — duplicated phrase, no new signal.

### Test 3 — automated coref flat (Wikipedia, entity already named)

NQ gold passages typically contain both the entity name and pronoun references. Dense model
already has the entity signal from the explicit mention.

### Test 4 — manual coref clear win (Apollo 11, sentence chunk)

**Query:** "What did Armstrong and Aldrin name the landing site?"

**Original (chunk 5):** *"They spent about two and a quarter hours together exploring the
site they had named Tranquility Base upon landing."*
**Manual coref:** *"Armstrong and Aldrin spent about two and a quarter hours together exploring
the site Armstrong and Aldrin had named Tranquility Base upon landing."*

Baseline missed (no entity overlap); coref_dense recovered. Zero regressions across 30 queries.

### Test 5 — manual coref flat at scale (WW2, sentence chunk)

**Query:** (Japan-related, q16/q17)

**Original (chunk 243):** *"its ambitions"* / *"it needed"* — pronoun-only for Japan.
Baseline missed these 2 critical queries; **coref_dense still missed them**. **coref_hybrid**
recovered both via BM25 + dense fusion — but hurt q27 (non-critical, chunk already explicit).

---

## 7. Conclusion

**Does coreference resolution before embedding improve retrieval?**

**Smaller chunks hurt** when gold passages are pronoun-only: baseline critical recall was 0.773
(Test 4, 100 chunks) and 0.905 (Test 5, 414 chunks). Paragraph chunking largely avoids this
because the entity is usually named somewhere in the same chunk (Tests 2–3).

**LLM-based coref worked better than LingMess** on the evals that stress this failure mode:
+17pp / 0 regressions (Test 4) vs +5pp / 1 regression (Test 1 LingMess) vs flat despite heavy
pronoun reduction (Tests 2–3 LingMess). But we did not run both engines on identical data, and
LLM coref did **not** improve Test 5 dense retrieval (0.933 → 0.933).

**On public paragraph benchmarks with LingMess:** No measurable gain (Tests 2–3).

**Practical bottom line (conservative):**
- Sentence-level chunking has a real pronoun-context cost — measure it on your data before
  assuming larger chunks are unnecessary.
- If you add coref, LLM-based resolution is safer and more effective than LingMess for entity
  injection — but validate on your corpus size; Test 5 shows high baseline absorbs the benefit.
- Do not treat Test 4 as a universal result. It is an upper bound on a small, favorable benchmark.
- Paragraph-level RAG with a modern dense model does not need coref-before-embed as a default step.

---

## 8. When It *Might* Help (conservative guidance)

All conditions below were observed in the data — none guarantee a gain:

1. **Sentence-level chunks with measured pronoun-only failures** — baseline R@5 on coref-critical
   queries below ~0.85 (Test 4 had 0.773; Test 5 at 0.905 showed no dense gain)
2. **LLM-based coref, not LingMess alone** — cleaner rewrites, no regressions in Tests 4–5;
   LingMess flat on paragraph corpora despite 77–89% pronoun reduction
3. **Small-to-medium corpus where pronoun-only chunks are genuinely missed** — Test 4 (100 chunks)
   yes; Test 5 (414 chunks) no for dense
4. **Pure dense on coref text** — hybrid BM25(original) hurt or underperformed in every test

**Not supported by the data:**
- Default coref for paragraph-level Wikipedia/documentation RAG
- Assuming LingMess pronoun reduction implies retrieval improvement
- Assuming LLM coref always fixes small-chunk retrieval (Test 5 counterexample)
- Hybrid fusion over original BM25 text as a reliable fix

---

## 9. Artifacts

| Path | Content |
|------|---------|
| `test-1/coref_rag_benchmark.ipynb` | Test 1 — custom stress test, LingMess auto coref |
| `test-1/test-1-findings.md` | Test 1 results (+5pp Recall@5) |
| `test-2/coref_public_eval.ipynb` | Test 2 — DAPR ConditionalQA, full auto coref |
| `test-2/test-2-findings.md` | Test 2 results (flat, hybrid worse) |
| `test-3/coref_public_eval_v3.ipynb` | Test 3 — DAPR NQ, selective auto coref |
| `test-3/test-3-findings.md` | Test 3 results (flat, hypothesis not confirmed) |
| `test-4/coref_public_eval_v4.ipynb` | Test 4 — Apollo 11 sentence chunks, manual coref |
| `test-4/test-4-data/` | Original + coref chunks, eval questions |
| `test-4/test-4-findings.md` | Test 4 results (+17pp Recall@5, clear win) |
| `test-5/coref_public_eval_v5.ipynb` | Test 5 — WW2 sentence chunks, manual coref at scale |
| `test-5/test-5-data/` | Original + coref chunks, eval questions, source text |
| `test-5/test-5-findings.md` | Test 5 results (flat dense, hybrid partial) |
| `coref-rag-hypothesis-and-findings.md` | This file — full synthesis |
