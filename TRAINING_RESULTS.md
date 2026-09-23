# DPO Fine-Tuning: Experiment Results

This documents the first QLoRA/DPO fine-tuning attempt on top of the LLM Clinical Eval Framework's automatically-generated training data — what was tried, what the metrics showed, and the honest conclusion drawn from them. Written as a companion to `SETUP.md` (environment setup) and the main `README.md` (project overview).

## Goal

Test whether the framework's automatically-generated, judge-validated preference pairs (`data/dpo_training_data.jsonl`) could be used to fine-tune a small open-source model (Mistral-7B-Instruct-v0.3) via QLoRA/DPO on consumer hardware (RTX 3060, 12GB VRAM), and whether doing so measurably improved the model's clinical reasoning on cases it had never seen.

## Setup

- **Base model:** `mistralai/Mistral-7B-Instruct-v0.3` (loaded via Unsloth's pre-quantized 4-bit build)
- **Method:** QLoRA (r=16, target modules: attention + MLP projections) + DPO (`beta=0.1`)
- **Trainable parameters:** 41,943,040 of 7,289,966,592 (0.58%)
- **Hardware:** RTX 3060, 12GB VRAM (see `SETUP.md` for full environment details)

## Runs

| | Run 1 | Run 2 |
|---|---|---|
| Training examples | 34 | 97 |
| Epochs | 3 | 1 |
| Total steps | 15 | 13 |
| Final `train_loss` | 0.1183 | 0.1477 |
| `rewards/margins` trend | Smooth, near-monotonic collapse toward 0 loss; margins climbing unbounded into the 70s | Noisier, non-monotonic; loss bounces rather than collapsing smoothly; margins still climb into the 30s-40s but with occasional negative `rewards/chosen` on later steps |
| Saved to | `models/mistral-7b-clinical-dpo-final` | `models/mistral-7b-clinical-dpo-final-v2` |

Note: the 97-example count for Run 2 reflects `data/dpo_training_data.jsonl` after two rounds of `build_dpo_dataset()`, which reprocesses the full case log each run rather than tracking already-converted cases (a known, accepted limitation — see main README).

## Qualitative comparison

All three variants (base model, Run 1 adapter, Run 2 adapter) were given the identical, held-out test case — a serotonin syndrome scenario (fluoxetine + buspirone + tramadol) that was **not** part of any training batch:

- **Base model (no fine-tuning):** Correctly identified serotonin syndrome, named all three drugs' specific serotonergic mechanisms, and included precise cyproheptadine dosing (2-4mg PO q2h, max 16mg/day). Well-organized, textbook-structured answer.
- **Run 1 adapter:** Correctly identified serotonin syndrome and recommended stopping tramadol, but opened with an odd verbatim restatement of the case, included a weaker differential ("fluoxetine-induced akathisia"), and omitted cyproheptadine dosing entirely.
- **Run 2 adapter:** Improved over Run 1 — no verbatim restatement, more organized reasoning, more thorough 8-point management plan (including electrolyte monitoring and a sensible note to reassess the psychiatric regimen after stopping tramadol). Still omitted cyproheptadine dosing and gave a vaguer mechanistic explanation than the base model.

## Conclusion

**The fine-tuning did not, on this test case, exceed the base model's own pretrained clinical knowledge — and Run 1 showed clear signs of overfitting rather than generalization.** The near-perfect `rewards/accuracies` and unboundedly climbing `rewards/margins` in Run 1, on only 34 examples over 3 epochs, is a textbook overfitting signature: the model likely memorized the specific training pairs rather than learning a transferable "recognize and flag dangerous clinical errors" behavior.

Growing the dataset (34 → 97 pairs) and reducing to 1 epoch in Run 2 produced a **directionally better, less extreme training signature** and a **qualitatively improved response** on the held-out test case — evidence that more diverse data helps. However, 97 pairs remains 2-3 orders of magnitude below the scale (typically thousands to tens of thousands of preference pairs) generally used for DPO fine-tuning to reliably generalize. The base model's own pretrained medical knowledge — not the fine-tuning — is doing most of the work in both adapters' correct answers.

This is treated as a legitimate, informative result rather than a failure: the pipeline (rubric-based scoring → automated flaw generation → validated preference pairs → QLoRA/DPO training) works correctly end to end, and the honest limiting factor (dataset scale) is now clearly identified rather than papered over.

## What would be needed to go further

- **Dataset scale**: hundreds to low thousands of validated pairs, not tens — the single biggest lever, and the most costly to pull given the manual case-writing and API costs involved.
- **A proper held-out test set**: scoring held-out cases through the existing judge/rubric (rather than a single manual read-through) to get a quantitative, repeatable comparison across model versions.
- **Deterministic generation for comparisons** (`do_sample=False`) rather than sampled outputs, to make before/after comparisons reproducible rather than subject to sampling variance.
- **A tracking mechanism** in `build_dpo_dataset()` to avoid reprocessing already-converted cases, which would make dataset growth more efficient at larger scale.

## Status

This phase is considered a complete, honestly-evaluated first attempt. Given project priorities (breadth across full-stack + AI/ML work, limited time before other commitments), further dataset scaling is deprioritized for now in favor of moving on to the next roadmap phase (RAG). The findings and next steps above are documented here so this can be picked back up with a clear starting point later.