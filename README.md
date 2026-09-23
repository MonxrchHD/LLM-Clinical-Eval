# LLM Clinical Eval Framework

A configurable, rubric-driven framework for evaluating LLM-generated clinical recommendations — and, built on top of it, a pipeline for turning those evaluations into training data for preference-based fine-tuning (DPO). The scoring rubric is treated as **data**, not hardcoded logic, so any structured clinical rubric can be loaded and used to score any clinical response without changing the underlying engine.

## Motivation

This project grew out of a real research workflow: manually running multiple LLMs against clinical cases and scoring their outputs against a rubric reviewed by a team of pharmacists. That process worked, but was entirely manual — spreadsheets, hand-scoring, no reusable tooling, and no way to turn the results into anything beyond a one-off comparison.

This framework automates that process end-to-end, then goes a step further: it uses the same evaluation engine to generate labeled preference data (a strong response paired with a deliberately flawed one, per case) suitable for fine-tuning a smaller, open-source model to reason more safely about clinical cases.

## How it works

### Evaluation pipeline (core)

1. **Structured input collection** — a person is prompted field-by-field for case details, or a batch of pre-written cases is loaded from a JSON file.
2. **Case formatting** — an LLM, acting as an attending physician, reformats the raw fields into a single, flowing clinical presentation.
3. **Consultant response generation** — a second LLM call produces a structured clinical recommendation, ending with a short standalone clinical summary.
4. **Rubric-based judging** — a third LLM call scores the recommendation item-by-item against a YAML-defined rubric, and separately flags critical errors, unsupported claims, scope violations, and major omissions.
5. **Scoring and logging** — results (case, response, summary, scores, flags) are appended to `data/data_logs.jsonl`.

### DPO data pipeline (built on top of the core engine)

6. **Flawed-response generation** — for a given case and its real, high-quality response, a fourth LLM call generates a plausible-but-dangerous counterpart, deliberately containing a case-specific critical safety error plus a vague/inaccurate recommendation.
7. **Validation via the judge** — the flawed response is scored using the same rubric and judge as any real response, confirming it's genuinely worse (not just cosmetically different) before being kept.
8. **Pair filtering** — only pairs with a meaningful score gap (currently ≥10 points) between the real and flawed response are kept, logged to `data/dpo_pairs.jsonl`.
9. **Format conversion** — validated pairs are converted into the standard DPO training shape (`{"prompt": ..., "chosen": ..., "rejected": ...}`) in `data/dpo_training_data.jsonl`, ready to feed into a training library.

