# Test 4 — Manual (LLM) Coreference Resolution vs. Model-Based Coref

**Run date:** 2026-07-02  
**Data folder:** `test-4-data/`  
**Hypothesis:** Manual (LLM-quality) coreference resolution at ingestion time produces better
retrieval than no coref, specifically on sentence-level chunks that "lose context" due to small size.

**Headline:** The hypothesis is **confirmed** — and this is the first test in the series where coref
delivers a clear, unambiguous win. Manual coref lifts Recall@5 from **0.817 → 0.983** (+0.167), with
the entire gain concentrated on **coref-critical** questions (R@5 0.773 → **1.000**, +0.227) while
non-critical questions stay flat (0.938 → 0.938). Four queries recovered, **zero hurt** for
`coref_dense`. This is the mirror image of Tests 2–3: with perfect coref quality and sentence-level
chunks, the technique works exactly as theory predicts.

---

## Motivation

Tests 1–3 used `fastcoref` LingMess for coreference resolution. The model produced 77% pronoun
reduction but **no net retrieval gain on public benchmarks** (Test 2, Test 3). One open question:
is the problem with coref-before-embed *in principle*, or with the *quality* of automated coref?

This test uses **manual (LLM-performed) coreference** — the highest quality resolution possible —
to establish an upper-bound on what perfect coref can deliver. If even perfect coref doesn't help
retrieval on sentence-level chunks, the technique has a fundamental ceiling. If it does help, the
issue was model quality (LingMess errors, missed antecedents, etc.).

---

## What's in `test-4-data/`

| File | Description |
|------|-------------|
| `original_chunks.json` | 100 sentence-level chunks from Apollo 11 Wikipedia article, no coref |
| `coref_chunks.json` | Same 100 chunks with manual coreference resolution (pronouns → named entities) |
| `eval_questions.json` | 30 retrieval evaluation questions with gold chunk IDs and coref-critical flags |

---

## Source document

Apollo 11 Wikipedia article (~5,000 words), covering:
- Mission overview and timeline
- Crew biographies (Armstrong, Aldrin, Collins)
- Saturn V launch vehicle
- Lunar module Eagle and the landing
- Surface activities and experiments
- Return to Earth, quarantine, and legacy

---

## Chunking strategy

- **Granularity:** One sentence per chunk (sentence-level)
- **Alignment:** Chunk IDs are 1:1 between original and coref versions
- **Goal:** Maximally stress-test the "small chunks lose context" claim. A single sentence with
  only a pronoun (e.g., "He resigned from NASA in 1971") has zero entity signal for dense retrieval.

---

## Coreference resolution approach

**Manual (LLM-performed)** — not model-based (no LingMess, no neuralcoref):
- Every pronoun (he, him, his, she, they, them, it, its) resolved to its antecedent
- Demonstratives (this, that, these, those) resolved when referring to a named entity
- Only proper nouns and specific noun phrases used as replacements
- Preserves sentence structure; only the referent word changes

### Resolution rules applied:
1. **he/him/his** → person's full name or surname (Armstrong, Aldrin, Collins, Nixon)
2. **they/them** → explicit group (Armstrong and Aldrin, the astronauts)
3. **it/its** → the specific object (Saturn V, Eagle, Columbia, Apollo 11)
4. **these/those** (referring to named things) → the specific noun (the F-1 engines, the lunar samples)

---

## Evaluation questions design

30 questions, of which **22 are coref-critical** (the gold chunk's original text uses only a
pronoun for the entity the question names). These are the cases where coref *should* help retrieval.

8 questions are **non-coref-critical** (the original chunk already names the entity). These serve
as a baseline sanity check — coref should not hurt performance on these.

### Question categories:
- Entity-targeted: "What did Armstrong do after NASA?" → gold chunk says "he resigned"
- Cross-entity: "How did Armstrong's doctoral thesis help NASA?" (trick — it's Aldrin's)
- Object-targeted: "How tall was the Saturn V?" → gold chunk says "It stood 363 feet"
- Event-targeted: "What happened to Eagle after docking?" → gold chunk says "its orbit decayed"

---

## How to run the evaluation

