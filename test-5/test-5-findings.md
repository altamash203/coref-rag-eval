# Test 5 — Manual (LLM) Coreference Resolution vs. Model-Based Coref

**Run date:** 2026-07-02  
**Data folder:** `test-5-data/`  
**Hypothesis:** Replicate Test 4 on a larger, entity-dense corpus (~10k words) to verify that
manual (LLM-quality) coreference resolution at ingestion time improves retrieval on sentence-level
chunks — especially on **coref-critical** questions where gold chunks use pronouns instead of named
entities.

**Second claim under test:** *"small chunks lose context."* Sentence-level chunks with bare pronouns
(e.g., "His largest collaboration with Germany…") should become retrievable when pronouns are replaced
with named entities before embedding.

**Headline:** Test 4's clear win **does not replicate** at scale. Manual coref dense retrieval is
**flat** vs baseline (R@5 0.933 → 0.933, R@5_crit 0.905 → 0.905, **0 recovered / 0 hurt**). The
baseline is already near-ceiling on this 414-chunk corpus — pronoun-only gold chunks are retrieved
without coref 90% of the time on critical questions. **`coref_hybrid`** adds a modest overall lift
(R@5 **+0.033**, R@5_crit **+0.095** → 1.000) by recovering two Japan pronoun queries (q16, q17),
but **hurts one non-critical query** (q27). Dense-only coref is not the answer here; hybrid fusion
with BM25 is a partial, mixed signal.

---

## What's in `test-5-data/`

| File | Description |
|------|-------------|
| `world_war2_wikipedia.txt` | Clean ~10,000-word excerpt from the World War II Wikipedia article |
| `original_chunks.json` | 414 sentence-level chunks, pronouns intact (baseline) |
| `coref_chunks.json` | Same 414 chunks with manual LLM coreference resolution |
| `eval_questions.json` | 30 retrieval evaluation questions with gold chunk IDs and coref-critical flags |

---

## Source document

World War II Wikipedia article (~10,000 words), covering:

- Global overview and timeline (1939–1945)
- Causes: Versailles, fascism, Japanese expansion
- European theatre: Poland, France, Battle of Britain, Barbarossa, Stalingrad, D-Day
- Pacific theatre: Pearl Harbor, Midway, island hopping, atomic bombs
- Home fronts, diplomacy, and post-war settlement

Fetched via Wikipedia API (`explaintext`), cleaned (references stripped, truncated to 10k words).

---

## Chunking strategy

- **Granularity:** One sentence per chunk (sentence-level)
- **Tooling:** Python regex sentence splitter — abbreviations protected
- **Count:** 414 chunks from ~10,000 words
- **Alignment:** Chunk IDs are 1:1 between original and coref versions (IDs 1–414 unchanged)
- **Post-build fixes:** Merged `Franklin D.` / `Roosevelt` split (164–165) and `Harry S.` / `Truman` split (380); completed truncated chunk 414 from Wikipedia source

---

## Coreference resolution approach

**Manual (LLM-performed)** — not model-based (no LingMess, no neuralcoref, no spaCy coref):

- Processed in batches of ~52 chunks with preceding context window during manual LLM resolution
- Every pronoun (he/him/his/she/they/them/their/it/its) resolved to antecedent entities
- Demonstratives (this/that/these/those) resolved when referring to named events or entities
- **118 of 414 chunks** changed from original; 102 chunks contained target pronouns
- Preserves sentence structure; only referent words change

### Resolution rules applied (same as Test 4):

1. **he/him/his** → person's name (Hitler, Churchill, Roosevelt, Franco, Ribbentrop, etc.)
2. **they/them/their** → explicit group (the Germans, Axis forces, Vichy forces, the Allies)
3. **it/its** → specific object or country (Japan, Germany, the campaign, the offensive)
4. **these/those/this/that** → specific noun phrase from context (the atomic bombings, the Ardennes offensive)

---

## Evaluation questions design

30 questions, of which **21 are coref-critical** (gold chunk original text relies on pronouns or
demonstratives for the entity the question names). Mix includes:

- Person-centric queries (Hitler, Franco, Chiang Kai-shek, Roosevelt)
- Event-centric queries (Operation Barbarossa, Battle of Britain, Pearl Harbor dilemma)
- Possessive pronoun queries (`its navy`, `its fascist regime`, `their campaign`)
- Non-critical controls where gold chunks already name entities explicitly

---

## Variants (identical to Test 4)

| Label | Retrieval |
|-------|-----------|
| **baseline** | Dense on **original** sentence text |
| **coref_dense** | Dense on the **manual coref** rewrite |
| **coref_hybrid** | **Weighted RRF**: 0.7 × dense(coref) + 0.3 × BM25(original) |

**Invariants:** original text returned to user; gold = `gold_chunk_ids`; same chunk IDs across
variants. Models: `bge-small-en-v1.5` + `rank_bm25`.

---

## Notebook

Run `coref_public_eval_v5.ipynb` to reproduce the three retrieval variants and measured results below.

---

## Comparison to Test 4

| | Test 4 | Test 5 |
|---|--------|--------|
| Source | Apollo 11 (~5k words) | World War II (~10k words) |
| Chunks | 100 | 414 |
| Coref-changed chunks | ~40 | 118 |
| Questions | 30 (22 coref-critical) | 30 (21 coref-critical) |
| Entity density | 3 astronauts + hardware | Dozens of leaders, armies, battles |

Test 5 stress-tests whether Test 4's gains hold at **2× document length** and **4× chunk count** with
much higher entity ambiguity (multiple concurrent "he/they/it" referents across theatres).

| Metric | Test 4 | Test 5 |
|--------|--------|--------|
| Baseline R@5 | 0.817 | **0.933** |
| Baseline R@5_crit | 0.773 | **0.905** |
| coref_dense ΔR@5 | **+0.167** | **0.000** |
| coref_dense ΔR@5_crit | **+0.227** | **0.000** |
| coref_dense recovered | 4 | **0** |
| Best variant | coref_dense | coref_hybrid (+0.033) |

At 414 chunks the dense retriever already finds most gold passages; coref-before-embed has little room
to improve and no longer delivers Test 4's upper-bound signal.

---

## Measured Results

**Run date:** 2026-07-02 | **Notebook:** `coref_public_eval_v5.ipynb`  
**Models:** BAAI/bge-small-en-v1.5 (dense) + rank_bm25 (lexical) | weighted-RRF 0.7/0.3 | TOP_K=5

Chunks: 414 (sentence-level) | Queries: 30 (21 coref-critical, 9 non-critical)

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.9333 | 0.8837 | 0.8581 | 0.9048 | 1.0000 | 0.0000 | 0.0000 |
| coref_dense | 0.9333 | 0.8875 | 0.8644 | 0.9048 | 1.0000 | 0.0000 | 0.0000 |
| coref_hybrid | 0.9667 | 0.8879 | 0.8531 | 1.0000 | 0.8889 | 0.0333 | 0.0952 |

**Flips vs baseline**

| variant | recovered | hurt | both_fail |
| --- | --- | --- | --- |
| coref_dense | 0 | 0 | 2 |
| coref_hybrid | 2 | 1 | 0 |

**Recovered by coref_hybrid (vs baseline):** q16, q17 — both Japan pronoun chunks (243: *"its ambitions"*
/ *"it needed"*; 269: *"left it overconfident"*).

**Hurt by coref_hybrid (vs baseline):** q27 — Italy/Franco support during the Spanish Civil War (chunk 76
already names Mussolini and troop counts; non-critical control).

---

## Interpretation

### 1. `coref_dense` is a complete null result

Recall@5, R@5_crit, and flip counts are **identical** to baseline. Zero queries recovered, zero hurt.
Two queries fail under both baseline and coref_dense (`both_fail=2`). nDCG@10 and MRR tick up slightly
for coref_dense (+0.004 nDCG, +0.006 MRR) without changing binary Recall@5 — ranking shifts within
the top 5, not gold-in-top-5 flips.

This is the opposite of Test 4 (+0.167 R@5, +0.227 R@5_crit, 4 recoveries). Perfect manual coref
does not help when the baseline is already at 0.933 overall and 0.905 on critical questions.

### 2. High baseline headroom absorbs the coref signal