All LLM calls share a consistent "attending physician" persona (set via the API's `system` parameter); each call's task-specific instructions live in its own prompt-building function.

## Project structure

```
llm-clinical-eval/
├── rubric/
│   └── example_rubric.yaml         # Generic, domain-agnostic scoring rubric
├── batch/
│   ├── sample_cases.json            # Example pre-written cases for batch mode
│   ├── cardiology_cases.json
│   ├── endocrine_renal_cases.json
│   ├── infectious_disease_cases.json
│   ├── pediatrics_cases.json
│   └── neuro_psych_cases.json       # Specialty-organized batch case sets
├── data/
│   ├── data_logs.jsonl               # Real logged evaluation results
│   ├── dpo_pairs.jsonl               # Validated (case, chosen, rejected) pairs + scores
│   └── dpo_training_data.jsonl       # Final {prompt, chosen, rejected} training format
├── objects.py                        # Rubric / Domain / Item dataclasses + YAML loader
├── call_API.py                       # Shared Anthropic API wrapper + persona/model constants
├── case_input.py                     # Interactive field collection + raw-case-to-text assembly
├── data_logger.py                    # Appends completed runs, DPO pairs, and training data to their JSONL logs
├── automate_pipeline.py              # Orchestrates a full run for one case, or a batch of cases
├── dpo_pipeline.py                   # Generates and validates flawed-response pairs; converts to training format
├── view_logs.py                      # Human-readable viewer for data_logs.jsonl
├── prompts/
│   ├── llm_HPI.py                    # Reformats raw input into a clinical presentation
│   ├── llm_consultant.py             # Generates clinical recommendations + summary
│   └── llm_judge.py                  # Scores a response against the rubric, detects flags
├── train_dpo.py                      # QLoRA/DPO fine-tuning script (run inside ft-env)
├── test_inference.py                 # Runs a held-out case through the fine-tuned adapter
├── test_inference_base.py            # Runs the same case through the unmodified base model, for comparison
├── models/                           # Saved LoRA adapters (not committed - see .gitignore)
├── ft-env/                           # Python 3.11 virtual environment for fine-tuning (not committed)
├── .env                                # API key (not committed)
├── .gitignore
├── README.md
├── SETUP.md                          # Local fine-tuning environment setup, including Windows-specific gotchas
└── TRAINING_RESULTS.md               # Fine-tuning experiment results and honest findings
```

## Usage

```
pip install pyyaml python-dotenv anthropic --break-system-packages
```
Create a `.env` file with `ANTHROPIC_API_KEY=your-key-here`, then run:
```
python automate_pipeline.py
```
Choose **"one case"** (interactive input) or **"batches"** (point it at any file in `batch/`). Either mode logs full results to `data/data_logs.jsonl`.

To review logged results in a readable format:
```
python view_logs.py
```

To generate and validate DPO training pairs from everything currently logged, then convert them to training format:
```
python dpo_pipeline.py
```
(Runs `build_dpo_dataset()` against `data/data_logs.jsonl`, then `build_dpo_converter()` to produce `data/dpo_training_data.jsonl`. Note: this currently reprocesses the entire log each run, so re-running after adding new cases will regenerate pairs for previously-processed cases too — acceptable at current dataset size, a known limitation for later.)

## The rubric

Rubrics are defined as YAML — any rubric following this shape can be dropped in without touching the scoring engine:

```yaml
rubric_name: "Clinical Reasoning Validation"
total_points: 42
domains:
  - name: "Clinical Decision Making and CC Prioritization"
    max_points: 10
    items:
      - id: "A-1"
        topic: "Individualized chief complaint stated"
        criteria:
          0: "No individualized chief complaint stated"
          1: "Chief complaint stated, but vague"
          2: "Chief complaint is stated clearly and uses proper terminology"
flags:
  - name: "Critical Errors"
    description: "Any critical errors that could result in patient harm"
    reported_separately: true
```

The included `example_rubric.yaml` is a generalized, condition-agnostic version of a rubric originally developed and reviewed for a diabetes-specific research project.

## Design notes / known limitations

- **Scoring assumes equal item weighting.** The rubric schema doesn't currently support per-item point weighting.
- **The judge's JSON output is defensively parsed and error-resilient** — malformed responses are skipped (with a printed warning) rather than crashing an entire batch run.
- **Flags and scoring were validated against deliberately flawed responses** across multiple cases and specialties — the judge consistently and correctly identifies critical errors, unsupported claims, and major omissions, with scores dropping sharply and proportionally to severity.
- **DPO pairs are validated, not assumed** — every flawed response is scored by the same judge before being accepted into the training set, and only pairs with a real, meaningful score gap are kept.
- **One rare judge output anomaly observed**: a single record in the dataset contained a rubric item ID not present in the actual rubric (likely an occasional judge hallucination on the JSON structure). Doesn't currently affect training since only the text fields are used downstream, but worth validating against in a future data-cleaning pass.
- **`dpo_pipeline.py` reprocesses the full log on every run** rather than tracking which cases have already been converted — acceptable at current scale (results in some duplicate pairs), but would need a "processed" tracking mechanism to scale efficiently.
- **The case-formatting step (`llm_HPI.py`) has some hallucination risk** for fields reported as absent — the prompt explicitly prohibits inferring an unstated status, but this is worth continued monitoring.

## Roadmap

**Completed:**
- **QLoRA/DPO fine-tuning attempt** — fine-tuned Mistral-7B-Instruct-v0.3 locally (RTX 3060, 12GB VRAM) via Unsloth + `trl`'s `DPOTrainer`, across two training runs of increasing dataset size. Full setup, metrics, and an honest analysis of the results (including a clear overfitting finding and what would be needed to improve on it) are documented in **`TRAINING_RESULTS.md`**; environment setup details are in `SETUP.md`.

**In progress:**
- **Source-grounded consultant (RAG)** — retrieval over clinical guidelines/literature (e.g., PubMed) so consultant recommendations are grounded in retrievable, citable sources.

**Planned next:**
- **Manual scoring path** — allow a human to score a response independently, to compute inter-rater agreement (e.g., weighted kappa) between the LLM judge and a human reviewer.
- **Multi-model comparison** — compare consultant recommendations across multiple LLM providers.
- **Patient-facing mode** — a separate, clearly-disclaimed educational mode where a patient can input their own diagnosis/summary and receive an explanation with explorable sources, distinct from the clinician-facing consultant mode, and explicitly **not** intended to provide medical advice or diagnosis. Would likely involve a conversational, multi-turn interface (the model asking clarifying questions rather than requiring all information upfront) and a web front end — a substantial project on its own, planned as the last major phase.

The full roadmap (fine-tuning → RAG → conversational UI) is unlikely to be fully complete on any fixed timeline; the priority is finishing and being able to fully explain each piece, with clear documentation of architecture decisions for whatever isn't yet built.

## Tech stack

Python, PyYAML, python-dotenv, Anthropic API (Claude Haiku 4.5). Planned: `transformers`, `trl`, `peft`, `bitsandbytes` for local QLoRA/DPO fine-tuning.

## Demo

![Demo of the pipeline running](Assets/README_demo.gif)