```python
import json
from sentence_transformers import SentenceTransformer
import numpy as np

# Load data
with open('test-4-data/original_chunks.json') as f:
    original = json.load(f)
with open('test-4-data/coref_chunks.json') as f:
    coref = json.load(f)
with open('test-4-data/eval_questions.json') as f:
    questions = json.load(f)

# Embed
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
orig_embeddings = model.encode([c['text'] for c in original])
coref_embeddings = model.encode([c['text'] for c in coref])

# Evaluate
def recall_at_k(query_emb, corpus_emb, gold_ids, k=5):
    scores = np.dot(corpus_emb, query_emb)
    top_k = np.argsort(scores)[-k:][::-1] + 1  # chunk_ids are 1-indexed
    return int(any(g in top_k for g in gold_ids))

results = {'original': [], 'coref': [], 'coref_critical_orig': [], 'coref_critical_coref': []}
for q in questions:
    q_emb = model.encode(q['question'])
    orig_hit = recall_at_k(q_emb, orig_embeddings, q['gold_chunk_ids'])
    coref_hit = recall_at_k(q_emb, coref_embeddings, q['gold_chunk_ids'])
    results['original'].append(orig_hit)
    results['coref'].append(coref_hit)
    if q['coref_critical']:
        results['coref_critical_orig'].append(orig_hit)
        results['coref_critical_coref'].append(coref_hit)

print(f"Overall Recall@5 — Original: {np.mean(results['original']):.3f}")
print(f"Overall Recall@5 — Coref:    {np.mean(results['coref']):.3f}")
print(f"Coref-critical Recall@5 — Original: {np.mean(results['coref_critical_orig']):.3f}")
print(f"Coref-critical Recall@5 — Coref:    {np.mean(results['coref_critical_coref']):.3f}")
```

---

## Measured Results

**Run date:** 2026-07-02 | **Notebook:** `coref_public_eval_v4.ipynb`
**Models:** BAAI/bge-small-en-v1.5 (dense) + rank_bm25 (lexical) | weighted-RRF 0.7/0.3 | TOP_K=5
Chunks: 100 (sentence-level) | Queries: 30 (22 coref-critical, 8 non-critical)

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit |
|---------|----------|---------|-----|----------|-------------|-----------|-------|
| baseline | 0.8167 | 0.6990 | 0.6549 | 0.7727 | 0.9375 | — | — |
| coref_dense | **0.9833** | **0.9145** | **0.9111** | **1.0000** | 0.9375 | **+0.1667** | **+0.2273** |
| coref_hybrid | 0.9500 | 0.8802 | 0.8617 | 0.9545 | 0.9375 | +0.1333 | +0.1818 |

**Flips vs baseline**

| variant | recovered | hurt | both_fail |
|---------|-----------|------|-----------|
| coref_dense | 4 (q2, q4, q19, q26) | 0 | 0 |
| coref_hybrid | 4 (q2, q4, q19, q26) | 1 (q12) | 0 |

### Worked example (q_id 2 — recovered by coref)

**Query:** "What did Armstrong and Aldrin name the landing site?"

- **Returned (original, chunk 5):** *"They spent about two and a quarter hours together exploring the
  site they had named Tranquility Base upon landing."* — pronouns: 2
- **Embedded (manual coref, chunk 5):** *"Armstrong and Aldrin spent about two and a quarter hours
  together exploring the site Armstrong and Aldrin had named Tranquility Base upon landing."* —
  pronouns: 0

The query names *Armstrong and Aldrin*; the original chunk refers to them only as *"They"/"they"*.
Baseline dense retrieval had no lexical/entity overlap with the query subject and missed the gold
chunk in the top 5. The coref rewrite injects both names, aligning query and index semantics — a
direct top-5 recovery.

---

## Interpretation

### 1. Coref helps exactly where the theory says it should

The gain is entirely on **coref-critical** questions: R@5_crit jumps 0.773 → **1.000** (+0.227),
while R@5_noncrit is unchanged at 0.938. That's the cleanest possible signal — coref moves the
metric only on the questions whose gold chunk originally hid the entity behind a pronoun, and leaves
everything else alone. No collateral damage.

### 2. Zero regressions for coref_dense

4 recovered, 0 hurt, 0 both-fail flips. Unlike LingMess in Tests 1–3 (which introduced grammar
artifacts and occasional bad rewrites), manual coref never degraded a query. This isolates coref
*quality* as the variable: perfect resolution is strictly non-harmful here.

### 3. The hybrid is slightly worse than coref_dense (and hurt one query)

