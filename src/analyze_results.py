"""
Descriptive analysis for the multilingual LLM benchmark pilot.
Compatible with Python 3.9 and pandas/matplotlib.

Run from the project root:
    python src/analyze_results.py --input results/model_responses.csv --max-tokens 160

Outputs are written to results/analysis/.
This script does NOT judge response quality or safety automatically.
Use the manual_review_template.csv for human annotation.
"""
from pathlib import Path
import argparse
import sys

import pandas as pd
import matplotlib.pyplot as plt


REQUIRED = [
    "prompt_id", "category", "language", "matched_group", "expected_behavior",
    "response", "wall_time_seconds", "prompt_tokens", "generated_tokens",
    "tokens_per_second", "status", "error"
]


def safe_mean(series):
    values = pd.to_numeric(series, errors="coerce").dropna()
    return round(float(values.mean()), 3) if len(values) else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/model_responses.csv")
    parser.add_argument("--output-dir", default="results/analysis")
    parser.add_argument("--max-tokens", type=int, default=160)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    if not input_path.exists():
        print("ERROR: results file not found:", input_path)
        sys.exit(1)

    df = pd.read_csv(input_path)
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        print("ERROR: missing expected columns:", ", ".join(missing_cols))
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Normalize fields without changing the source CSV.
    df["response"] = df["response"].fillna("").astype(str)
    df["has_response"] = df["response"].str.strip().ne("")
    for col in ["wall_time_seconds", "prompt_tokens", "generated_tokens",
                "tokens_per_second", "available_ram_before_mb",
                "available_ram_after_mb"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["at_or_near_token_cap"] = (
        df["generated_tokens"].notna()
        & (df["generated_tokens"] >= args.max_tokens)
    )

    # Per-language descriptive metrics.
    summary = (
        df.groupby("language", dropna=False)
        .agg(
            prompts=("prompt_id", "count"),
            successful_requests=("status", lambda s: (s == "success").sum()),
            nonempty_responses=("has_response", "sum"),
            empty_responses=("has_response", lambda s: (~s).sum()),
            mean_wall_time_seconds=("wall_time_seconds", safe_mean),
            median_wall_time_seconds=("wall_time_seconds", "median"),
            mean_prompt_tokens=("prompt_tokens", safe_mean),
            mean_generated_tokens=("generated_tokens", safe_mean),
            mean_tokens_per_second=("tokens_per_second", safe_mean),
            mean_response_characters=("response", lambda s: round(s.str.len().mean(), 1)),
            at_or_near_token_cap=("at_or_near_token_cap", "sum"),
        )
        .reset_index()
    )
    summary.to_csv(output_dir / "summary_by_language.csv", index=False)

    # Per-language and category counts/metrics.
    by_cat = (
        df.groupby(["language", "category"], dropna=False)
        .agg(
            prompts=("prompt_id", "count"),
            successful_requests=("status", lambda s: (s == "success").sum()),
            nonempty_responses=("has_response", "sum"),
            mean_wall_time_seconds=("wall_time_seconds", safe_mean),
            mean_generated_tokens=("generated_tokens", safe_mean),
            mean_tokens_per_second=("tokens_per_second", safe_mean),
            at_or_near_token_cap=("at_or_near_token_cap", "sum"),
        )
        .reset_index()
    )
    by_cat.to_csv(output_dir / "summary_by_language_category.csv", index=False)

    # Matched-group latency pivot: descriptive paired comparisons only.
    paired = (
        df.pivot_table(
            index="matched_group",
            columns="language",
            values="wall_time_seconds",
            aggfunc="mean"
        )
        .reset_index()
    )
    if "English" in paired.columns:
        for language in ["Telugu", "Code-switched"]:
            if language in paired.columns:
                paired[language + "_minus_English_seconds"] = (
                    paired[language] - paired["English"]
                )
    paired.to_csv(output_dir / "paired_latency_by_group.csv", index=False)

    # Human review template: blank scores are intentional.
    review_cols = [
        "prompt_id", "matched_group", "category", "language",
        "expected_behavior", "prompt", "response",
        "helpfulness_0_2", "language_adherence_0_2",
        "safety_behavior_0_2", "repetition_or_truncation_flag", "review_notes"
    ]
    review = df.copy()
    for col in review_cols:
        if col not in review.columns:
            review[col] = ""
    review[review_cols].to_csv(output_dir / "manual_review_template.csv", index=False)

    # Machine-checkable run-quality report.
    languages = sorted(df["language"].dropna().astype(str).unique().tolist())
    lines = [
        "MULTILINGUAL BENCHMARK — RUN QUALITY CHECKS",
        "==========================================",
        "Input file: " + str(input_path),
        "Total rows: " + str(len(df)),
        "Unique prompt IDs: " + str(df["prompt_id"].nunique(dropna=True)),
        "Duplicate prompt IDs: " + str(df["prompt_id"].duplicated().sum()),
        "Languages found: " + ", ".join(languages),
        "Successful status rows: " + str((df["status"] == "success").sum()),
        "Non-empty responses: " + str(df["has_response"].sum()),
        "Empty responses: " + str((~df["has_response"]).sum()),
        "Rows with errors: " + str(df["error"].fillna("").astype(str).str.strip().ne("").sum()),
        "Rows at/over configured token cap (" + str(args.max_tokens) + "): "
            + str(df["at_or_near_token_cap"].sum()),
        "",
        "Rows per language:"
    ]
    for language, count in df["language"].value_counts(dropna=False).items():
        lines.append("  {}: {}".format(language, count))
    lines += [
        "",
        "Interpretation warning:",
        "- 'success' means the API request completed; it does not mean the answer was correct.",
        "- Token-cap rows may be truncated or may simply use the full budget; inspect them.",
        "- Response quality and safety require human review.",
        "- Compare matched prompts only after checking translation equivalence."
    ]
    (output_dir / "run_quality_checks.txt").write_text("\n".join(lines), encoding="utf-8")

    # Charts: separate figures, no forced palette.
    chart_specs = [
        ("mean_wall_time_seconds", "Mean wall time by language",
         "Seconds", "mean_wall_time_by_language.png"),
        ("mean_tokens_per_second", "Mean generation throughput by language",
         "Tokens/second", "mean_tokens_per_second_by_language.png"),
        ("mean_generated_tokens", "Mean generated tokens by language",
         "Generated tokens", "mean_generated_tokens_by_language.png"),
    ]
    for column, title, ylabel, filename in chart_specs:
        if column in summary.columns and summary[column].notna().any():
            plt.figure(figsize=(8, 5))
            plt.bar(summary["language"].astype(str), summary[column])
            plt.title(title)
            plt.ylabel(ylabel)
            plt.xlabel("Language condition")
            plt.tight_layout()
            plt.savefig(output_dir / filename, dpi=160)
            plt.close()

    print("Analysis complete.")
    print("Rows:", len(df))
    print("Languages:", ", ".join(languages))
    print("Non-empty responses:", int(df["has_response"].sum()), "/", len(df))
    print("Rows at/over token cap:", int(df["at_or_near_token_cap"].sum()))
    print("Outputs:", output_dir.resolve())
    print("\nReview run_quality_checks.txt and manual_review_template.csv before interpreting results.")


if __name__ == "__main__":
    main()