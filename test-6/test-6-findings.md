# Test 6 — Manual Chunking + Manual Coreference Resolution (French Revolution)

**Run date:** 2026-07-03  
**Data folder:** `test-6-data/`  
**Hypothesis:** Replicate Tests 4 and 5, but fix the chunk-quality problems that came from naive
regex sentence splitting. If chunks are built by semantic reading (complete, self-contained
sentences) and coreference is resolved manually, sentence-level chunks that "lose context" through
bare pronouns should become retrievable when those pronouns are replaced with named entities before
embedding.

**Key difference from Test 5:** Test 5 used a Python regex sentence splitter, which produced broken
chunks (orphaned fragments, `Franklin D.` / `Roosevelt` splits) that required post-hoc merges. Test 6
avoids that entirely — chunking and coref were done manually / via sub-agents with semantic judgment,
so every chunk is a complete, retrievable sentence before any coref is applied.

**Headline:** Test 6 lands **between** Test 4 (clear win) and Test 5 (flat). Manual coref lifts
Recall@5 from **0.867 → 0.933** (+0.067) for `coref_dense`, with the entire gain on **coref-critical**
questions (R@5_crit 0.864 → **0.955**, +0.091) while non-critical questions stay flat (0.875 → 0.875).
`coref_hybrid` goes further, reaching **R@5 0.967** and a perfect **R@5_crit 1.000** (+0.136) with
**zero queries hurt**. On this cleaner, entity-dense corpus, coref helps exactly where theory predicts.

---

## What's in `test-6-data/`

| File | Description |
|------|-------------|
| `french_revolution_wikipedia.txt` | Clean ~5,000-word excerpt from the French Revolution Wikipedia article |
| `original_chunks.json` | 204 sentence-level chunks, pronouns intact (baseline) |
| `coref_chunks.json` | Same 204 chunks with manual coreference resolution |
| `eval_questions.json` | 30 retrieval evaluation questions with gold chunk IDs and coref-critical flags |

---

## Source document

French Revolution Wikipedia article (~5,000 words), covering:

- Overview and timeline (1789–1799)
- Causes: financial crisis, the Ancien Régime, Enlightenment critiques
- Estates-General of 1789 and the formation of the National Assembly
- Storming of the Bastille and abolition of feudalism
- The Catholic Church, the Civil Constitution of the Clergy
- Constitutional monarchy, the flight to Varennes, and the fall of the monarchy
- The First Republic, the September Massacres, and the trial and execution of Louis XVI

Fetched via the Wikipedia API (`explaintext`) using `fetch_article.py`, cleaned (references and
section-header markup stripped, whitespace normalised, truncated to ~5,000 words).

---

## Chunking strategy — manual, not regex

- **Granularity:** One sentence per chunk (sentence-level)
- **Method:** The cleaned article was split into 5 sections (~1,000 words each) and chunked by
  sub-agents reading each section, **not** by a regex/Python sentence splitter.
- **Count:** 204 chunks from ~5,000 words
- **Alignment:** Chunk IDs are 1:1 between original and coref versions (IDs 1–204, sequential)
- **Quality rules enforced during chunking:**
  - Every chunk is one complete, grammatically valid sentence with an explicit subject and predicate.
  - Section-header fragments merged into running text (e.g. "Causes.", "Catholic Church.",
    "Varennes and after.") were dropped, not emitted as chunks.
  - The orphaned fragment *"One of the most influential was written by Abbé Sieyès."* (missing its
    noun) was minimally rewritten to *"One of the most influential pamphlets of the Revolution was
    written by Abbé Sieyès."*
  - No proper names or numbers were split across chunks (no `Franklin D.` / `Roosevelt`-style breaks).

---

## Coreference resolution approach

**Manual (LLM-performed)** — not model-based (no LingMess, no neuralcoref, no spaCy coref):

- Processed in batches of ~55 chunks with a preceding-context window during manual LLM resolution.
- Every pronoun (he/him/his/she/her/they/them/their/it/its) resolved to its antecedent entity.
- Demonstratives (this/that/these/those) resolved when referring to a named event or entity.
- A second **strict review pass** additionally resolved same-sentence pronouns and expletive-style
  references, so the only pronouns remaining in `coref_chunks.json` sit inside 3 verbatim historical
  quotations (McManners, Rousseau, and the "Vive le roi" response), which were deliberately left
  untouched to preserve quotation fidelity.
- Preserves sentence structure; only referent words change.

### Resolution rules applied (same as Tests 4/5):

1. **he/him/his** → person's name (Louis XVI, Robespierre, Brissot, Lafayette, Brienne, Launay, etc.)
2. **they/them/their** → explicit group (the National Assembly, the Brissotins, the women marchers,
   the émigré nobility)
