# Test 8 — Replication and Extension of Jang et al. (2025) on full BEIR

**Run date:** 2026-09-11 — completed, 4.18 h on a Kaggle T4 × 2, resumed across two pushes
**Notebook:** `coref_public_eval_v8.ipynb` (self-contained; everything runs on Kaggle)
**Data folder:** `test-8-data/` — created by the notebook, copied back from `/kaggle/working/`
**Paper:** Jang, Y., Hong, S., Son, J., Park, S., Park, C., Lim, H. (2025). *From Ambiguity to
Accuracy: The Transformative Effect of Coreference Resolution on Retrieval-Augmented Generation
systems.* [arXiv:2507.07847](https://arxiv.org/abs/2507.07847) v3. Korea University + NAVER.

> **Status.** Run complete. All four encoders finished, no sanity-floor failures, no out-of-memory
> events, no deadline stop. Every number below comes from that run; nothing here was written before
> it existed. Full tables are in `test-8-data/test-8-results.md`, the raw per-query rows in
> `per_query_results.jsonl.gz` (14,952 records, gzipped for the repo — `gunzip` to use).
>
> **The notebook is built to be pushed as a Kaggle batch job and left alone**: no kernel restart, no
> cell that waits for a human, a session budget that stops it cleanly inside Kaggle's 12h ceiling,
> and a `RESULTS.md` / `run_summary.json` pair written at the end saying what ran and what did not.

---

## Hypothesis

The paper makes two claims this repo is positioned to test:

1. **Coreference resolution consistently improves dense retrieval.**
2. **Mean pooling gains more than CLS or last-token pooling**, because mean pooling weights all
   tokens equally, so replacing a pronoun with a name adds real semantic content.

Their effects are small: overall nDCG moves +0.001 to +0.006, `bge-large-en-v1.5` (CLS) shows
0.789 → 0.789, and several cells decrease. **They report no confidence intervals.**

Tests 2–3 in this repo already found a flat result with `bge-small-en-v1.5`, which is **CLS
pooling** — the same pooling as the one cell where the paper itself measures exactly zero change. So
this repo's null is not in conflict with their paper; it is consistent with their weakest cell, and
the configuration their mechanism predicts should work was never tested here.

---

## What test 8 adds

| # | Contribution | Why it is missing today |
|---|---|---|
| 1 | **Pooling as a variable** | Tests 1–7 are CLS-only, so the paper's mechanism was never exercised |
| 2 | **Stratification** | The paper averages over all queries; coref can only help a query whose gold passage hides an entity the query names |
| 3 | **Bootstrap confidence intervals** | Neither the paper nor this repo has any, anywhere |
| 4 | **Controlled LingMess vs LLM coref** | The README lists this as an open gap: never run on the same data |

---

## Benchmark: full BEIR `scifact` + `nfcorpus`

| | scifact | nfcorpus |
|---|---|---|
| corpus | 5,183 | 3,633 |
| test queries | ~300 | ~323 |
| gold per query | ~1.1 | ~38 |
| relevance | binary | **graded 0/1/2** |
| role | carries the **stratified** arm | carries the **aggregate** arm |

**Why these two.** They are the only full-BEIR sets small enough to LLM-coref end to end on a free
T4. The next step up, `scidocs`, is 25,657 passages; `nq` is 2.68M. Together they give **8,816
passages and ~623 queries** — 12× the query count of a NanoBEIR run, which is what makes the
confidence intervals worth computing at all.

### Three data hazards handled explicitly

1. **`scifact` qrels use `int64` ids while its corpus `_id` is a string.** A naive join matches
   nothing. All ids are cast with `str()` on both sides, and Stage 1 asserts every gold id resolves.
2. **`nfcorpus` relevance is graded 0/1/2; `scifact` is binary.** Flattening grades to 1 would
   quietly mis-measure nDCG. Grades are preserved and passed to `pytrec_eval` as-is; "gold" means
   `score > 0`.
3. **Both corpora are `title` + `text`.** BEIR convention concatenates them, and that concatenated
   string is what gets coref-resolved and embedded.

---

## Design

| Axis | Levels |
|------|--------|
| Coref variant | `original`, `lingmess` (fastcoref), `llm` (**Qwen2.5-3B-Instruct, fp16**, greedy, the paper's Table 5 prompt) |
| Embedding model | `BAAI/bge-small-en-v1.5` (**CLS**), `intfloat/e5-small-v2` (**mean**) |
| Retrieval | `dense`, and `coref_hybrid` = weighted RRF (0.7 dense on the variant + 0.3 BM25 on the original) |
| Metrics | nDCG@1, @3, @5 + Recall@5, MRR, via `pytrec_eval` with graded qrels |
| CIs | Bootstrap over queries, 1,000 iterations, seed 42, shared resample matrix within each stratum |
| Reporting | **Per dataset and pooled** |

Both embedding models are 33M parameters / 384 dimensions, so **pooling is the variable, not
capacity**. Each model's documented prefixes are applied.

Pooling across datasets concatenates per-query metric vectors and bootstraps over all ~623 queries,
which weights datasets by query count. That is a real interpretive choice and is stated in the
notebook rather than presented as neutral.

**Coref is applied to the entire corpus, never only to gold passages.** Stages 2 and 3 both assert
gold and non-gold counts against the full corpus. This repo already documents a query-term-injection
problem caused by treating gold text differently from the rest; the corpus-level version of that
mistake would invalidate the whole comparison.

### Which configuration of the paper this replicates

The paper used `gpt-4o-mini` for its headline table and `Qwen2.5-7B-Instruct` as a cheaper
alternative in **Appendix B**. Test 8 follows **Appendix B** — with one substitution: it runs
**`Qwen2.5-3B-Instruct`**, the same family and the same Table 5 prompt, scaled down so the whole
corpus fits one free-tier session. That is a replication of their *method*, not of their exact
configuration, and Stage 0 is what makes it defensible: it measures the 3B model's hallucination
rate and exact-match against test-6's hand-written gold **before** the expensive stage runs.
Appendix B matters because there the pooling contrast is *sharper* than in their headline:

| Model | Pooling | Original | + CR (gpt-4o-mini) | + CR (Qwen2.5-7B) |
|-------|---------|----------|--------------------|-------------------|
| `stella_en_400M_v5` | Mean | 0.796 | 0.798 | **0.812** |
| `bge-large-en-v1.5` | CLS | 0.789 | 0.789 | **0.788** |
| `LLM2Vec` | Mean | 0.822 | 0.828 | 0.825 |
| `Linq-Embed-Mistral` | Last | 0.823 | 0.826 | 0.826 |

_(OVR column, their Tables 1 and 4.)_

---

## The stratification rule

> For each query, check whether any gold passage lacks a content word present in the query, and
> whether the coref rewrite adds it. Those queries are `coref_critical`.

Computed in two halves, because the second depends on a rewrite that does not exist yet in Stage 1
and differs between variants:

* **Stage 1, variant-independent:** a query is `coref_eligible` when some gold passage is missing
  ≥1 query content word **that no other gold passage for that query supplies**, and that gold
  passage contains a pronoun.
* **Stage 2 gate and Stage 4, per variant:** `coref_critical` = eligible **and** that variant's
  rewrite actually supplies one of those missing words.

**Sibling-gold exclusion is part of the rule.** A missing term supplied by another gold passage for
the same query is not a coreference failure — retrieval can still succeed through that sibling.

On `scifact` (~1.1 gold/query) the exclusion barely bites. On `nfcorpus` (~38 gold/query) it is
severe, and that stratum is expected to come out near zero. **That is the rule working as specified,
not a bug.** The notebook prints eligible counts **with and without** the exclusion so the effect
stays visible and auditable.

Content words use the tokenisation this repo's committed injection audit already documents:
lowercase, drop stopwords and tokens of ≤2 characters, keep hyphenated identifiers whole.

---

## Predictions registered before the run

**1. The paper's own data predicts a null here.** Their only true IR benchmark is NanoSCIDOCS, and
on it both their *encoder* models go flat-or-down at @3/@5:

| Model | Pooling | nDCG@1 | nDCG@3 | nDCG@5 |
|-------|---------|--------|--------|--------|
| `e5-large-v2` | Mean | 0.520 → 0.520 | 0.404 → **0.400** | 0.359 → **0.352** |
| `bge-large-en-v1.5` | CLS | 0.480 → 0.480 | 0.395 → **0.382** | 0.364 → **0.359** |
| `gte-modernbert-base` | CLS | 0.520 → 0.520 | 0.452 → **0.448** | 0.410 → **0.391** |

Their positive averages come from BELEBELE / SQuAD2.0 / BoolQ — QA sets adapted into retrieval, not
IR benchmarks. Test 8 runs two small **encoders** on scientific IR data.

**2. The pronoun-density risk.** Scientific abstracts use far fewer pronouns than Wikipedia. If
pronoun density is low, coref has little to change and any null is **by construction rather than a
finding**. Stage 1 measures and prints `corpus_pronoun_share` per dataset **before** the expensive
stage, and it is carried into the results header for exactly this reason.

---

## Verification built into the notebook

Every check **raises and halts**, with two deliberate exceptions noted below. Nothing warns and
continues. Each logs a `CHECK PASS` / `CHECK FAIL` line, and the full list ships in
`stage4_results.json`.

- **Stage 0 (gate):** the coref model with the paper's prompt over test-6's committed chunks,
  fetched from a pinned commit with SHA-256 asserts. Reports exact-match rate and hallucinated
  antecedents. Interactively it halts for review; in a batch job it decides from declared
  thresholds (`STAGE0_MAX_HALLUC_RATE`, `STAGE0_MAX_FAIL_RATE`, `STAGE0_MIN_CHANGED`), prints the
  decision, and halts if any is breached. It also decides the Stage 3 anaphor skip, by measuring
  whether this model alters pronoun-free chunks at all.
- **Stage 1:** corpus size matches the published BEIR size; ids unique; no empty text; every gold
  id resolves; query set fixed and SHA'd; stratification and pronoun density printed. The eligible
  count is an upper bound and is **reported, not gated on**.
- **Stages 2 and 3:** output length equals input length; every `chunk_id` preserved and order
  matched; no duplicates; original text unmodified; gold and non-gold counts asserted against the
  full corpus; passages changed, pronoun before/after, mean length change; every rewrite adding a
  proper noun absent from its source is flagged; both stages asserted to emit an identical schema.
- **Stratum, after Stage 2 (exception 1 — records, does not halt):** the confirmed critical count is
  computed from the cheap LingMess rewrites **before** committing hours to the LLM stage. A thin
  stratum is a finding about the benchmark, not an error in the run, and the aggregate arm does not
  depend on it, so the number is recorded and the run continues. The analysis refuses to *fit* a
  scope below `MIN_FIT`, which is where the real protection lives.
- **Sanity floor in Stage 4 (exception 2 — quarantines, does not halt):** a model below its floor on
  the ORIGINAL corpus is misconfigured, and every coref delta on top of it would be noise. Its rows
  are still written, flagged `floor_pass=false`, and **excluded from every table** by the analysis,
  which names it. Halting here would discard every model that had not run yet in order to punish
  one that was misconfigured.
- **Stage 4:** all variants asserted to identical passage counts and ids; embeddings asserted finite
  with no all-zero vectors; query set asserted unchanged via SHA; **bootstrap resample matrices
  asserted to match their stratum size** (a mismatched matrix would give a biased CI); per-variant
  wall-clock, peak GPU memory and seed logged.

Package versions are read from the actual Kaggle image and stored with every stage output.

---

## How to run it

**One push, then walk away.** Kaggle allows no concurrent GPU sessions, so the notebook is a strict
waterfall with checkpoints. Every stage checks whether its output exists: if yes it loads and skips,
if no it computes and saves **atomically**, so a timeout mid-write cannot leave a corrupt file that
later loads as garbage.

1. Confirm the accelerator is **T4 × 2** (Stage 3 runs one Qwen per visible GPU) and that internet
   is enabled.
2. `Save & Run All (Commit)`.
3. When it finishes, open **`RESULTS.md`** in the output. It says what ran, what every gate decided,
   what was skipped or quarantined, what is missing, and how to resume.

There is **no kernel restart** and **no cell that waits for a human**. The install cell pins
`transformers<5` and takes the new version in-process by purging `sys.modules`; if the pin somehow
fails it says so immediately rather than hours later inside LingMess.

`SESSION_BUDGET_H` (default 11.2h) keeps the run inside Kaggle's 12h ceiling. Expensive stages stop
*taking new work* once it is spent, flush their checkpoints, and print a resume banner:

| If it stops in | What you get | To resume |
|---|---|---|
| Stage 3 | every rewritten passage checkpointed | save the output, add it to `kernel-metadata.json` as a `kernel_sources` entry, push again |
| Stage 4 | every completed model's rows, fsynced and analysable | same — the remaining models run next push |

`load_stage()` looks in `/kaggle/working` first and any attached `/kaggle/input/*/test-8-data`
second, so a resumed push inherits the earlier one's checkpoints. **No code changes between
pushes** — only that one metadata line. Nothing is ever recomputed.

---

## Measured Results

### What the two coref arms actually did

| dataset | method | passages changed | pronouns before → after | reduction |
|---|---|---|---|---|
| scifact | LingMess | 2,606 / 5,183 | 5,586 → 1,011 | **81.9%** |
| scifact | LLM (Qwen2.5-3B) | 1,859 / 5,183 | 5,586 → 5,557 | **0.5%** |
| nfcorpus | LingMess | 1,692 / 3,633 | 3,855 → 760 | **80.3%** |
| nfcorpus | LLM (Qwen2.5-3B) | 1,463 / 3,633 | 3,855 → 3,839 | **0.4%** |

The LLM arm rewrote a third of each corpus while resolving almost nothing, and introduced proper
nouns absent from the source in 9.9% / 5.7% of the passages it changed (LingMess: 3.5% / 3.3%).
**It is therefore reported as a text-perturbation comparison, not as a coreference condition.**

### Retrieval: nothing moved

Mean Δ nDCG@10, dense retrieval, all queries, LingMess arm. Every bootstrap CI includes zero:

| model | pooling | scifact | nfcorpus |
|---|---|---|---|
| all-MiniLM-L6-v2 | mean | −0.0069 | +0.0010 |
| e5-small-v2 | mean | −0.0050 | −0.0021 |
| bge-small-en-v1.5 | CLS | −0.0045 | +0.0007 |
| Qwen3-Embedding-0.6B | last | +0.0009 | +0.0017 |

- **32 paired Wilcoxon tests. 2 reach raw p<0.05 (1.6 expected by chance). 0 survive Bonferroni or
  Benjamini-Hochberg.** Both nominal hits are negative.
- Best cell anywhere in the grid: **+0.0024** (Qwen3 / scifact / llm / pronoun scope), p = 0.24.
- Largest single-query swing: **+0.613** nDCG@10. scifact carries ~1.13 gold passages per query, so
  one document crossing rank 10 dominates that query's score.

### Confirmed coref-critical stratum: 0 of 623

Zero **by construction**, not by accident. LingMess is extractive — every string it inserts is copied
from elsewhere in the same passage — so the passage's content-word set cannot grow, and a query term
the gold passage lacked can never be supplied.

### BM25 fusion versus coreference, same corpora and models

| addition to the dense baseline | mean Δ nDCG@10 | cells won |
|---|---|---|
| BM25 fusion | **+0.0137** | 7 of 8 |
| LingMess coreference | **−0.0018** | 1 of 8 |

### Encoders disagree about which queries move

| | moved by ≥1 encoder | moved by all 4 | all 4 agree on sign |
|---|---|---|---|
| scifact / lingmess | 82 | **0** | 0 |
| nfcorpus / lingmess | 183 | 13 | 3 (chance ≈ 1.6) |

### The pooling claim

Mean-pooling models −0.0060 vs CLS/last-token −0.0018 on scifact (Mann-Whitney p = 0.60);
−0.0006 vs +0.0012 on nfcorpus (p = 0.26). No gradient, and mean pooling is nominally the worst of
the three — the opposite of the predicted direction, though not significantly so.

---

## Interpretation

The reading was fixed in advance, before any numbers existed. Matching the run against it:

- **Effect only in the stratified subset** → **not applicable.** The confirmed stratum is 0 of 623,
  by construction for an extractive system. The stratified arm cannot be run at all, which is itself
  the finding.
- **Mean pooling gains, CLS does not** → **not supported.** No pooling gradient appeared; mean
  pooling is nominally the worst of the three.
- **Both flat, stratified included** → **this is the result.** Coreference before embedding does not
  help dense retrieval on these two benchmarks, under any of the three pooling strategies. Not
  softened.
- **CIs overlap everywhere** → **yes.** The power table puts N-for-80%-power between 231 and
  414,569 against the 623 queries available.
- **Slope near −1 in the delta-vs-baseline regression** → **no.** Slopes run −0.004 to −0.030 with
  |r| ≤ 0.14. This is not regression to the mean; it is flat.
- **A low `corpus_pronoun_share` would make the null a property of scientific prose** → **retired.**
  56% of scifact passages and 53% of nfcorpus passages contain a pronoun. The null is not an
  artefact of pronoun-scarce text.

Two findings the registered list did not anticipate:

1. **Where this repo found a gain, it tracks query-term injection rather than coreference.** Across
   tests 4–8 the share of coref-critical questions whose rewrite inserted a word the query itself
   used predicts the outcome at ρ = 0.87. Pronoun reduction predicts nothing: it sat between 77% and
   90% in every test, while outcomes ranged from −0.014 to +0.167. A near-constant cannot explain a
   varying result.
2. **A rewriter that did not resolve pronouns performed the same as one that did.** The 3B arm (0.5%
   reduction) and LingMess (81.9% / 80.3%) are statistically indistinguishable in 7 of 8
   model × dataset cells. This was an accident of the model substitution rather than a designed
   control — but it is precisely the control the question needs, and no published work on this
   technique appears to run one.

---

## Caveats and honest scope

- **Scientific prose is a hard case for this mechanism.** Both datasets are abstracts. If
  `corpus_pronoun_share` comes back low, a null says more about the corpus than about coreference,
  and the findings will say so.
- **`nfcorpus`'s stratified arm is expected to be near-empty** because of ~38 gold passages per
  query combined with the sibling-gold exclusion. Structural, not a defect.
- **Pooling weights datasets by query count** (~300 vs ~323, so roughly even here, but it is still a
  choice).
- **This follows the paper's Appendix B configuration**, not its headline (gpt-4o-mini) — and not
  even Appendix B exactly: the coref model is **`Qwen2.5-3B-Instruct`, not the 7B they used**,
  scaled down to fit a free-tier session. One model rewrote the entire corpus, so no comparison
  inside this notebook is confounded, but absolute coref quality is not comparable to theirs.
  Stage 0 measures what the substituted model actually does, and the run halts if it misbehaves.
- **`google/embeddinggemma-300m` was dropped for GPU cost.** The paper's own claim survives intact
  — mean (MiniLM, e5) vs CLS (bge) vs last-token (Qwen3) are all still measured — but the
  mean-pooling ladder now spans 2021 → 2022 only, so this repo's second hypothesis (newer encoders
  gain less from coreference) is **registered but not answered** in this run. The analysis prints
  that rather than reporting a two-rung ladder as if it settled the question.
- **Pronoun-free passages may skip the LLM.** The Table 5 prompt resolves anaphora, so a passage
  with no pronoun has nothing to resolve. Stage 3 keeps such passages verbatim — but only if
  Stage 0 first shows this model changed *zero* pronoun-free reference chunks. Otherwise the skip
  stays off. The skipped count is reported in the Stage 3 stats either way.
- **The paper's prompt is verbatim** (`coref_prompt.py`, fingerprint `dabdeb94b7e6`), but Table 5
  specifies no role split and no decoding parameters. Sending it as a single user turn and decoding
  greedily are our choices, recorded in every stage output.
- **Retrieval metrics only.** No answer generation, no end-task evaluation — the same limit tests
  2–7 have.
