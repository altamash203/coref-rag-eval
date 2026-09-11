## Measured Results (auto-generated from `per_query_results.jsonl`)

Source: `/kaggle/working/test-8-data/per_query_results.jsonl` (14,952 raw per-query rows).
Primary metric: **ndcg_10**, dense retrieval. Bootstrap: **10,000** query resamples,
seed **42**. **Per dataset only — nothing is pooled across scifact and nfcorpus.**

Models present: all-MiniLM-L6-v2, bge-small-en-v1.5, e5-small-v2, Qwen3-Embedding-0.6B
Datasets present: scifact, nfcorpus | coref methods: lingmess, llm
No model fell below its sanity floor.

Every result appears twice: the **confirmed stratum** (upper bound) and the
**confirmed + `gold_has_pronoun`** subset (the coreference claim).

### Absolute scores

| model | pooling | dataset | retrieval | condition | N | ndcg_10 | recall_10 | mrr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | mean | scifact | dense | baseline | 300 | 0.6553 | 0.8081 | 0.613 |
| all-MiniLM-L6-v2 | mean | scifact | dense | coref:lingmess | 300 | 0.6484 | 0.8064 | 0.6056 |
| all-MiniLM-L6-v2 | mean | scifact | dense | coref:llm | 300 | 0.6493 | 0.8014 | 0.6086 |
| all-MiniLM-L6-v2 | mean | scifact | hybrid | baseline | 300 | 0.6798 | 0.8316 | 0.6417 |
| all-MiniLM-L6-v2 | mean | scifact | hybrid | coref:lingmess | 300 | 0.6785 | 0.8316 | 0.6409 |
| all-MiniLM-L6-v2 | mean | scifact | hybrid | coref:llm | 300 | 0.681 | 0.8341 | 0.6421 |
| all-MiniLM-L6-v2 | mean | nfcorpus | dense | baseline | 323 | 0.3098 | 0.1532 | 0.5023 |
| all-MiniLM-L6-v2 | mean | nfcorpus | dense | coref:lingmess | 323 | 0.3108 | 0.1542 | 0.5073 |
| all-MiniLM-L6-v2 | mean | nfcorpus | dense | coref:llm | 323 | 0.3094 | 0.1528 | 0.503 |
| all-MiniLM-L6-v2 | mean | nfcorpus | hybrid | baseline | 323 | 0.3301 | 0.1627 | 0.5288 |
| all-MiniLM-L6-v2 | mean | nfcorpus | hybrid | coref:lingmess | 323 | 0.3309 | 0.1612 | 0.535 |
| all-MiniLM-L6-v2 | mean | nfcorpus | hybrid | coref:llm | 323 | 0.331 | 0.1625 | 0.5347 |
| bge-small-en-v1.5 | cls | scifact | dense | baseline | 300 | 0.7127 | 0.8362 | 0.6866 |
| bge-small-en-v1.5 | cls | scifact | dense | coref:lingmess | 300 | 0.7083 | 0.8329 | 0.6827 |
| bge-small-en-v1.5 | cls | scifact | dense | coref:llm | 300 | 0.7112 | 0.8379 | 0.6845 |
| bge-small-en-v1.5 | cls | scifact | hybrid | baseline | 300 | 0.7137 | 0.8407 | 0.6851 |
| bge-small-en-v1.5 | cls | scifact | hybrid | coref:lingmess | 300 | 0.7111 | 0.8324 | 0.6863 |
| bge-small-en-v1.5 | cls | scifact | hybrid | coref:llm | 300 | 0.7147 | 0.8391 | 0.6885 |
| bge-small-en-v1.5 | cls | nfcorpus | dense | baseline | 323 | 0.3431 | 0.162 | 0.5332 |
| bge-small-en-v1.5 | cls | nfcorpus | dense | coref:lingmess | 323 | 0.3437 | 0.1629 | 0.5343 |
| bge-small-en-v1.5 | cls | nfcorpus | dense | coref:llm | 323 | 0.3447 | 0.1623 | 0.533 |
| bge-small-en-v1.5 | cls | nfcorpus | hybrid | baseline | 323 | 0.3517 | 0.1679 | 0.563 |
| bge-small-en-v1.5 | cls | nfcorpus | hybrid | coref:lingmess | 323 | 0.3499 | 0.1681 | 0.5533 |
| bge-small-en-v1.5 | cls | nfcorpus | hybrid | coref:llm | 323 | 0.3516 | 0.1674 | 0.5653 |
| e5-small-v2 | mean | scifact | dense | baseline | 300 | 0.6884 | 0.809 | 0.6636 |
| e5-small-v2 | mean | scifact | dense | coref:lingmess | 300 | 0.6834 | 0.809 | 0.6565 |
| e5-small-v2 | mean | scifact | dense | coref:llm | 300 | 0.6774 | 0.8073 | 0.6491 |
| e5-small-v2 | mean | scifact | hybrid | baseline | 300 | 0.7182 | 0.8241 | 0.6988 |
| e5-small-v2 | mean | scifact | hybrid | coref:lingmess | 300 | 0.7149 | 0.8307 | 0.6919 |
| e5-small-v2 | mean | scifact | hybrid | coref:llm | 300 | 0.7097 | 0.8157 | 0.689 |
| e5-small-v2 | mean | nfcorpus | dense | baseline | 323 | 0.3248 | 0.1598 | 0.527 |
| e5-small-v2 | mean | nfcorpus | dense | coref:lingmess | 323 | 0.3227 | 0.1555 | 0.5277 |
| e5-small-v2 | mean | nfcorpus | dense | coref:llm | 323 | 0.3235 | 0.1597 | 0.5232 |
| e5-small-v2 | mean | nfcorpus | hybrid | baseline | 323 | 0.3332 | 0.1603 | 0.5505 |
| e5-small-v2 | mean | nfcorpus | hybrid | coref:lingmess | 323 | 0.3317 | 0.1597 | 0.5453 |
| e5-small-v2 | mean | nfcorpus | hybrid | coref:llm | 323 | 0.3337 | 0.1599 | 0.5516 |
| Qwen3-Embedding-0.6B | last | scifact | dense | baseline | 300 | 0.7034 | 0.8332 | 0.6725 |
| Qwen3-Embedding-0.6B | last | scifact | dense | coref:lingmess | 300 | 0.7042 | 0.8299 | 0.6747 |
| Qwen3-Embedding-0.6B | last | scifact | dense | coref:llm | 300 | 0.7011 | 0.8332 | 0.6696 |
| Qwen3-Embedding-0.6B | last | scifact | hybrid | baseline | 300 | 0.7195 | 0.8431 | 0.6902 |
| Qwen3-Embedding-0.6B | last | scifact | hybrid | coref:lingmess | 300 | 0.7213 | 0.8447 | 0.692 |
| Qwen3-Embedding-0.6B | last | scifact | hybrid | coref:llm | 300 | 0.7181 | 0.8431 | 0.6884 |
| Qwen3-Embedding-0.6B | last | nfcorpus | dense | baseline | 323 | 0.3599 | 0.1743 | 0.5673 |
| Qwen3-Embedding-0.6B | last | nfcorpus | dense | coref:lingmess | 323 | 0.3617 | 0.1741 | 0.5696 |
| Qwen3-Embedding-0.6B | last | nfcorpus | dense | coref:llm | 323 | 0.3591 | 0.174 | 0.5623 |
| Qwen3-Embedding-0.6B | last | nfcorpus | hybrid | baseline | 323 | 0.3611 | 0.1743 | 0.5723 |
| Qwen3-Embedding-0.6B | last | nfcorpus | hybrid | coref:lingmess | 323 | 0.3607 | 0.1738 | 0.5723 |
| Qwen3-Embedding-0.6B | last | nfcorpus | hybrid | coref:llm | 323 | 0.36 | 0.1735 | 0.5693 |