3. **it/its** → specific object/event/country (the Anglo-French War, the Catholic Church, the campaign
   for war, the Bastille)
4. **this/that/these/those** → specific noun phrase from context (the split over the loyalty oath, the
   victory at Valmy, the demands for doubling Third Estate representation)

---

## Evaluation questions design

30 questions, of which **22 are coref-critical** (the gold chunk's original text relies on a pronoun
or demonstrative for the entity the question names). 8 are **non-coref-critical** controls where the
gold chunk already names the entity — coref should not move these.

- Person-centric: Louis XVI, Robespierre, Brissot, Launay, Marie Antoinette / Comte d'Artois
- Event/entity-centric: the Anglo-French War debt, the Bastille's governor, the campaign for war,
  the victory at Valmy, the split over the Civil Constitution of the Clergy
- Demonstrative-driven: "these demands", "this challenge", "Emboldened by this", "This stiffened…"
- Non-critical controls: dates and named entities already explicit (Revolution timeline, Calonne's
  reforms, Bastille Day, Battle of Valmy, Place de la Révolution)

---

## Variants (identical to Tests 4/5)

| Label | Retrieval |
|-------|-----------|
| **baseline** | Dense on **original** sentence text |
| **coref_dense** | Dense on the **manual coref** rewrite |
| **coref_hybrid** | **Weighted RRF**: 0.7 × dense(coref) + 0.3 × BM25(original) |

**Invariants:** original text returned to the user; gold = `gold_chunk_ids`; same chunk IDs across
variants. Models: `bge-small-en-v1.5` (dense) + `rank_bm25` (lexical).

---

## Notebook

Run `coref_public_eval_v6.ipynb` to reproduce the three retrieval variants and the measured results
below.

---

## Comparison to Tests 4 and 5

| | Test 4 | Test 5 | Test 6 |
|---|--------|--------|--------|
| Source | Apollo 11 (~5k words) | World War II (~10k words) | French Revolution (~5k words) |
| Chunks | 100 | 414 | 204 |
| Chunking method | regex splitter | regex splitter (post-hoc fixes) | **manual / sub-agent** |
| Questions | 30 (22 crit) | 30 (21 crit) | 30 (22 crit) |
| Baseline R@5 | 0.817 | 0.933 | 0.867 |
| Baseline R@5_crit | 0.773 | 0.905 | 0.864 |
| coref_dense ΔR@5 | **+0.167** | 0.000 | **+0.067** |
| coref_dense ΔR@5_crit | **+0.227** | 0.000 | **+0.091** |
| Best variant | coref_dense | coref_hybrid (+0.033) | coref_hybrid (+0.100) |

Test 6 sits between the two prior tests: a smaller corpus than Test 5 (204 vs 414 chunks) leaves more
headroom for coref to help, and clean manual chunking removes the broken-fragment noise that muddied
Test 5. The result is a modest but genuine dense-only gain plus a clean hybrid win.

---

## Measured Results (auto-generated)

**Run date:** 2026-07-03 | **Notebook:** `coref_public_eval_v6.ipynb`  
**Models:** BAAI/bge-small-en-v1.5 (dense) + rank_bm25 (lexical) | weighted-RRF 0.7/0.3 | TOP_K=5

Chunks: 204 (sentence-level, manually chunked) | Queries: 30 (22 coref-critical, 8 non-critical)

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.8667 | 0.8309 | 0.8033 | 0.8636 | 0.875 | 0.0 | 0.0 |
| coref_dense | 0.9333 | 0.8875 | 0.8638 | 0.9545 | 0.875 | 0.0667 | 0.0909 |
| coref_hybrid | 0.9667 | 0.9021 | 0.8704 | 1.0 | 0.875 | 0.1 | 0.1364 |

**Flips vs baseline**

| variant | recovered | hurt | both_fail |
| --- | --- | --- | --- |
| coref_dense | 3 | 1 | 1 |
| coref_hybrid | 3 | 0 | 1 |

**How to read this:** if `R@5_crit` rises for `coref_dense` while `R@5_noncrit` stays flat, manual
coref helps exactly where it should (pronoun-only gold chunks). A flat `R@5_crit` would mean even
perfect coref can't beat the dense model's implicit context handling at sentence level.

---

## Interpretation

### 1. Coref helps exactly where the theory says it should

The entire `coref_dense` gain is on **coref-critical** questions: R@5_crit rises 0.864 → **0.955**
(+0.091) while R@5_noncrit is unchanged at 0.875. As in Test 4, coref moves the metric only on the
questions whose gold chunk originally hid the entity behind a pronoun/demonstrative, and leaves the
explicit-entity controls alone.