With 414 chunks (vs Test 4's 100), the same embedding model retrieves pronoun-only sentence chunks
most of the time anyway. Possible reasons:

- **Corpus density:** WW2 text repeats entity names across many neighbouring sentences; dense retrieval
  may surface the right *region* even when the pronoun-only gold sentence ranks lower.
- **Query overlap:** Questions name entities explicitly ("Japan", "Hitler", "Franco"); lexical overlap
  with surrounding chunks or partial semantic match may suffice at this corpus size.
- **Ceiling effect:** Only ~2 critical questions (≈10%) remain as hard misses under baseline; too few
  for aggregate R@5_crit to move without recovering all of them.

### 3. `coref_hybrid` partially rescues critical queries — at a cost

Hybrid lifts R@5_crit from 0.905 → **1.000** (+0.095) by recovering q16 and q17 (Japan `it`/`its`
chunks). BM25 over original text plus dense over coref text apparently disambiguates cases where dense
alone on either surface failed.

But hybrid **hurts q27** (non-critical; chunk 76 already explicit), dropping R@5_noncrit from 1.000 →
0.889. Net overall R@5 gain is only +0.033. Same pattern as Test 4: fusing BM25(original) is a mixed
bag — it can help some pronoun cases while reintroducing ambiguity on others.

### 4. Test 4 vs Test 5 — why the divergence?

| Factor | Test 4 (win) | Test 5 (flat dense) |
|--------|--------------|---------------------|
| Chunks | 100 | **414** |
| Baseline R@5 | 0.817 | **0.933** |
| Baseline R@5_crit | 0.773 | **0.905** |
| Entity focus | 3 astronauts + hardware | Dozens of leaders/theatres |
| Hard critical misses | ~5/22 (23%) | ~2/21 (10%) |
| coref_dense ΔR@5_crit | +0.227 | **0.000** |

Test 4's win required a **low critical baseline** (0.773) on a **small** corpus where pronoun-only
chunks were genuinely invisible to dense retrieval. Test 5 shows that as chunk count and baseline
recall rise, even perfect coref has **no marginal value for dense-only retrieval** — the technique's
ceiling is corpus- and baseline-dependent, not universal.

---

## What this says about "small chunks lose context"

- **Still true at the chunk level:** individual sentence chunks like *"left it overconfident"* (chunk
  269) carry no entity string — the context loss is real.
- **Less true at the retrieval level:** with 414 chunks and explicit entity queries, the dense model
  often finds the gold anyway (90.5% on critical questions without coref).
- **Coref helps only on the residual hard cases:** hybrid recovers the ~2 Japan queries baseline missed;
  dense-only coref does not move them — suggesting the coref rewrite alone did not shift embeddings
  enough, but BM25 + coref-dense fusion did.

Practical takeaway: **coref-before-embed is not a free win at sentence level** once the corpus grows
and baseline retrieval is strong. It targets a shrinking tail of hard pronoun queries; hybrid fusion
may capture some of that tail but can regress on easy queries.

---

## Caveats / honest scope

- **414 chunks, 30 questions, one document** — same micro-benchmark caveats as Test 4; ±1 query ≈ 0.03
  R@5 swing.
- **Manual coref quality** was corrected post-build (bad rewrites on chunks 22, 50, 52, etc.); even
  after fixes, dense coref did not beat baseline — so quality is not the bottleneck here; baseline
  headroom is.
- **21/30 coref-critical** (after relabelling weak flags) — still entity-targeted, but baseline is
  higher than Test 4 despite that.
- **2 `both_fail` queries** under baseline and coref_dense — the eval has a small hard core that
  neither variant solves; hybrid fixes two different ones but not necessarily the same two.

---

## Key differences from Test 4

| Dimension | Test 4 | Test 5 |
|-----------|--------|--------|
| Outcome | coref_dense clear win | coref_dense **flat** |
| Best variant | coref_dense (+0.167) | coref_hybrid (+0.033) |
| Baseline R@5_crit | 0.773 | 0.905 |
| coref_dense recovered | 4 | 0 |
| Interpretation | Perfect coref buys back lost context | High baseline absorbs most coref benefit |