### Delta vs baseline (OLS slope, Spearman rho, bootstrap 95% CI)

| model | dataset | coref | scope | N | slope | slope 95% CI | spearman rho | rho 95% CI | mean baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | scifact | lingmess | all queries | 300 | -0.0181 | [-0.0337, -0.0044] | -0.0736 | [-0.1662, +0.0265] | 0.6553 |
| all-MiniLM-L6-v2 | scifact | lingmess | gold_has_pronoun | 169 | -0.0325 | [-0.0616, -0.0078] | -0.1061 | [-0.2299, +0.0315] | 0.6615 |
| all-MiniLM-L6-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| all-MiniLM-L6-v2 | scifact | llm | all queries | 300 | -0.019 | [-0.0412, +0.0000] | -0.0667 | [-0.1571, +0.0271] | 0.6553 |
| all-MiniLM-L6-v2 | scifact | llm | gold_has_pronoun | 169 | -0.0248 | [-0.0601, +0.0052] | -0.0529 | [-0.1794, +0.0832] | 0.6615 |
| all-MiniLM-L6-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 |  | underpowered |  | underpowered | 0.6309 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | all queries | 323 | -0.0041 | [-0.0120, +0.0028] | 0.0451 | [-0.0468, +0.1372] | 0.3098 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | -0.0045 | [-0.0135, +0.0032] | 0.0441 | [-0.0519, +0.1406] | 0.3122 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| all-MiniLM-L6-v2 | nfcorpus | llm | all queries | 323 | -0.0035 | [-0.0104, +0.0027] | -0.0388 | [-0.1321, +0.0583] | 0.3098 |
| all-MiniLM-L6-v2 | nfcorpus | llm | gold_has_pronoun | 303 | -0.004 | [-0.0115, +0.0028] | -0.0436 | [-0.1425, +0.0592] | 0.3122 |
| all-MiniLM-L6-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| bge-small-en-v1.5 | scifact | lingmess | all queries | 300 | -0.0075 | [-0.0191, +0.0017] | -0.0691 | [-0.1784, +0.0485] | 0.7127 |
| bge-small-en-v1.5 | scifact | lingmess | gold_has_pronoun | 169 | -0.009 | [-0.0280, +0.0063] | -0.0659 | [-0.2161, +0.0984] | 0.7202 |
| bge-small-en-v1.5 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| bge-small-en-v1.5 | scifact | llm | all queries | 300 | -0.0072 | [-0.0218, +0.0032] | 0.001 | [-0.1268, +0.1265] | 0.7127 |
| bge-small-en-v1.5 | scifact | llm | gold_has_pronoun | 169 | 0.003 | [-0.0030, +0.0105] | 0.101 | [-0.0619, +0.2381] | 0.7202 |
| bge-small-en-v1.5 | scifact | llm | confirmed stratum (diagnostic) | 1 |  | underpowered |  | underpowered | 0.0 |
| bge-small-en-v1.5 | nfcorpus | lingmess | all queries | 323 | -0.0065 | [-0.0131, -0.0007] | -0.0494 | [-0.1404, +0.0412] | 0.3431 |
| bge-small-en-v1.5 | nfcorpus | lingmess | gold_has_pronoun | 303 | -0.0074 | [-0.0149, -0.0009] | -0.0535 | [-0.1487, +0.0421] | 0.3455 |
| bge-small-en-v1.5 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| bge-small-en-v1.5 | nfcorpus | llm | all queries | 323 | 0.0048 | [+0.0000, +0.0101] | 0.0869 | [-0.0106, +0.1811] | 0.3431 |
| bge-small-en-v1.5 | nfcorpus | llm | gold_has_pronoun | 303 | 0.0046 | [-0.0007, +0.0105] | 0.0892 | [-0.0184, +0.1917] | 0.3455 |
| bge-small-en-v1.5 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| e5-small-v2 | scifact | lingmess | all queries | 300 | -0.0295 | [-0.0487, -0.0120] | -0.1155 | [-0.2007, -0.0236] | 0.6884 |
| e5-small-v2 | scifact | lingmess | gold_has_pronoun | 169 | -0.0279 | [-0.0512, -0.0095] | -0.1301 | [-0.2402, -0.0127] | 0.6995 |
| e5-small-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| e5-small-v2 | scifact | llm | all queries | 300 | -0.0276 | [-0.0507, -0.0093] | -0.0503 | [-0.1445, +0.0495] | 0.6884 |
| e5-small-v2 | scifact | llm | gold_has_pronoun | 169 | -0.0152 | [-0.0371, +0.0008] | 0.026 | [-0.1061, +0.1614] | 0.6995 |
| e5-small-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 |  | underpowered |  | underpowered | 0.3562 |
| e5-small-v2 | nfcorpus | lingmess | all queries | 323 | -0.0091 | [-0.0168, -0.0022] | -0.0968 | [-0.1836, -0.0083] | 0.3248 |
| e5-small-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | -0.0088 | [-0.0166, -0.0015] | -0.0974 | [-0.1883, -0.0056] | 0.3267 |
| e5-small-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| e5-small-v2 | nfcorpus | llm | all queries | 323 | -0.0044 | [-0.0121, +0.0029] | -0.0268 | [-0.1229, +0.0728] | 0.3248 |
| e5-small-v2 | nfcorpus | llm | gold_has_pronoun | 303 | -0.005 | [-0.0135, +0.0033] | -0.029 | [-0.1322, +0.0751] | 0.3267 |
| e5-small-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| Qwen3-Embedding-0.6B | scifact | lingmess | all queries | 300 | -0.0042 | [-0.0176, +0.0065] | 0.0246 | [-0.0807, +0.1256] | 0.7034 |
| Qwen3-Embedding-0.6B | scifact | lingmess | gold_has_pronoun | 169 | -0.0068 | [-0.0302, +0.0125] | -0.0046 | [-0.1357, +0.1269] | 0.6969 |
| Qwen3-Embedding-0.6B | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| Qwen3-Embedding-0.6B | scifact | llm | all queries | 300 | -0.0096 | [-0.0211, -0.0008] | -0.0339 | [-0.1356, +0.0725] | 0.7034 |
| Qwen3-Embedding-0.6B | scifact | llm | gold_has_pronoun | 169 | -0.0018 | [-0.0056, +0.0005] | -0.08 | [-0.2026, +0.0588] | 0.6969 |
| Qwen3-Embedding-0.6B | scifact | llm | confirmed stratum (diagnostic) | 1 |  | underpowered |  | underpowered | 0.301 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | all queries | 323 | 0.0011 | [-0.0044, +0.0068] | -0.0615 | [-0.1421, +0.0235] | 0.3599 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | gold_has_pronoun | 303 | 0.0013 | [-0.0050, +0.0078] | -0.0655 | [-0.1573, +0.0248] | 0.3586 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |
| Qwen3-Embedding-0.6B | nfcorpus | llm | all queries | 323 | -0.0018 | [-0.0071, +0.0034] | -0.0374 | [-0.1251, +0.0517] | 0.3599 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | gold_has_pronoun | 303 | -0.002 | [-0.0082, +0.0039] | -0.0373 | [-0.1333, +0.0591] | 0.3586 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  | underpowered |  | underpowered |  |

