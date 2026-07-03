# Test 7 — Manual Chunking + Manual Coreference Resolution (American Civil War)

**Run date:** 2026-07-03  
**Data folder:** `test-7-data/`  
**Hypothesis:** Third replication of the sentence-level coref-before-embed experiment (after Test 6 /
French Revolution), on a new entity-dense article. Chunking and coreference were done manually / via
sub-agents with semantic judgment — no regex sentence splitter, no automated coref
(LingMess/spaCy/neuralcoref). If sentence chunks that "lose context" through bare pronouns become
retrievable once those pronouns are replaced with named entities, coref-before-embed helps exactly on
those chunks.

**Headline:** Test 7 is the **clearest win in the 5k-word series so far.** Manual coref lifts Recall@5
from **0.833 → 0.933** for `coref_dense` (+0.100), with the whole gain on **coref-critical** questions
(R@5_crit 0.773 → **0.909**, +0.136) while non-critical questions stay pinned at **1.000**.
`coref_hybrid` goes further to **R@5 0.967** / R@5_crit **0.955** (+0.182) with **zero queries hurt**.
Ranking metrics move sharply too (baseline nDCG@10 0.656 → coref_dense **0.806**; MRR 0.571 →
**0.743**), because coref pulls pronoun-only gold chunks from deep ranks (e.g. rank 30 → 4) up into the
top 5.

---

## What's in `test-7-data/`

| File | Description |
|------|-------------|
| `american_civil_war_wikipedia.txt` | Clean ~5,000-word excerpt from the American Civil War Wikipedia article |
| `original_chunks.json` | 230 sentence-level chunks, pronouns intact (baseline) |
| `coref_chunks.json` | Same 230 chunks with manual coreference resolution |
| `eval_questions.json` | 30 retrieval evaluation questions with gold chunk IDs and coref-critical flags |

---

## Source document

American Civil War Wikipedia article (~5,000 words), covering:

- Overview and timeline (1861–1865)
- Origins: slavery, secession, the Lost Cause ideology, Lincoln's election
- The secession crisis, Fort Sumter, and the outbreak of war
- The border states (Maryland, Missouri, Kentucky, West Virginia)
- Mobilization, conscription, draft resistance, and Southern Unionists
- Women in the war (Union and Confederate home fronts)
- The Union Navy, ironclads, and the Anaconda Plan

Fetched via the Wikipedia API (`explaintext`) using `fetch_article.py`, cleaned (references and
section-header markup stripped, whitespace normalised, truncated to ~5,000 words).

---

## Chunking strategy — manual, not regex

- **Granularity:** One sentence per chunk (sentence-level)
- **Method:** The cleaned article was split into 5 sections (~1,000 words each) and chunked by
  sub-agents reading each section — **not** by a regex/Python sentence splitter.
- **Count:** 230 chunks from ~5,000 words
- **Alignment:** Chunk IDs are 1:1 between original and coref versions (IDs 1–230, sequential)
- **Quality rules enforced during chunking:**
  - Every chunk is one complete, grammatically valid sentence with an explicit subject and predicate.
  - Section-header fragments merged into running text (e.g. "Origins.", "Secession crisis.",
    "Mobilization.", "Union Navy.") were dropped, not emitted as chunks.
  - Multi-sentence block quotations (Richard N. Current, James McPherson) were split at clean sentence
    boundaries with balanced quotation marks per chunk.
  - No proper names or numbers were split across chunks.

---

## Coreference resolution approach

**Manual (LLM-performed)** — not model-based (no LingMess, no neuralcoref, no spaCy coref):

