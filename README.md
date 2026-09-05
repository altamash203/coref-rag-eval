# Coreference-Aware RAG Benchmark

**Does resolving coreference (pronouns → entity names) before embedding improve dense retrieval?**

- **Coref:** replacing pronouns (*he*, *it*, *they*) with the entity they refer to (*Armstrong*, *Apollo 11*, *the Allies*) before indexing.
- **The problem:** a dense retriever matches on what's in the chunk — if the chunk says *"he resigned"* but the query says *"Armstrong"*, there is no shared entity string to match on.
- **Small chunks lose context:** at sentence level, the antecedent (*"Armstrong joined NASA in 1962"*) lives in a different chunk, so *"He resigned in 1971"* has no entity name left in it.

This is a research proof-of-concept. **Seven tests**, mixed results, and two limitations documented
below that a reviewer should weigh before believing any of the positive numbers.

---

## Abstract

When you build a search system over documents, you split text into chunks and index them. If a
chunk says *"He resigned in 1971"* but someone searches for *"Armstrong"*, the search may fail —
the name isn't in the chunk. **Coreference resolution** replaces pronouns with the names they refer
to before indexing.

Seven tests were run. They split cleanly into two groups that answer different questions.

**Tests 1–3 (automated coref, LingMess/fastcoref).** On two public DAPR benchmarks with externally
authored queries and qrels, coref-before-embed did nothing: Recall@5 moved −0.0015 on
ConditionalQA and −0.0142 on NaturalQuestions, both within noise. Coref itself ran correctly
(77–89% pronoun reduction). These are the only tests in the repo whose queries were not written
by the same process that wrote the data — see the weak-null caveat below.

**Tests 4–7 (manual/LLM coref, sentence-level chunks of one Wikipedia article each).** Here coref
does move the metrics, sometimes a lot: dense Recall@5 +0.167 (Test 4, Apollo 11), 0.000 (Test 5,
WWII), +0.067 (Test 6, French Revolution), +0.100 (Test 7, American Civil War). The gain lands on
coref-critical questions and leaves the controls flat, which is what the theory predicts.

**But the tests 4–7 design has a hole.** In many of those questions the coref rewrite inserts into
the gold chunk the exact entity string the query is searching for. On test-7, **all four** queries
coref recovered are cases like this. On those questions the recall gain is partly a lexical term
match that the rewrite manufactured, not evidence that the technique generalises. A second audit
found that a share of the questions flagged `coref_critical` have rewrites that add no new content
word to the gold chunk at all — 15 of 21 on test-5.

**Bottom line:** the mechanism is real and demonstrable on constructed sentence-level evals. On the
two public benchmarks it produced no gain, and the constructed evals carry a validity problem that
the public benchmarks do not. Treat the positive numbers as an upper bound measured under
favourable conditions, not as a result you should expect to reproduce on your own corpus.

---

## The seven tests at a glance

Every number below is copied from the committed `test-*/test-*-findings.md` files.

| Test | Corpus | Coref | Chunks | Queries | Baseline R@5 | coref_dense R@5 | coref_hybrid R@5 | Best Δ R@5 | Verdict |
|------|--------|-------|--------|---------|--------------|-----------------|------------------|-----------|---------|
| 1 | Wikipedia (altruism), pronoun-targeted q-gen | LingMess (auto) | 117 (≤60-word groups) | 20 | 0.500 | 0.550 | — | **+0.050** | Small gain, N=20 |
| 2 | DAPR ConditionalQA (gov guidance) | LingMess (auto) | 8,093 para | 271 | 0.2894 | 0.2879 | 0.2565 | −0.0015 | Flat (weak null) |
| 3 | DAPR NaturalQuestions (Wikipedia) | LingMess, selective | 8,000 para | 200 | 0.7967 | 0.7825 | 0.7192 | −0.0142 | Flat (weak null) |
| 4 | Apollo 11 Wikipedia | Manual (LLM) | 100 sent | 30 | 0.8167 | **0.9833** | 0.9500 | **+0.1667** | Largest win |
| 5 | World War II Wikipedia (~10k words) | Manual (LLM) | 414 sent | 30 | 0.9333 | 0.9333 | 0.9667 | +0.0333 | Dense flat |
| 6 | French Revolution Wikipedia | Manual (LLM) | 204 sent | 30 | 0.8667 | 0.9333 | **0.9667** | +0.1000 | Modest win |
| 7 | American Civil War Wikipedia | Manual (LLM) | 230 sent | 30 | 0.8333 | 0.9333 | **0.9667** | +0.1333 | Clear win |