A slope near -1 is regression to the mean rather than a uniform gain.

### Paired Wilcoxon on per-query delta, with effect size

| model | dataset | coref | scope | N | n!=0 | mean delta | mean 95% CI | median delta | rank-biserial | p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | scifact | lingmess | all queries | 300 | 33 | -0.0069 | [-0.0144, +0.0001] | 0.0 | -0.3583 | 0.07194 |
| all-MiniLM-L6-v2 | scifact | lingmess | gold_has_pronoun | 169 | 24 | -0.0143 | [-0.0266, -0.0034] | 0.0 | -0.5333 | 0.02195 |
| all-MiniLM-L6-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| all-MiniLM-L6-v2 | scifact | llm | all queries | 300 | 31 | -0.006 | [-0.0169, +0.0044] | 0.0 | -0.2137 | 0.2985 |
| all-MiniLM-L6-v2 | scifact | llm | gold_has_pronoun | 169 | 21 | -0.0053 | [-0.0202, +0.0091] | 0.0 | -0.1991 | 0.4236 |
| all-MiniLM-L6-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 | 0 | 0.0 | n/a | 0.0 | 0.0 | n/a |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | all queries | 323 | 103 | 0.001 | [-0.0015, +0.0035] | 0.0 | 0.1891 | 0.09564 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | 103 | 0.001 | [-0.0016, +0.0038] | 0.0 | 0.1891 | 0.09564 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| all-MiniLM-L6-v2 | nfcorpus | llm | all queries | 323 | 70 | -0.0003 | [-0.0026, +0.0019] | 0.0 | -0.041 | 0.7653 |
| all-MiniLM-L6-v2 | nfcorpus | llm | gold_has_pronoun | 303 | 69 | -0.0003 | [-0.0026, +0.0022] | 0.0 | -0.0207 | 0.8812 |
| all-MiniLM-L6-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| bge-small-en-v1.5 | scifact | lingmess | all queries | 300 | 22 | -0.0045 | [-0.0106, +0.0008] | 0.0 | -0.3715 | 0.1268 |
| bge-small-en-v1.5 | scifact | lingmess | gold_has_pronoun | 169 | 16 | -0.0058 | [-0.0154, +0.0028] | 0.0 | -0.3897 | 0.1705 |
| bge-small-en-v1.5 | scifact | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| bge-small-en-v1.5 | scifact | llm | all queries | 300 | 13 | -0.0016 | [-0.0073, +0.0034] | 0.0 | -0.2637 | 0.4241 |
| bge-small-en-v1.5 | scifact | llm | gold_has_pronoun | 169 | 7 | 0.0001 | [-0.0043, +0.0058] | 0.0 | -0.4286 | 0.375 |
| bge-small-en-v1.5 | scifact | llm | confirmed stratum (diagnostic) | 1 | 1 | 0.2891 | n/a | 0.2891 | 1.0 | 1 |
| bge-small-en-v1.5 | nfcorpus | lingmess | all queries | 323 | 71 | 0.0007 | [-0.0017, +0.0031] | 0.0 | 0.029 | 0.8321 |
| bge-small-en-v1.5 | nfcorpus | lingmess | gold_has_pronoun | 303 | 71 | 0.0007 | [-0.0018, +0.0033] | 0.0 | 0.029 | 0.8321 |
| bge-small-en-v1.5 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| bge-small-en-v1.5 | nfcorpus | llm | all queries | 323 | 68 | 0.0017 | [-0.0005, +0.0040] | 0.0 | 0.1398 | 0.3163 |
| bge-small-en-v1.5 | nfcorpus | llm | gold_has_pronoun | 303 | 67 | 0.0013 | [-0.0009, +0.0038] | 0.0 | 0.1141 | 0.4168 |
| bge-small-en-v1.5 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| e5-small-v2 | scifact | lingmess | all queries | 300 | 33 | -0.005 | [-0.0146, +0.0043] | 0.0 | -0.2068 | 0.2964 |
| e5-small-v2 | scifact | lingmess | gold_has_pronoun | 169 | 20 | -0.0017 | [-0.0135, +0.0099] | 0.0 | -0.0381 | 0.8808 |
| e5-small-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| e5-small-v2 | scifact | llm | all queries | 300 | 26 | -0.011 | [-0.0218, -0.0022] | 0.0 | -0.4986 | 0.02603 |
| e5-small-v2 | scifact | llm | gold_has_pronoun | 169 | 14 | -0.0014 | [-0.0094, +0.0066] | 0.0 | -0.2667 | 0.3792 |
| e5-small-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 | 0 | 0.0 | n/a | 0.0 | 0.0 | n/a |
| e5-small-v2 | nfcorpus | lingmess | all queries | 323 | 103 | -0.0021 | [-0.0057, +0.0012] | 0.0 | -0.0599 | 0.5975 |
| e5-small-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | 101 | -0.0019 | [-0.0056, +0.0016] | 0.0 | -0.0493 | 0.667 |
| e5-small-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| e5-small-v2 | nfcorpus | llm | all queries | 323 | 88 | -0.0013 | [-0.0043, +0.0018] | 0.0 | -0.0603 | 0.6234 |
| e5-small-v2 | nfcorpus | llm | gold_has_pronoun | 303 | 88 | -0.0014 | [-0.0046, +0.0018] | 0.0 | -0.0603 | 0.6234 |
| e5-small-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| Qwen3-Embedding-0.6B | scifact | lingmess | all queries | 300 | 17 | 0.0009 | [-0.0051, +0.0078] | 0.0 | -0.0458 | 0.8683 |
| Qwen3-Embedding-0.6B | scifact | lingmess | gold_has_pronoun | 169 | 14 | -0.0004 | [-0.0104, +0.0107] | 0.0 | -0.1524 | 0.6152 |
| Qwen3-Embedding-0.6B | scifact | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| Qwen3-Embedding-0.6B | scifact | llm | all queries | 300 | 15 | -0.0023 | [-0.0085, +0.0035] | 0.0 | -0.2417 | 0.4092 |
| Qwen3-Embedding-0.6B | scifact | llm | gold_has_pronoun | 169 | 7 | 0.0024 | [-0.0006, +0.0074] | 0.0 | 0.5 | 0.2969 |
| Qwen3-Embedding-0.6B | scifact | llm | confirmed stratum (diagnostic) | 1 | 1 | -0.012 | n/a | -0.012 | -1.0 | 1 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | all queries | 323 | 75 | 0.0017 | [-0.0005, +0.0040] | 0.0 | 0.1211 | 0.3623 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | gold_has_pronoun | 303 | 75 | 0.0018 | [-0.0005, +0.0043] | 0.0 | 0.1211 | 0.3623 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |
| Qwen3-Embedding-0.6B | nfcorpus | llm | all queries | 323 | 54 | -0.0008 | [-0.0028, +0.0012] | 0.0 | -0.2444 | 0.1181 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | gold_has_pronoun | 303 | 54 | -0.0009 | [-0.0030, +0.0013] | 0.0 | -0.2444 | 0.1181 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | confirmed stratum (diagnostic) | 0 | 0 |  | n/a |  | 0.0 | n/a |

