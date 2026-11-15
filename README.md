# Multilingual LLM Safety and Inference Benchmark — pilot

## Research question
Does one fixed model show differences in safety behaviour and inference performance across matched English, Telugu, and Telugu-English prompts?

## Dataset
- 20 matched prompt groups: 10 harmless and 10 high-level disallowed safety probes.
- Each group has English, Telugu, and code-switched variants.
- Total: 60 rows.
- Translations are draft translations and must be reviewed by a fluent Telugu speaker before treating the dataset as validated.

## Model
Initial baseline: `qwen3:0.6b` via Ollama. Record the exact Ollama version, model tag/digest, date, hardware, and generation settings in the final report.

## Important limitations
- This is a small pilot, not a representative multilingual safety benchmark.
- A single small model cannot support claims about all LLMs.
- The Telugu and code-switched prompts require independent language review.
- Safety labels require human review; do not infer them automatically from refusal keywords.
- Available system RAM before/after a request is only a coarse system-level observation, not model-only peak memory.
- Inference timing is hardware- and runtime-dependent.

## First run
Run a three-row smoke test first:
`python src/run_experiment.py --limit 3`

After verifying that it works, run all rows:
`python src/run_experiment.py --limit 0`

Results are saved to `results/model_responses.csv`.