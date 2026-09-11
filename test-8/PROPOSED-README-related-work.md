# Proposed addition to the root `README.md` — **not applied**

You asked me to propose README edits and not apply them. This is the proposal. It is one new
section plus one small cross-reference.

The repo currently cites nothing, which is a real gap: two published papers work on exactly this
problem, and one of them (Jang et al.) reaches a *different* conclusion from tests 2–3, which a
reader deserves to see acknowledged rather than discovered elsewhere.

---

## Where to put it

Insert the section below **between** `## What this repo does not establish` and
`## What's in this repo`. That placement matters: the limitations section is where a reader is
already asking "so has anyone else done this properly?", and the answer should be immediately
adjacent rather than buried at the end.

One additional one-line change, in the `## What's in this repo` table, add a row:

```markdown
| `test-8/coref_public_eval_v8.ipynb` | **Test 8** — partial replication of Jang et al. (2025): pooling as a variable, stratification, bootstrap CIs, controlled LingMess vs LLM coref. |
```

---

## The proposed section, verbatim

```markdown
## Related work

Two published papers address coreference in retrieval directly. Neither was cited in earlier
versions of this README, and one of them reaches a different conclusion from tests 2–3.

### Jang et al. (2025) — coreference resolution before embedding

> Jang, Y., Hong, S., Son, J., Park, S., Park, C., & Lim, H. (2025). *From Ambiguity to Accuracy:
> The Transformative Effect of Coreference Resolution on Retrieval-Augmented Generation systems.*
> [arXiv:2507.07847](https://arxiv.org/abs/2507.07847). Korea University + NAVER.

This is the closest published work to what this repo tests, and it reports the **opposite sign** to
tests 2–3. They resolve coreference with `gpt-4o-mini` (and `Qwen2.5-7B-Instruct` in Appendix B),
re-embed, and evaluate nDCG@1/3/5 over BELEBELE, SQuAD2.0, BoolQ and NanoSCIDOCS across eight
embedding models. Their two claims are that coref consistently improves dense retrieval, and that
**mean pooling benefits more than CLS or last-token pooling**, because mean pooling weights all
tokens equally so a pronoun→name substitution adds real semantic content.

Three things are worth stating precisely, because the headline claim is easy to over-read:

- **The effects are small.** Overall nDCG moves +0.001 to +0.006. `bge-large-en-v1.5` (CLS pooling)
  goes 0.789 → 0.789 — no change at all — and several individual cells decrease.
- **They report no confidence intervals**, significance tests, or repeated runs. Neither does this
  repo, which is why test 8 adds them.
- **Their only true IR benchmark is NanoSCIDOCS, and their encoder models go flat-or-down on it**
  (`bge-large` nDCG@5 0.364 → 0.359; `e5-large-v2` 0.359 → 0.352). The positive averages are carried
  by BELEBELE, SQuAD2.0 and BoolQ, which are QA datasets adapted into retrieval rather than
  retrieval benchmarks.

**Why this matters for tests 2–3.** Every test in this repo before test 8 used
`bge-small-en-v1.5`, which is **CLS pooling** — the same pooling as the one cell where Jang et al.
themselves measure exactly zero change. So this repo's flat result is not in conflict with their
paper; it is consistent with their weakest cell, and the repo simply never tested the configuration
their mechanism predicts should work. Test 8 exists to close that gap.

### Xu, Xu & Yuan (2025) — CLAP

> Xu, H., Xu, L., & Yuan, L. (2025). *CLAP: Coreference-Linked Augmentation for Passage Retrieval.*
> [arXiv:2508.06941](https://arxiv.org/abs/2508.06941). CIKM 2025.

CLAP uses coreference as one component of a larger passage-expansion pipeline: it segments passages
into coherent chunks, resolves coreference chains, and generates localised pseudo-queries aligned
with the dense retriever's representation space. It reports gains up to +20.68 absolute nDCG@10,
with the largest improvements out of domain.

**The comparison is not like-for-like, and the difference is the interesting part.** CLAP's gains
come from *pseudo-query generation* aligned to the retriever, with coreference acting as a
preprocessing step that makes those generated queries coherent. This repo (and Jang et al.) test
coreference *alone*, with nothing added to the passage but the resolved entity names. The gap
between +20.68 nDCG@10 and Jang et al.'s +0.001 to +0.006 is a reasonable indication that on this
problem the query generation, not the coreference, is doing most of the work.
```

---

## Two notes on the wording above

1. **I did not soften tests 2–3.** The section says the repo's null is *consistent with* the paper's
   weakest cell — which is a factual statement about pooling — and does not claim tests 2–3 were
   wrong. The existing weak-null caveat elsewhere in the README still stands on its own.

2. **The CLAP paragraph makes a claim I can support but have not measured**: that query generation
   rather than coreference drives CLAP's gain. It is phrased as "a reasonable indication", not a
   finding. If you would rather this repo assert nothing it has not measured, cut the final sentence
   and end the paragraph at "…out of domain." I would keep it, because the size gap between the two
   papers is the single most useful orienting fact for a reader deciding whether coref alone is
   worth their time.