`rank-biserial`: +1 = every query improved, -1 = every query degraded, 0 = balanced.

### Power

| model | dataset | coref | scope | N | observed delta | sd | N for 80% power |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | scifact | lingmess | all queries | 300 | -0.0069 | 0.0636 | 667 |
| all-MiniLM-L6-v2 | scifact | lingmess | gold_has_pronoun | 169 | -0.0143 | 0.0778 | 231 |
| all-MiniLM-L6-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| all-MiniLM-L6-v2 | scifact | llm | all queries | 300 | -0.006 | 0.0936 | 1908 |
| all-MiniLM-L6-v2 | scifact | llm | gold_has_pronoun | 169 | -0.0053 | 0.0962 | 2602 |
| all-MiniLM-L6-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 |  |  | n/a (empty) |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | all queries | 323 | 0.001 | 0.0234 | 4515 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | 0.001 | 0.0241 | 4236 |
| all-MiniLM-L6-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| all-MiniLM-L6-v2 | nfcorpus | llm | all queries | 323 | -0.0003 | 0.0208 | 28155 |
| all-MiniLM-L6-v2 | nfcorpus | llm | gold_has_pronoun | 303 | -0.0003 | 0.0215 | 43482 |
| all-MiniLM-L6-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| bge-small-en-v1.5 | scifact | lingmess | all queries | 300 | -0.0045 | 0.0507 | 1003 |
| bge-small-en-v1.5 | scifact | lingmess | gold_has_pronoun | 169 | -0.0058 | 0.061 | 856 |
| bge-small-en-v1.5 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| bge-small-en-v1.5 | scifact | llm | all queries | 300 | -0.0016 | 0.0479 | 7171 |
| bge-small-en-v1.5 | scifact | llm | gold_has_pronoun | 169 | 0.0001 | 0.0332 | 414569 |
| bge-small-en-v1.5 | scifact | llm | confirmed stratum (diagnostic) | 1 |  |  | n/a (empty) |
| bge-small-en-v1.5 | nfcorpus | lingmess | all queries | 323 | 0.0007 | 0.0221 | 8836 |
| bge-small-en-v1.5 | nfcorpus | lingmess | gold_has_pronoun | 303 | 0.0007 | 0.0228 | 8290 |
| bge-small-en-v1.5 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| bge-small-en-v1.5 | nfcorpus | llm | all queries | 323 | 0.0017 | 0.021 | 1239 |
| bge-small-en-v1.5 | nfcorpus | llm | gold_has_pronoun | 303 | 0.0013 | 0.0203 | 1787 |
| bge-small-en-v1.5 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| e5-small-v2 | scifact | lingmess | all queries | 300 | -0.005 | 0.085 | 2252 |
| e5-small-v2 | scifact | lingmess | gold_has_pronoun | 169 | -0.0017 | 0.0784 | 17076 |
| e5-small-v2 | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| e5-small-v2 | scifact | llm | all queries | 300 | -0.011 | 0.087 | 489 |
| e5-small-v2 | scifact | llm | gold_has_pronoun | 169 | -0.0014 | 0.0527 | 11212 |
| e5-small-v2 | scifact | llm | confirmed stratum (diagnostic) | 1 |  |  | n/a (empty) |
| e5-small-v2 | nfcorpus | lingmess | all queries | 323 | -0.0021 | 0.0315 | 1696 |
| e5-small-v2 | nfcorpus | lingmess | gold_has_pronoun | 303 | -0.0019 | 0.0317 | 2197 |
| e5-small-v2 | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| e5-small-v2 | nfcorpus | llm | all queries | 323 | -0.0013 | 0.0282 | 3733 |
| e5-small-v2 | nfcorpus | llm | gold_has_pronoun | 303 | -0.0014 | 0.0291 | 3502 |
| e5-small-v2 | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| Qwen3-Embedding-0.6B | scifact | lingmess | all queries | 300 | 0.0009 | 0.057 | 32420 |
| Qwen3-Embedding-0.6B | scifact | lingmess | gold_has_pronoun | 169 | -0.0004 | 0.0705 | 257815 |
| Qwen3-Embedding-0.6B | scifact | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| Qwen3-Embedding-0.6B | scifact | llm | all queries | 300 | -0.0023 | 0.0524 | 4230 |
| Qwen3-Embedding-0.6B | scifact | llm | gold_has_pronoun | 169 | 0.0024 | 0.0292 | 1185 |
| Qwen3-Embedding-0.6B | scifact | llm | confirmed stratum (diagnostic) | 1 |  |  | n/a (empty) |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | all queries | 323 | 0.0017 | 0.0203 | 1081 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | gold_has_pronoun | 303 | 0.0018 | 0.021 | 1014 |
| Qwen3-Embedding-0.6B | nfcorpus | lingmess | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |
| Qwen3-Embedding-0.6B | nfcorpus | llm | all queries | 323 | -0.0008 | 0.0184 | 4007 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | gold_has_pronoun | 303 | -0.0009 | 0.019 | 3759 |
| Qwen3-Embedding-0.6B | nfcorpus | llm | confirmed stratum (diagnostic) | 0 |  |  | n/a (empty) |

### Plots

- `delta_vs_baseline__scifact__all.png`
- `delta_vs_baseline__scifact__pronoun.png`
- `delta_vs_baseline__scifact__confirmed.png`
- `delta_vs_baseline__nfcorpus__all.png`
- `delta_vs_baseline__nfcorpus__pronoun.png`
- `delta_vs_baseline__nfcorpus__confirmed.png`