Tests 1 and 2–3 use different embedding models and question sources from each other and from
tests 4–7, so the rows are not directly comparable. See
[What this repo does not establish](#what-this-repo-does-not-establish).

### Tests 6 and 7 — the cleanest runs

Tests 6 and 7 (both run 2026-07-03) are the two most carefully built experiments in the repo:
chunking was done by reading the text rather than by a regex splitter, so there are no broken
fragments; both ship the source `.txt` and the `fetch_article.py` that produced it; and test 7 adds
an explicit audit that no query depends on a term that exists only after coref.

**Test 6 — French Revolution, 204 chunks, 30 queries (22 coref-critical, 8 non-critical)**

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit | recovered | hurt |
|---------|----------|---------|-----|----------|-------------|-----------|-------|-----------|------|
| baseline | 0.8667 | 0.8309 | 0.8033 | 0.8636 | 0.8750 | — | — | — | — |
| coref_dense | 0.9333 | 0.8875 | 0.8638 | 0.9545 | 0.8750 | +0.0667 | +0.0909 | 3 | 1 |
| coref_hybrid | 0.9667 | 0.9021 | 0.8704 | 1.0000 | 0.8750 | +0.1000 | +0.1364 | 3 | 0 |

**Test 7 — American Civil War, 230 chunks, 30 queries (22 coref-critical, 8 non-critical)**

| variant | recall@5 | nDCG@10 | MRR | R@5_crit | R@5_noncrit | Δrecall@5 | Δcrit | recovered | hurt |
|---------|----------|---------|-----|----------|-------------|-----------|-------|-----------|------|
| baseline | 0.8333 | 0.6561 | 0.5706 | 0.7727 | 1.0000 | — | — | — | — |
| coref_dense | 0.9333 | 0.8062 | 0.7428 | 0.9091 | 1.0000 | +0.1000 | +0.1364 | 4 | 1 |
| coref_hybrid | 0.9667 | 0.7830 | 0.7233 | 0.9545 | 1.0000 | +0.1333 | +0.1818 | 4 | 0 |

Test 7's ranking metrics move more than its recall (nDCG@10 0.6561 → 0.8062, MRR 0.5706 → 0.7428),
because coref lifts pronoun-only gold chunks several ranks at once — one gold chunk went from rank
30 to rank 4. That is the mechanism behaving as designed. It is also, on all four recovered
queries, a query-term injection case; see the next section.

---

## Read the deltas at the right scale

**Tests 4–7 each use 30 questions. In tests 5, 6 and 7 every question has exactly one gold chunk**
(verified against the committed JSON; test 4 has 24 single-gold and 6 two-gold questions). So:

- **One query is worth 1/30 = ~3.3pp of Recall@5.**
- On the 22-question coref-critical subset, one query is worth ~4.5pp of R@5_crit.

Every headline delta in this repo is therefore a handful of queries:

| Test | Δ R@5 | queries that represents |
|------|-------|-------------------------|
| 4 (coref_dense) | +0.1667 | 5 |
| 5 (coref_hybrid) | +0.0333 | 1 |
| 6 (coref_dense) | +0.0667 | 2 |
| 6 (coref_hybrid) | +0.1000 | 3 |
| 7 (coref_dense) | +0.1000 | 3 |
| 7 (coref_hybrid) | +0.1333 | 4 |

The flip tables in the findings confirm this directly: test 6 recovered 3 queries and hurt 1; test 7
recovered 4 and hurt 1. **There are no confidence intervals anywhere in this repo**, and at N=30 a
±2 query swing would erase or double any of these results.

---

## Limitation: query-term injection

**This is the most serious threat to validity in tests 4–7, and it was previously undisclosed.**

### The mechanism

In many coref-critical questions, the rewrite inserts into the gold chunk the exact entity string
that appears in the question. The retriever then finds the chunk partly because the two now share a
literal term — a term the rewrite put there.

Concrete example, **test-7 q1** (one of the four queries coref recovered):

> **Question:** How many Deep South slave states seceded after **Lincoln** won the 1860 election?
>
> **Gold chunk 46, original:** "**His** victory triggered declarations of secession by seven slave
> states of the Deep South, all of whose riverfront or coastal economies were based on cotton that
> was cultivated by slave labor."
>
> **Gold chunk 46, coref rewrite:** "**Lincoln's** victory triggered declarations of secession by
> seven slave states of the Deep South, …"

The only content word the rewrite added is `lincoln`. The query also contains `lincoln`. The gold
chunk moved from rank 8 to rank 3.

### The counts

A coref-critical question counts as injection when the content words its rewrite added to the gold
chunk intersect the question's own content words.

> **Provenance.** The relabelling and injection counts in this README were computed from the
> committed `original_chunks.json`, `coref_chunks.json` and `eval_questions.json` in each
> `test-*-data/` folder, and can be recomputed from those files: tokenise the gold chunk before and
> after the rewrite into lowercased content words (dropping stopwords and tokens of two characters
> or fewer, keeping hyphenated identifiers such as `F-1` whole), take the set difference to get the
> added tokens, and intersect that with the question's tokens. No retrieval run is involved. The
> per-question verdicts are stored in each `eval_questions.json` as `critical_confirmed`,
> `critical_added_tokens` and `query_term_injection`, so every count below can be checked by
> summing those fields.

| test | coref-critical questions | rewrite injected a query term |
|------|--------------------------|-------------------------------|
| test-4 | 22 | **14** |
| test-5 | 21 | **2** |
| test-6 | 22 | **8** |
| test-7 | 22 | **16** |

### It is worse than the aggregate suggests

The findings files record *which* queries flipped from baseline-miss to coref-hit. Cross-referencing
those against the injection list:

| test | variant | queries coref recovered | of those, injection cases |
|------|---------|-------------------------|---------------------------|
| test-4 | coref_dense | q2, q4, q19, q26 | **3 of 4** (4 of 4 under a per-gold-chunk rule) |
| test-5 | coref_hybrid | q16, q17 | **0 of 2** |
| test-6 | coref_dense | not recorded | cannot be checked |
| test-7 | coref_dense | q1, q9, q10, q12 | **4 of 4** |

**On test 7 — the repo's cleanest positive result — every single query that coref recovered is a
query-term injection case.** Three of the four resolve a pronoun to `Lincoln`, which the query also
names. On these questions, improved recall is partly mechanical: the rewrite handed the retriever
the string it was looking for. It is not evidence that coreference resolution is a generally useful
retrieval technique.

Two honest qualifications, in both directions:

- **This is not fabrication.** Resolving *"His victory"* to *"Lincoln's victory"* is correct
  coreference, and a real user asking about Lincoln would name Lincoln. The problem is that the
  questions were written against the same data, so the overlap is guaranteed rather than observed.
  What the experiment cannot do is separate "coref helped retrieval" from "the rewrite and the query
  now share a term".
- **Test 5 is the counterexample.** Its two recovered queries are *not* injection cases — and test 5
  is also the test where dense-only coref gained exactly nothing.
- **Test 7's findings file already documents a partial control:** two draft questions using words
  that exist only after coref ("admitting", "paroled") were rewritten before finalising. That
  control stops a query from being *unanswerable* without coref. It does not stop the rewrite from
  injecting a term the query already contained, which is the effect measured here.

**This does not affect tests 2 and 3.** Those use DAPR's externally authored queries and official
qrels — neither the questions nor the relevance labels were written by anyone who saw the coref
rewrites. That independence is precisely why their null result matters, and precisely what tests
4–7 lack.

---

## Limitation: some `coref_critical` flags are not supported by the data

A question is only genuinely coref-critical if resolving coreference actually *adds* entity
information the original gold chunk lacked. Some questions flagged `coref_critical: true` have gold
chunks whose rewrite adds no new content word at all — the entity was already there.

From test-5 (q3):

> **Original:** "Chiang Kai-shek deployed his best army…"
> **Coref rewrite:** "Chiang Kai-shek deployed **Chiang Kai-shek's** best army…"

`Chiang Kai-shek` was already in the chunk. Coref cannot have helped retrieval here by the mechanism
the hypothesis proposes.

| test | flagged `coref_critical` | rewrite added nothing new | confirmed |
|------|--------------------------|---------------------------|-----------|
| test-4 | 22 | **7** | 15 |
| test-5 | 21 | **15** | 6 |
| test-6 | 22 | **0** | 22 |
| test-7 | 22 | **4** | 18 |

**Test 6 is the clean one:** all 22 flagged questions have rewrites that genuinely add entity
information. **Test 5 is the worst:** 15 of its 21 coref-critical questions are unsupported, which
is a plausible partial explanation for its flat dense result — most of its "critical" subset was
never critical.

Two things this does **not** do:

- **The original labels have not been changed.** A `critical_confirmed` field was added alongside
  the existing `coref_critical` field in every `eval_questions.json`, together with
  `critical_added_tokens` (the content words the rewrite added) and `query_term_injection`. The
  original flags are preserved, so the relabelling is auditable per question in the data itself.
- **No metric has been recomputed.** Every `R@5_crit` figure in the findings files and in this README
  was computed against the **original** labels. Recomputing the critical-subset metrics against
  `critical_confirmed` would require re-running the notebooks, which this pass did not do. So the
  reported per-test critical metrics and this table describe different question sets.

The audit has its own sensitivity, and only test-4 is affected by it. Splitting on every
non-alphanumeric character shreds `F-1` and `S-II` into fragments the length filter discards, which
misclassifies two questions; scoping the token difference per gold chunk rather than over their
union changes three more. Test-4's unsupported count therefore ranges from 4 to 9 depending on the
rule, with 7 under the rule described above. Tests 5–7 give the same counts under every variant.

---

## Limitation: tests 2–3 are a weak null, not a clean negative

Tests 2 and 3 do not run on the full DAPR corpus. Both subsample, and the framing needs to be
accurate in both directions.

| | Test 2 (ConditionalQA) | Test 3 (NaturalQuestions) |
|--|------------------------|---------------------------|
| Corpus cap | `CONDITIONALQA_MAX_CORPUS = 8000` → 8,093 passages kept | `CORPUS_MAX = 8000` → 8,000 passages |
| Full corpus | ~69k passages | ~2.68M passages |
| Query cap | none — all 271 test queries with qrels | `MAX_QUERIES = 200` (first 200) |
| Baseline R@5 | 0.2894 | 0.7967 |

**The document-aware cap is a strength.** Both notebooks keep *whole gold-containing documents
first* — the gold passage plus every other passage from the same document — and only then top up
with other whole documents until the cap. DAPR is hard precisely because the gold passage sits among
topically near-identical passages from the same document, so this retains the hardest distractors. A
naive random sample would have thrown those away and made retrieval artificially easy.

**The small corpus is a weakness for the null result specifically.** Fewer candidates means a higher
baseline, and a higher baseline leaves less headroom for any effect to show. Test 3's baseline
Recall@5 is **0.7967** — the retriever already finds the gold passage in the top 5 four times out of
five. An 8,000-passage pool drawn from 2.68M is 0.3% of the corpus. Whatever coref could contribute
has very little room left to appear in.

**Therefore: tests 2–3 should be read as a weak null, not as a clean negative result.** They show
that coref-before-embed did not help *in this subsampled setting with a strong baseline*. They do
not establish that it would not help on the full corpus, where the baseline would be lower and the
headroom larger. The honest statement is that the technique failed to demonstrate a benefit, not
that it was demonstrated to have none.

What they *do* establish, and what tests 4–7 cannot: with externally authored queries and official
qrels, on a corpus nobody involved in this project constructed, coref-before-embed produced no
measurable gain.

---

## Do not overstate the win

This section survives from the earlier version of this README, with the new findings folded in.

- **Test 4 (+0.1667) is a small micro-benchmark**: 100 chunks, 30 questions, 22 coref-critical, one
  document. ±1 query moves Recall@5 by ~3.3pp, so the entire result is 5 queries.
- **Test 5 did not replicate** Test 4's dense-only gain (0.9333 → 0.9333, 0 recovered / 0 hurt).
  `coref_hybrid` recovered 2 queries (q16, q17) for +0.0333 overall and R@5_crit 0.9048 → 1.0000,
  but **hurt one non-critical query** (q27), dropping R@5_noncrit from 1.0000 to 0.8889.
- **Tests 6 and 7 replicate the direction but not the size**: dense-only +0.0667 and +0.1000 versus
  Test 4's +0.1667. The pattern across tests 4–7 is that the gain tracks how much headroom the
  baseline left, not how good the coref was — all four used the same manual LLM coref.
- **Every one of test 7's four recovered queries is a query-term injection case**, and 3 of 4 (or 4
  of 4, depending on the rule) of test 4's. The strongest positive results in the repo are the ones
  most exposed to the injection objection. See
  [Limitation: query-term injection](#limitation-query-term-injection).
- **15 of test 5's 21 coref-critical questions have rewrites that add nothing to the gold chunk**,
  so its "critical" subset metrics do not measure what the label claims. Test 4 has 7 such
  questions, test 7 has 4, test 6 has none.
- **Hybrid fusion is inconsistent across tests.** It was the best variant in tests 5, 6 and 7, but
  *worse* than pure `coref_dense` in test 4 (0.9500 vs 0.9833), and it hurt one query in tests 4 and
  5. On the public benchmarks it was clearly harmful (test 2: −0.0329; test 3: −0.0775). Its value
  is corpus-dependent and not established.
- **Paragraph-level RAG with a modern dense model does not need coref-before-embed as a default
  step.** Nothing in tests 2–3 supports adding it, subject to the weak-null caveat above.
- **The positive results all come from one question-authoring process** applied to four single
  Wikipedia articles, with questions written alongside the data. Tests 6 and 7 both say this
  outright in their own caveats sections: "on organic queries the coref-critical fraction — and the
  aggregate gain — would be smaller."

---

## What this repo does not establish

- **No controlled A/B between LingMess and LLM coref.** The two were never run on the same data.
  Tests 1–3 use LingMess on paragraph corpora; tests 4–7 use manual LLM coref on sentence chunks.
  The corpus, chunk size, question source, and coref method all change at once, so the apparent
  "LLM coref is better" conclusion is confounded four ways. The findings files already note this;
  it remains true.
- **No confidence intervals, significance tests, or repeated runs anywhere.** At N=30 (tests 4–7)
  and N=20 (test 1), no reported delta is distinguishable from noise by any stated criterion.
- **A single embedding model.** Tests 2–7 all use `BAAI/bge-small-en-v1.5` — 33M parameters, 384
  dimensions. Whether the effect survives a larger or differently trained retriever is untested.
  (Test 1 used `Qwen3-Embedding-8B`, but on different data, so it is not a comparison.)
- **English only.** All seven tests. Coreference behaves differently in pro-drop and
  morphologically richer languages; nothing here speaks to that.
- **Tests 4–7's coref is not reproducible.** It was performed manually by an LLM in batches, not by
  a script. There is no pipeline in this repo that takes new text and produces the `coref_chunks.json`
  format. You can re-run the *retrieval* on the committed data, but you cannot re-run the *method* on
  your own corpus. Tests 1–3 are reproducible end-to-end because LingMess is a committed code path.
- **No end-task evaluation.** Retrieval metrics only — no answer generation, no LLM-as-judge, no
  measurement of whether better retrieval produced better answers.
- **Test 6's per-query flip data is not committed.** The findings report 3 recovered and 1 hurt but
  do not name the queries, and the notebooks ship with outputs stripped, so test 6 cannot be
  cross-referenced against the injection audit.
- **Tests 4 and 5 do not ship their source text.** Only tests 6 and 7 include the article `.txt` and
  the `fetch_article.py` that produced it. `test-5-findings.md` lists a `world_war2_wikipedia.txt`
  that is not in the repository (a correction note has been added to that file), so tests 4 and 5
  begin at the chunk JSON — their chunking cannot be re-derived from source.

---

## What's in this repo

| Path | What it does |
|------|--------------|
| `test-1/coref_rag_benchmark.ipynb` | **Test 1** — stress test on one Wikipedia article, 20 pronoun-targeted generated questions. Automated coref +0.050 R@5. |
| `test-2/coref_public_eval.ipynb` | **Test 2** — DAPR ConditionalQA, official qrels. Automated coref flat. |
| `test-3/coref_public_eval_v3.ipynb` | **Test 3** — DAPR NaturalQuestions + selective coref. Still flat. |
| `test-4/coref_public_eval_v4.ipynb` | **Test 4** — manual LLM coref, sentence chunks, Apollo 11. +0.1667 R@5. |
| `test-5/coref_public_eval_v5.ipynb` | **Test 5** — manual LLM coref, sentence chunks, WWII (414 chunks). Dense flat. |
| `test-6/coref_public_eval_v6.ipynb` | **Test 6** — manual chunking + manual coref, French Revolution. +0.0667 dense, +0.1000 hybrid. |
| `test-7/coref_public_eval_v7.ipynb` | **Test 7** — manual chunking + manual coref, American Civil War. +0.1000 dense, +0.1333 hybrid. |
| `coref-rag-hypothesis-and-findings.md` | Research write-up: hypothesis and synthesis. **Covers tests 1–5 only.** |
| `test-*/test-*-findings.md` | Per-test detailed results |

---

## Quick start

**Tests 4–7** need no GPU, no API key, and no dataset download — the chunks and questions are
committed:

```bash
pip install -r requirements.txt
```

Then run `test-N/coref_public_eval_vN.ipynb` top-to-bottom. Tests 6 and 7 also ship the source
article text and the `fetch_article.py` that produced it.

**Tests 1–3** were run on a Kaggle free T4 GPU:

1. Upload the notebook to a Kaggle notebook with a GPU T4 accelerator.
2. Run the **install cell**, then **restart the kernel** — one-time, required because `fastcoref`
   needs `transformers<5`.
3. Run all remaining cells. Results print inline and a findings `.md` is written.

Test 1 additionally needs a DeepInfra API key (question generation and embeddings).

---

## How it works

```
Original passage:  "He won the Nobel Prize in 1921."
                        ↓ coreference resolution (LingMess, or manual LLM)
Coref rewrite:     "Albert Einstein won the Nobel Prize in 1921."
                        ↓ embed the rewrite (but return the original to the user)
Dense vector:      now captures "Albert Einstein" for query matching
```

**Three retrieval variants (tests 2–7):**
- `baseline` — embed the original text as-is
- `coref_dense` — embed the coref-rewritten text
- `coref_hybrid` — fuse BM25(original) + dense(coref) via reciprocal rank fusion
  (equal weight in test 2; weighted 0.7 dense / 0.3 BM25 in tests 3–7)

**Invariant across all variants:** the original text is what gets returned to the user. Only the
embedded text changes. Chunk IDs are 1:1 between the original and coref versions — verified for
tests 4–7 against the committed JSON.

---

## What the tests suggest, stated conservatively

**Sentence-level chunking does create pronoun-only chunks, and they are harder to retrieve.**
Baseline R@5 on the coref-critical subset was 0.7727 (test 4), 0.9048 (test 5), 0.8636 (test 6),
0.7727 (test 7) — below the overall baseline in every case except test 5. The mechanism is visible
in the data.

**Whether resolving them helps depends on headroom, and the evidence is compromised by injection.**
Test 5 had the highest critical baseline (0.9048) and gained nothing. Tests 4 and 7 had the lowest
(0.7727) and gained the most. But tests 4 and 7 are also the two most affected by query-term
injection, so headroom and injection are confounded in this data — the repo cannot separate them.

**Automated coref did not reproduce any of this.** LingMess reduced pronouns by 77–89% on the DAPR
corpora and moved retrieval by −0.0015 and −0.0142. Test 2's findings identify the reason on that
corpus: its coreference chains resolve to common nouns ("mobility aids", "your home"), which add no
discriminative term. Test 3 tested the entity-rich case with selective proper-noun-only coref and
still saw nothing.

**If you are considering this technique:** measure your own baseline R@5 on the queries you think
are coref-critical before doing anything else. Test 5 entered at a critical baseline of 0.9048 and
gained nothing from dense coref; tests 4 and 7 entered at 0.7727 and gained the most. That is a
four-point pattern, not a threshold — but it is the only guidance this data supports. And write
your evaluation questions *before* you look at the coref rewrites, which is the control this repo
lacks.

---

## Tech stack

| Component | Choice |
|-----------|--------|
| Embedding | `BAAI/bge-small-en-v1.5` (tests 2–7, 33M params, 384-d) / `Qwen3-Embedding-8B` (test 1) |
| Coreference | `fastcoref` LingMessCoref (tests 1–3, local GPU) / manual LLM, unscripted (tests 4–7) |
| Lexical | `rank_bm25` (BM25 Okapi) |
| Metrics | `pytrec_eval` (Recall@5, nDCG@10, MRR) |
| Datasets | DAPR (`UKPLab/dapr`), Wikipedia article excerpts |
| Runtime | Kaggle free T4 GPU; tests 4–7 run on CPU from committed JSON |

---

## Repo structure

```
coref-rag-eval/
├── README.md                              ← you are here
├── LICENSE
├── requirements.txt
├── coref-rag-hypothesis-and-findings.md   ← research write-up (tests 1–5 only)
├── test-1/
│   ├── coref_rag_benchmark.ipynb
│   └── test-1-findings.md
├── test-2/
│   ├── coref_public_eval.ipynb
│   └── test-2-findings.md
├── test-3/
│   ├── coref_public_eval_v3.ipynb
│   └── test-3-findings.md
├── test-4/
│   ├── coref_public_eval_v4.ipynb
│   ├── test-4-data/                       ← Apollo 11 chunks + eval questions
│   └── test-4-findings.md
├── test-5/
│   ├── coref_public_eval_v5.ipynb
│   ├── test-5-data/                       ← WWII chunks + eval questions
│   └── test-5-findings.md
├── test-6/
│   ├── coref_public_eval_v6.ipynb
│   ├── fetch_article.py
│   ├── test-6-data/                       ← French Revolution .txt + chunks + questions
│   └── test-6-findings.md
└── test-7/
    ├── coref_public_eval_v7.ipynb
    ├── fetch_article.py
    ├── test-7-data/                       ← American Civil War .txt + chunks + questions
    └── test-7-findings.md
```

---

## License & citation

Code and documentation: MIT, see [LICENSE](LICENSE). The datasets the notebooks download (DAPR,
Wikipedia) carry their own licenses.

If referencing this work:

> Coreference-aware RAG ingestion: a seven-test proof-of-concept. On two public DAPR benchmarks
> with external qrels, resolving coreference before embedding produced no measurable gain in
> Recall@5 (−0.0015, −0.0142), though on subsampled corpora with high baselines. On four
> constructed sentence-level evaluations over single Wikipedia articles, LLM-quality coref improved
> Recall@5 by 0.000 to +0.167 (N=30 each), but an audit of those evaluations found that in 2–16 of
> the 21–22 coref-critical questions per test the rewrite inserted a term the query already
> contained, so those gains cannot be separated from a lexical term match.
