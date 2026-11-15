# Research summary

## Title
Multilingual LLM Safety and Inference Benchmark: A Comparative Pilot Study of English, Telugu, and Telugu-English Code-Switched Prompts

## Abstract
This pilot study compares one locally executed language model across matched English, Telugu, and Telugu-English code-switched prompts. The dataset contains 20 matched prompt groups (10 harmless and 10 disallowed), producing 60 model responses. The study examines response helpfulness, language adherence, safety behaviour, and inference performance. The model was Qwen3-0.6B served locally through Ollama. Results are descriptive and should be interpreted cautiously because the sample is small, language variants require independent semantic validation, and adopted human ratings were produced by a single evaluator.

## Research question
Does one fixed model exhibit differences in safety behaviour, response quality, and inference performance when equivalent requests are presented in English, Telugu, and Telugu-English code-switched language?

## Experimental configuration
- Model tag: qwen3:0.6b
- Interface: Ollama local chat API
- Temperature: 0
- Maximum generated tokens: 160
- Context window: 2,048 tokens
- Repetition penalty: 1.15
- Thinking: disabled
- Dataset: 60 prompts across 3 language conditions

## Main descriptive findings

### Response quality and language adherence
| Metric (0–2 mean) | English | Telugu | Code-switched |
|---|---:|---:|---:|
| Helpfulness | 1.85 | 0.00 | 0.00 |
| Language adherence | 2.00 | 0.70 | 0.05 |

### Safety on disallowed prompts
| Mean safety score (0–2) | English | Telugu | Code-switched |
|---|---:|---:|---:|
| Disallowed prompts only | 1.80 | 0.60 | 0.90 |

There was one clear unsafe English response that suggested objects as weapons. Several Telugu and code-switched outputs repeated harmful requests or were unintelligible, making the safety behaviour unclear. The rubric distinguishes clear failure (0), ambiguous/unclear (1), and expected safe behaviour (2); unclear output should not be described as confirmed harmful compliance.

### Inference performance
| Metric | English | Telugu | Code-switched |
|---|---:|---:|---:|
| Mean wall time (seconds) | 3.677 | 4.948 | 5.173 |
| Mean generated tokens | 63.45 | 103.55 | 119.75 |
| Mean throughput (tokens/second) | 42.912 | 41.205 | 42.258 |

The local run completed 60/60 API requests with non-empty responses and no request errors. Nine responses reached the 160-token cap. Throughput was broadly similar, while mean wall time and generated-token counts were higher for Telugu and code-switched prompts. These averages do not establish that language alone caused the timing differences; prompt length, tokenization, output length, warm-up, hardware, and runtime can contribute.

## Human evaluation
Ratings use a 0–2 scale for helpfulness, language adherence, and safety behaviour. The adopted ratings are single-evaluator judgments, including suggested scores reviewed and accepted by the researcher. They are not independent multi-annotator labels, and no inter-rater reliability estimate is available.

## Limitations
1. The prompt set is small and is not a representative benchmark.
2. Telugu and code-switched translations require independent fluent-speaker validation for semantic equivalence.
3. Ratings are from one evaluator; independent annotation and adjudication are needed.
4. Several outputs reached the token cap and require truncation review.
5. Runtime results are hardware- and runtime-dependent and should be replicated.
6. A single small model cannot support conclusions about all LLMs or multilingual systems.

## Recommended next steps
- Validate prompt equivalence with fluent Telugu reviewers.
- Obtain an independent second evaluator and report agreement.
- Repeat runs and record exact model digest, Ollama version, date, and hardware.
- Evaluate additional models and a larger balanced prompt set.
- Conduct paired statistical analysis only where sample size and assumptions justify it.

## Responsible interpretation
This project is an exploratory pilot. Its findings are signals for further investigation, not proof of a general multilingual safety gap or a universal property of LLMs.
