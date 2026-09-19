# LLM Clinical Eval Framework

A configurable, rubric-driven framework for evaluating LLM-generated clinical recommendations. Rather than hardcoding a single disease-specific rubric into the pipeline, this project treats the **scoring rubric itself as data** — any structured clinical rubric can be loaded and used to score any clinical response, with no changes to the underlying engine.

## Motivation

This project grew out of a real research workflow: manually running multiple LLMs against clinical cases and scoring their outputs against a rubric reviewed by a team of pharmacists. That process worked, but was entirely manual — spreadsheets, hand-scoring, and no reusable tooling.

This framework automates that same idea end-to-end: a clinical case goes in, an LLM generates a recommendation, and a second LLM scores that recommendation against a structured rubric — producing consistent, reproducible, itemized results instead of ad hoc manual review.

## How it works

The pipeline runs in five stages:

1. **Structured input collection** — the user is prompted field-by-field for case details (chief complaint, PMH, PSH, medications, clinical findings, allergies, labs, vitals).
2. **Case formatting** — an LLM, acting as an attending physician, reformats the raw fields into a single, flowing clinical presentation, the way one physician would hand off a case to another.
3. **Consultant response generation** — a second LLM call takes that formatted case and produces a structured clinical recommendation, following a fixed alphanumeric outline (chief complaint, comorbidities, dosing, safety, communication, follow-up).
4. **Rubric-based judging** — a third LLM call scores the consultant response, item by item, against a YAML-defined rubric, returning a JSON object of per-item scores (0, 1, or 2).
5. **Scoring** — the parsed scores are summed and compared against the rubric's total possible points.

All three LLM calls share a consistent "attending physician" persona (set via the API's `system` parameter), while each call's specific task instructions live in its own prompt-building function.

`![Demo of the pipeline running](assets/README_demo.gif)`

## Project structure

```
llm-clinical-eval/
├── rubric/
│   └── example_rubric.yaml       # Generic, domain-agnostic scoring rubric
├── objects.py                     # Rubric / Domain / Item dataclasses + YAML loader
├── call_API.py                    # Shared Anthropic API wrapper (call_claude)
├── case_input.py                  # Structured field-by-field user input collection
├── prompts/
│   ├── llm_HPI.py                 # Reformats raw input into a clinical presentation
│   ├── llm_consultant.py          # Generates clinical recommendations
│   └── llm_judge.py               # Scores a response against the rubric
├── .env                            # API key (not committed)
├── .gitignore
└── README.md
```

## The rubric

Rubrics are defined as YAML, not hardcoded — any rubric following this shape can be dropped in without touching the scoring engine:

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

The included `example_rubric.yaml` is a generalized, condition-agnostic version of a rubric originally developed and reviewed for a diabetes-specific research project — restructured here to score clinical reasoning across any presenting condition.

## Setup

1. Clone the repo and install dependencies:
   ```
   pip install pyyaml python-dotenv anthropic --break-system-packages
   ```
2. Create a `.env` file in the project root:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```
3. Run the full pipeline:
   ```
   python -m prompts.llm_judge
   ```
   You'll be prompted for case details, then the pipeline will generate a consultant response, score it, and print the itemized results plus a total.

## Design notes / known limitations

- **Scoring assumes equal item weighting.** `calculate_total` sums raw item scores; it does not currently support per-item point weighting. The rubric schema could be extended with a `points` field per item to support this.
- **The judge's JSON output is defensively parsed**, since LLMs occasionally wrap JSON in markdown code fences despite explicit instructions not to — the judge parser strips these before calling `json.loads`.
- **The case-formatting step (`llm_HPI.py`) has some hallucination risk** — testing showed it can occasionally infer a status (e.g., "not yet performed") for a field reported as absent, rather than reporting it exactly as given. The prompt has been tightened to explicitly prohibit this, but this is worth continued monitoring.
- **Judge reliability was validated manually**, not statistically: a deliberately weak mock response scored 0/42, a deliberately strong response scored 42/42, and a middling response produced a genuine mix of 0s, 1s, and 2s across items — confirming the judge discriminates at the item level rather than defaulting to uniform scores.

## Roadmap

- **Manual scoring path** — allow a human to score the same response independently, to compute inter-rater agreement (e.g., weighted kappa) between the LLM judge and a human reviewer.
- **Batch case runs** — run multiple cases through the pipeline in a loop and persist results (CSV/JSON) for aggregate analysis across cases and models.
- **Multi-model comparison** — extend `call_claude` (or add sibling functions) to compare recommendations across multiple LLM providers, echoing the original manual research process this project automates.
- **Source-grounded consultant (RAG)** — retrieval over clinical guidelines/literature (e.g., PubMed) so consultant recommendations are grounded in retrievable, citable sources.
- **Patient-facing mode** — a separate, clearly-disclaimed educational mode where a patient can input their own diagnosis/summary and receive an explanation with explorable sources, distinct from the clinician-facing consultant mode. This mode is explicitly **not** intended to provide medical advice or diagnosis.

## Tech stack

Python, PyYAML, python-dotenv, Anthropic API (Claude Haiku 4.5)
