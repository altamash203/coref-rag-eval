# Test 1 — Coref RAG Benchmark Findings

**Run date:** 2026-07-01  
**Notebook:** `coref_rag_benchmark.ipynb`  
**Question under test:** Does resolving coreference before chunking improve retrieval on pronoun-dependent queries?

---

## Setup (summary)

| Component | Choice |
|-----------|--------|
| Coref engine | `fastcoref` LingMessCoref (local) |
| Q-gen | `deepseek-ai/DeepSeek-V4-Flash` (DeepInfra) |
| Embeddings | `Qwen/Qwen3-Embedding-8B` (DeepInfra) |
| Eval metric | Recall@5, MRR |
| Query scope | Pronoun-dependent questions only (stress test, not general RAG) |

**Variants compared**

| Variant | Coref strategy | What gets embedded |
|---------|----------------|-------------------|
| **V0 – Baseline** | None | Original text |
| **V1 – Full rewrite** | LingMess resolves all mentions | Fully rewritten text |

Chunk boundaries are identical across variants. Retrieval always returns **original** chunk text; only the indexed embedding text differs.

---

## Headline results

| Variant | n_chunks | Recall@5 | MRR | Δ Recall vs V0 |
|---------|----------|----------|-----|----------------|
| V0_baseline | 117 | **0.50** | 0.285 | — |
| V1_full_coref | 117 | **0.55** | 0.342 | **+0.05** |

- **V0 baseline:** Recall@5 = 0.500 (10/20)
- **V1 full coref:** Recall@5 = 0.550 (11/20)

Coref resolution before indexing yielded a modest improvement on this run: **+5 pp Recall@5** and **+0.057 MRR**.

---

## Per-question flip analysis

| Outcome | Count |
|---------|-------|
| Recovered by coref (V0 miss → V1 hit) | 2 |
| Hurt by coref (V0 hit → V1 miss) | 1 |
| Both fail | 8 |
| Both hit (implied) | 9 |

Net: **+1 question** recovered vs baseline (11 hits vs 10), consistent with the aggregate metrics.

### Recovered by coref (+2)

1. *What did French write about in his work on altruism?*
2. *What did Marcel Mauss's write about in his work on altruism?*

### Hurt by coref (−1)

1. *What is Whether usually contrasted with in the context of altruism?*

---

## Worked example — Marcel Mauss recovery

**Question:** What did Marcel Mauss's write about in his work on altruism?

### Returned to user (original text — both variants)

> In it, he writes:
>
> Evolutionary explanations
>
> In the Science of ethology (the study of animal behaviour), and more generally in the study of social evolution, altruism refers to behavior by an individual that increases the fitness of another individual while decreasing the fitness of the actor.

### Embedded text — V0 baseline

Same as returned text. Pronouns remain unresolved in the index:

> In it, **he** writes: …

**Pronoun count in embed text:** 2

### Embedded text — V1 full coref

LingMess rewrites the pronoun reference to the entity name:

> In This note, **Marcel Mauss's** writes: …

**Pronoun count in embed text:** 0

### Interpretation

The query names **Marcel Mauss** explicitly. The gold chunk originally refers to him only as *"he"*. V0’s embedding shares little lexical overlap with the query entity name, hurting dense retrieval. V1’s rewrite injects *"Marcel Mauss"* into the embedded text, aligning query and index semantics — a direct win for the benchmark’s pronoun-dependent design.

---

## Observations

1. **Coref helps on the intended case.** The Marcel Mauss example is exactly the failure mode this benchmark targets: entity named in the query, pronoun-only reference in the passage.

2. **Gains are small and noisy at N=20.** +5 pp Recall@5 with 2 recoveries and 1 regression on 20 questions is directionally positive but not statistically strong.

3. **Coref is not uniformly beneficial.** One question flipped from hit to miss (*"Whether usually contrasted with…"* — likely a noisy q-gen phrasing or a bad LingMess rewrite). Automatic coref can introduce errors that hurt retrieval.

4. **Large shared failure set.** 8/20 questions fail under both variants — retrieval limits, q-gen quality, or chunks that remain hard even after rewrite.

5. **Q-gen note.** The Marcel Mauss question text contains a typo (*"Mauss's write"*) and the V1 rewrite shows *"In This note, Marcel Mauss's writes"* — minor coref/grammar artifacts that did not prevent recovery on this instance.

---

## Log excerpt (evaluation phase)

```
15:23:56 | INFO | [V0_baseline] Recall@5=0.500 MRR=0.285 (10/20)
15:24:02 | INFO | [V1_full_coref] Recall@5=0.550 MRR=0.342 (11/20)
```

(Embedding API calls to DeepInfra completed successfully prior to each variant evaluation.)

---

## Conclusion (Test 1)

Resolving coreference with LingMess **before** embedding improved pronoun-dependent retrieval on this Wikipedia altruism document: **Recall@5 0.50 → 0.55**, with a clear mechanistic example (Marcel Mauss / *he* → entity name in index). The effect size is modest; a larger question set and additional documents would be needed to confirm the trend and quantify regression risk from coref errors.
