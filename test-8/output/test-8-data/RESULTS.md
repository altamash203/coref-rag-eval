# Test 8 - run summary

- mode: **BATCH (unattended)**
- elapsed: **4.18 h** of a 11.2 h budget
- status: **COMPLETE**

## What produced the coreference

- LLM: `Qwen/Qwen2.5-3B-Instruct` (fp16)
- **Departure from the paper.** Jang et al. Appendix B use `Qwen/Qwen2.5-7B-Instruct`. This run used a smaller model of the same family with the same Table 5 prompt, to fit a free-tier session. Stage 0 measured its coref behaviour before Stage 3 spent anything; those numbers are below. This is a replication of the METHOD, not of their exact configuration.
- Anaphor skip requested but **NOT active**: 27 of 115 pronoun-free reference chunks were changed by this model, so every passage went to the LLM.

## Gates

- Stage 0 (batch-auto): changed 63, failure rate 0.0, hallucination rate 0.0635 -> PASS
- Stratum: 0 confirmed vs threshold 10 -> UNDERPOWERED (recorded as a finding, run continued)

## Stage 4 roster

- completed: all-MiniLM-L6-v2, bge-small-en-v1.5, e5-small-v2, Qwen3-Embedding-0.6B
- no sanity-floor failures

## Coreference stats per dataset

- `scifact`: lingmess changed 2606 (pronouns -81.9%), llm changed 1859 (pronouns -0.5%)
- `nfcorpus`: lingmess changed 1692 (pronouns -80.3%), llm changed 1463 (pronouns -0.4%)

## Known limitations of THIS run

- `google/embeddinggemma-300m` was dropped for GPU cost. The mean-pooling ladder therefore spans 2021 -> 2022 only, and the registered hypothesis that newer encoders gain less from coreference is **registered but not answered**. The paper's own pooling claim (mean vs CLS vs last-token) is unaffected and fully tested.
- The coreference model is smaller than the paper's. Absolute coref quality is therefore not comparable to theirs; the within-notebook A/B (none vs LingMess vs LLM) is unaffected because one model rewrote the entire corpus.
- The confirmed coref-critical stratum is thin, so the stratified arm is a diagnostic only. The aggregate arm is the paper's own condition and does not depend on it.

## Artifacts

`test-8-results.md` carries every table and plot. `per_query_results.jsonl` is the durable raw artifact - it holds each query's top-50 doc ids, so any other metric can be recomputed on a CPU without re-running a GPU stage.