- Processed in 5 batches of ~46 chunks with a preceding-context window during manual LLM resolution.
- **Strict mode:** pronouns were resolved even when the antecedent sat in the same sentence, so chunks
  are maximally explicit (e.g. "Anderson took matters into his own hands" → "…into Anderson's own
  hands").
- **Quotation exception:** text inside direct quotations was left verbatim to preserve source fidelity.
  The only pronouns remaining in `coref_chunks.json` are almost entirely inside preserved quotations
  (chiefly the Richard N. Current block quote).
- Preserves sentence structure; only referent words change.

### Corpus-level coref footprint (measured)

| Metric | Value |
|--------|-------|
| Chunks total | 230 |
| Chunks changed by coref | 90 (39%) |
| Pronouns before coref | 134 |
| Pronouns after coref | 13 (121 removed, **90% reduction**) |

The 13 residual pronouns are almost all inside preserved direct quotations.

---

## Evaluation questions design

30 questions, of which **22 are coref-critical** (the gold chunk's original text relies on a pronoun
or demonstrative for the entity the question names) and **8 are non-critical** controls where the gold
chunk already names the entity.

**Honesty controls on the questions:**

- Queries are phrased as natural retrieval questions, not restatements of the gold sentence.
- Every query content word was verified to appear somewhere in the **original** corpus, so no question
  can be answered *only* via a term introduced by the coref rewrite. (Two early drafts using "admitting"
  and "paroled" — words that exist only after coref — were rephrased before finalising.)
- `coref_critical=True` means the **gold** chunk hides the queried entity behind a pronoun. It does
  **not** mean the baseline cannot retrieve it — as the analysis below shows, the dense baseline still
  finds many pronoun-only gold chunks via neighbouring named context.

---

## Variants (identical to Tests 4/5/6)

| Label | Retrieval |
|-------|-----------|
| **baseline** | Dense on **original** sentence text |
| **coref_dense** | Dense on the **manual coref** rewrite |
| **coref_hybrid** | **Weighted RRF**: 0.7 × dense(coref) + 0.3 × BM25(original) |

**Invariants:** original text returned to the user; gold = `gold_chunk_ids`; same chunk IDs across
variants. Models: `bge-small-en-v1.5` (dense) + `rank_bm25` (lexical).

---

## Notebook

Run `coref_public_eval_v7.ipynb` to reproduce the three retrieval variants, the measured results
below, and the practical analysis in section 10 (per-query recovered/hurt breakdown with examples).

---

## Comparison to Tests 4, 5 and 6

| | Test 4 | Test 5 | Test 6 | Test 7 |
|---|--------|--------|--------|--------|
| Source | Apollo 11 (~5k) | World War II (~10k) | French Revolution (~5k) | American Civil War (~5k) |
| Chunks | 100 | 414 | 204 | 230 |
| Chunking method | regex splitter | regex splitter (+fixes) | manual / sub-agent | manual / sub-agent |
| Questions | 30 (22 crit) | 30 (21 crit) | 30 (22 crit) | 30 (22 crit) |
| Baseline R@5 | 0.817 | 0.933 | 0.867 | 0.833 |
| Baseline R@5_crit | 0.773 | 0.905 | 0.864 | 0.773 |
| coref_dense ΔR@5 | +0.167 | 0.000 | +0.067 | **+0.100** |
| coref_dense ΔR@5_crit | +0.227 | 0.000 | +0.091 | **+0.136** |
| coref_dense recovered | 4 | 0 | 3 | **4** |
| Best variant | coref_dense | coref_hybrid (+0.033) | coref_hybrid (+0.100) | coref_hybrid (+0.133) |

Test 7 reproduces Test 4's pattern almost exactly: a low critical baseline (0.773) on a ~5k-word
corpus leaves real headroom, and coref fills it. The manual chunking (as in Test 6) keeps chunks clean,
and the strict same-sentence coref pass drove pronoun density down 90%, giving the dense model named
entities to match on.

---

## Measured Results (auto-generated)

**Run date:** 2026-07-03 | **Notebook:** `coref_public_eval_v7.ipynb`  
**Models:** BAAI/bge-small-en-v1.5 (dense) + rank_bm25 (lexical) | weighted-RRF 0.7/0.3 | TOP_K=5

Chunks: 230 (sentence-level, manually chunked) | Queries: 30 (22 coref-critical, 8 non-critical)

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.8333 | 0.6561 | 0.5706 | 0.7727 | 1.0 | 0.0 | 0.0 |
| coref_dense | 0.9333 | 0.8062 | 0.7428 | 0.9091 | 1.0 | 0.1 | 0.1364 |
| coref_hybrid | 0.9667 | 0.783 | 0.7233 | 0.9545 | 1.0 | 0.1333 | 0.1818 |

**Flips vs baseline**

| variant | recovered | hurt | both_fail |
| --- | --- | --- | --- |
| coref_dense | 4 | 1 | 1 |
| coref_hybrid | 4 | 0 | 1 |

**How to read this:** `coref_critical` marks queries whose *gold* chunk hides the entity behind a
pronoun. It does not mean the baseline cannot retrieve it. A rise in `R@5_crit` for `coref_dense` while
`R@5_noncrit` stays flat is the signal that coref helped where it should.

---

## Practical analysis — how coreference performed (with examples)

The notebook's section 10 prints the per-query breakdown. Summary of what actually happened this run:

### Queries recovered by coref_dense (baseline miss → coref hit): 4

All four are coref-critical, and in each the coref rewrite injected the named entity that the query
asked for, pulling the gold chunk up into the top 5.

| q_id | Query | Gold | Pronoun fix | Gold rank baseline → coref_dense → hybrid |
|------|-------|------|-------------|--------------------------------------------|
| q1 | "How many Deep South slave states seceded after Lincoln won the 1860 election?" | 46 | "His victory" → "Lincoln's victory" | 8 → **3** → 3 |
| q9 | "What did Lincoln say about collecting duties and imposts…?" | 87 | "He stated" → "Lincoln stated" | 7 → **2** → 2 |
| q10 | "How did Lincoln close his first inaugural address?" | 88 | "His speech" → "Lincoln's speech" | 30 → **4** → 5 |
| q12 | "Who commanded the Fort Sumter garrison before the war began?" | 101 | "its garrison" → "Fort Sumter's garrison" | 10 → **5** → 4 |

The q10 case is the most striking: the gold chunk sat at rank **30** under baseline (the sentence
"His speech closed with a plea…" has no entity string at all), and coref lifted it to rank **4**.

### Queries hurt by coref_dense (baseline hit → coref miss): 1

Honest downside. q13 ("What happened to Fort Sumter after the Confederate bombardment began on April
12?") — gold chunk 117 was at rank 5 under baseline and slipped to rank 6 under coref_dense. The fix
here was "it fell the next day" → "the fort fell the next day"; replacing a pronoun with the generic
"the fort" (rather than a distinctive entity name) slightly diluted the embedding and cost one rank.
**`coref_hybrid` recovers this** (0 hurt overall) because the BM25-over-original component keeps the
lexical signal.

### Coref-critical but the baseline already found it (coref-critical ≠ impossible)

Several coref-critical queries were already answered at rank 1 by the baseline, because neighbouring
named chunks give the dense model enough topical signal even when the gold sentence itself is
pronoun-only:

- q2 ("What do historians disagree about…?") — gold 33 "They disagree on the North's reasons…" —
  baseline rank 1, coref_dense rank 1.
- q3 ("Why was there a sectional balance in the Senate but not the House?") — gold 38 "This had kept a
  sectional balance…" — baseline rank 1.
- q4 ("What caused the capture of Atlanta and the March to the Sea?") — gold 17 "This led to the fall
  of Atlanta…" — baseline rank 1.

This is why R@5_crit does not go to 1.000 purely from the recoveries, and why the honest framing
matters: coref moves the hard tail of pronoun-only chunks, not every coref-critical query.

---

## Interpretation

### 1. Coref helps exactly where the theory says it should

The entire `coref_dense` Recall@5 gain lands on coref-critical questions (R@5_crit 0.773 → 0.909),
while non-critical questions are flat at 1.000. Four gold chunks that were invisible or deep-ranked
under baseline (ranks 7, 8, 10, 30) surfaced into the top 5 once their pronoun was replaced with the
named entity.

### 2. Ranking quality improves more than binary recall

nDCG@10 jumps 0.656 → 0.806 and MRR 0.571 → 0.743 for coref_dense — larger relative moves than
Recall@5. Coref does not just flip in/out of the top-5; it lifts gold chunks several ranks (q10: 30 →
4), which is exactly the behaviour expected when a bare-pronoun sentence gains its entity string.

### 3. The hybrid is the best variant and hurts nothing

`coref_hybrid` reaches R@5 0.967 / R@5_crit 0.955 with **0 hurt** — it keeps all four recoveries and
repairs the single query (q13) that dense-only coref cost. As in Test 6, on this corpus the hybrid is a
strict improvement rather than the mixed bag seen in Tests 4/5.

### 4. Consistent with Test 4, unlike Test 5

Test 7 mirrors Test 4 (clear win) rather than Test 5 (flat). The common factor is a **low critical
baseline on a ~5k-word corpus**: at 0.773, roughly five critical gold chunks are genuine misses, giving
coref room to work. Test 5's flatness came from a high 0.905 baseline on a 414-chunk corpus where the
dense model already found nearly everything.

---

## What this says about "small chunks lose context"

- **Validated at the chunk level:** sentences like "His speech closed with a plea…" (chunk 88) or "Its
  status had been contentious for months" (chunk 100) carry no entity string on their own — the context
  loss is real, and it shows up as deep baseline ranks.
- **Recoverable by coref:** replacing those pronouns with named entities lifts the affected gold chunks
  into the top 5 without enlarging the chunk. Small chunks losing context is a property of *naive*
  chunking, not an inherent limit.
- **But not every pronoun matters for retrieval:** several coref-critical chunks were already found by
  the baseline through neighbouring context. Coref targets the hard tail, not the whole set.

Practical takeaway: at sentence granularity on a mid-sized, entity-dense corpus, coref-before-embed is
a real win for dense retrieval and a clean win when fused with BM25 — provided both the chunking and
the coref are high quality.

---

## Caveats / honest scope

- **Small, constructed micro-benchmark.** 230 chunks, 30 questions, one document, 22/30 questions
  entity-targeted. A ±1 query flip moves R@5 by ~0.033.
- **Manual coref is the quality ceiling**, not what automated coref delivers in practice (Tests 1–3).
- **Questions were written alongside the data** but audited so no query depends on a coref-only term;
  still, the coref-critical fraction is higher than an organic query mix would be.
- **Residual quoted pronouns** (13, mostly the Richard N. Current block quote) are preserved by design
  and are not gold chunks for any coref-critical question.
- **Hybrid caveat carries from prior tests:** BM25 over original text can reintroduce ambiguity on some
  queries; it happened to help (not hurt) here, but that is corpus-dependent.

---

## Key differences from Tests 4, 5 and 6

| Dimension | Test 4 | Test 5 | Test 6 | Test 7 |
|-----------|--------|--------|--------|--------|
| Chunking | regex | regex + fixes | manual | manual (+ strict same-sentence coref) |
| Outcome | coref_dense clear win | coref_dense flat | coref_dense modest win | coref_dense clear win |
| Best variant | coref_dense (+0.167) | coref_hybrid (+0.033) | coref_hybrid (+0.100) | coref_hybrid (+0.133) |
| Hybrid queries hurt | 1 | 1 | 0 | 0 |
| Pronoun reduction | ~partial | ~partial | high | **90%** |
| Interpretation | perfect coref buys back context | high baseline absorbs coref | clean chunks + coref work | low baseline + clean chunks → clearest 5k win |