`coref_hybrid` (+0.133 R@5) trails `coref_dense` (+0.167) and flipped q12 from hit to miss. This
echoes Tests 2–3: adding BM25(original) drags the strong dense(coref) signal down. BM25 indexes the
*original* pronoun-laden text, so on coref-critical queries it reintroduces the very ambiguity coref
removed. On this data, **pure dense on coref text is the best variant** — the hybrid is a net drag.

### 4. Why this differs from Tests 2–3

| Factor | Tests 2–3 (flat) | Test 4 (clear win) |
|--------|------------------|--------------------|
| Coref quality | LingMess (automated, error-prone) | Manual/LLM (perfect) |
| Chunk size | Paragraph (~100–200 words) | Sentence (~15–30 words) |
| Baseline headroom | High baseline (R@5 0.80), gold often already named entity | Lower on critical subset (0.77), gold hides entity in pronoun |
| Query design | Real benchmark queries (mixed) | 22/30 explicitly entity-targeted |

Two things flipped the result: **(a)** perfect coref quality removed the noise/errors that washed out
LingMess's gains, and **(b)** sentence-level chunking created the pronoun-only gold chunks that make
coref necessary. In paragraph chunks, the entity is usually named *somewhere* in the same chunk, so
the dense model already has the signal. At sentence granularity, a chunk like "They named it
Tranquility Base" genuinely has no entity — exactly the failure mode coref fixes.

---

## What this says about "small chunks lose context"

The claim is **partially validated and partially defeated**:

- **Validated:** the baseline confirms small chunks *do* lose context — R@5_crit is only 0.773
  because pronoun-only sentence chunks are genuinely under-specified.
- **Defeated:** coref-at-ingestion **fully recovers** that lost context (R@5_crit → 1.000) without
  enlarging the chunk. So "small chunks lose context" is a property of *naive* sentence chunking, not
  an inherent limit. Reference resolution lets you keep sentence-level granularity (precise
  retrieval, tight context windows) *and* self-contained chunks.

This is the practical takeaway: if you want small chunks for precision, coref-before-embed is a valid
way to buy back the context you'd otherwise lose — **provided the coref quality is high**.

---

## Caveats / honest scope

- **Small, favorable micro-benchmark.** 100 chunks, 30 questions, one document, and 22/30 questions
  intentionally entity-targeted. This is a *constructed best case*, designed to isolate the mechanism —
  not a representative production workload. A ±1 query flip moves R@5 by ~0.03.
- **Manual coref is the ceiling, not the reality.** These numbers show what *perfect* coref can do.
  Tests 1–3 show that real automated coref (LingMess) captures little of this in practice. The gap
  between Test 4 and Test 3 is precisely the "coref quality" gap.
- **Questions were written alongside the data**, so they align well with what coref exposes. On
  organic queries the coref-critical fraction would be lower, shrinking the aggregate gain.
- **The hybrid finding is consistent across tests:** BM25 over original text undoes coref's benefit
  on the exact queries coref targets. If using a hybrid, index BM25 over the coref text too, or drop
  it for this use case.

---

## Key differences from Tests 1–3

| Dimension | Tests 1–3 | Test 4 |
|-----------|-----------|--------|
| Coref engine | fastcoref LingMess (automated) | Manual/LLM (perfect quality) |
| Chunk size | Paragraph-level (~100-200 words) | Sentence-level (~15-30 words) |
| Corpus | Various (1 article, DAPR datasets) | 1 long article (Apollo 11), 100 chunks |
| Goal | Measure automated coref's retrieval impact | Upper-bound: what can perfect coref deliver? |

---

## Connection to "small chunks lose context" claim

The core claim: *"When you chunk at the sentence level, each chunk loses the surrounding context
(who is 'he'? what is 'it'?), making retrieval unreliable."*

This test directly challenges that by:
1. Chunking at the smallest useful level (one sentence)
2. Resolving all references so each chunk is self-contained
3. Measuring whether self-contained chunks retrieve better than ambiguous ones

If coref-resolved sentence chunks match or beat paragraph-level chunking on these entity queries,
it validates the idea that **coref can substitute for larger chunk windows** as a context-preservation
strategy.

---

## Scope notes

- Single document (Apollo 11), 100 chunks, 30 questions — a focused micro-benchmark, not a
  large-scale eval.
- Manual coref represents the quality ceiling; any production system would be between LingMess
  and this.
- Questions are intentionally biased toward coref-critical cases (22/30) to maximize signal.
- The 1:1 chunk alignment ensures any difference is purely from the text change, not chunking.