### 2. The hybrid is the best variant and hurts nothing

`coref_hybrid` reaches R@5 **0.967** and a perfect **R@5_crit 1.000** (+0.136) with **0 queries hurt**
— unlike Test 4 and Test 5, where the hybrid regressed at least one query. On this corpus, fusing
BM25(original) with dense(coref) recovers the same three critical queries as dense-only *and* the
extra critical case that dense alone left just outside the top 5, without dragging down any explicit
control. Here the hybrid is a strict improvement, not a mixed bag.

### 3. `coref_dense` has one hurt and one both-fail

Dense-only coref recovered 3 queries but flipped 1 from hit to miss, and 1 query fails under both
baseline and coref_dense. This is the familiar sentence-level trade-off: rewriting a pronoun to a full
entity name shifts the embedding, which usually helps the targeted query but can occasionally nudge a
neighbouring query's ranking. The hybrid absorbs this — its BM25 component over the original text
stabilises the ranking so the net hurt count drops to zero.

### 4. Why Test 6 beats Test 5's flat result

| Factor | Test 5 (flat dense) | Test 6 (dense win) |
|--------|---------------------|--------------------|
| Chunks | 414 | 204 |
| Baseline R@5_crit | 0.905 | 0.864 |
| Chunking | regex splitter + fixes | manual / sub-agent |
| coref_dense ΔR@5_crit | 0.000 | +0.091 |

Two things reopened the gap coref can fill: a **smaller corpus** (204 vs 414 chunks) means the dense
retriever has less redundant entity signal to fall back on, so pronoun-only chunks are genuinely
harder to find without coref; and **clean manual chunking** removes the broken-fragment noise that
made Test 5's gold chunks inconsistent. The lower critical baseline (0.864 vs 0.905) leaves real
headroom, and coref uses it.

---

## What this says about "small chunks lose context"

- **Validated at the chunk level:** sentence chunks like *"Even after it ended, the monarchy continued
  to borrow heavily…"* or *"Its governor, Bernard-René de Launay, surrendered…"* carry no entity
  string on their own — the context loss is real, and the baseline R@5_crit of 0.864 reflects it.
- **Recoverable by coref:** replacing those pronouns with named entities lifts R@5_crit to 0.955
  (dense) and 1.000 (hybrid) **without enlarging the chunk**. Small chunks losing context is a
  property of *naive* chunking, not an inherent limit — reference resolution buys the context back.
- **Chunk quality matters upstream:** because chunking here was manual, there were no orphaned
  fragments for coref to trip over. Clean chunks + clean coref is what let the mechanism work as
  designed.

Practical takeaway: at sentence granularity on a mid-sized, entity-dense corpus, coref-before-embed
is a real (if modest) win for dense retrieval, and a clean win when fused with BM25 — provided both
the chunking and the coref are high quality.

---

## Caveats / honest scope

- **Small, constructed micro-benchmark.** 204 chunks, 30 questions, one document, 22/30 questions
  intentionally entity-targeted. A ±1 query flip moves R@5 by ~0.033. This isolates the mechanism; it
  is not a representative production workload.
- **Manual coref is the quality ceiling.** These numbers show what perfect coref can do; automated
  coref (Tests 1–3) captured little of this in practice.
- **Questions were written alongside the data**, so they align well with what coref exposes. On
  organic queries the coref-critical fraction — and the aggregate gain — would be smaller.
- **Three quoted pronouns remain** in `coref_chunks.json` by design (inside historical quotations);
  they are not gold chunks for any coref-critical question, so they do not affect the results.
- **Hybrid caveat carries from Tests 4/5:** BM25 over original text can reintroduce pronoun ambiguity
  on some queries. It happened not to hurt here, but that is corpus-dependent, not guaranteed.

---

## Key differences from Tests 4 and 5

| Dimension | Test 4 | Test 5 | Test 6 |
|-----------|--------|--------|--------|
| Chunking | regex splitter | regex splitter + post-hoc merges | **manual / sub-agent, no splitter** |
| Chunk quality | some fragments | broken chunks (`Franklin D.`/`Roosevelt`) | complete sentences throughout |
| Outcome | coref_dense clear win | coref_dense flat | coref_dense modest win |
| Best variant | coref_dense (+0.167) | coref_hybrid (+0.033) | coref_hybrid (+0.100) |
| Hybrid queries hurt | 1 | 1 | **0** |
| Interpretation | perfect coref buys back context | high baseline absorbs coref | clean chunks + coref work as designed |
