# Local Fine-Tuning Environment Setup

This documents how the local QLoRA/DPO fine-tuning environment was set up, including the specific issues hit along the way. Written so this doesn't have to be re-derived from scratch later.

**Hardware:** NVIDIA RTX 3060 (12GB VRAM), Windows 10/11.

## Why a separate environment

This project's core eval framework (`automate_pipeline.py`, `dpo_pipeline.py`, etc.) only needs `pyyaml`, `python-dotenv`, and `anthropic` — lightweight API-calling dependencies. The fine-tuning stack (`torch`, `unsloth`, `trl`, `peft`, `bitsandbytes`, `transformers`) is much heavier and has strict version interdependencies, so it lives in its own virtual environment (`ft-env`) rather than alongside the core framework's dependencies.

## 1. Confirm GPU driver

```
nvidia-smi
```
Confirms the NVIDIA driver is installed and shows the max CUDA version the driver supports (this is a ceiling, not what's actually installed — PyTorch bundles its own CUDA runtime separately).

## 2. Python version — must be 3.10, 3.11, or 3.12

**Gotcha:** This machine's default Python was 3.14, which **Unsloth does not support** (as of writing). Rather than replacing the system Python, installed a second version specifically for this environment using Python's newer Install Manager tool:

```
winget install 9NQ7512CXL7T   # installs the Python Install Manager
py install 3.11               # installs Python 3.11 specifically, alongside 3.14
py list                       # confirms both versions are available
```

## 3. Create the virtual environment (pinned to 3.11)

```
py -3.11 -m venv ft-env
ft-env\Scripts\activate
```

**Gotcha:** PowerShell blocked the activation script by default (`running scripts is disabled on this system`). Fixed once, for this user account only:
```
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Confirm the venv is actually on 3.11 (not the system 3.14) with `python --version` before proceeding.

## 4. Install PyTorch (CUDA build)

Get the exact current install command from https://pytorch.org/get-started/locally/ (Stable, Windows, Pip, Python, newest CUDA version listed). At time of setup:
```
python -m pip install torch==2.12.1 torchvision==0.27.1 --index-url https://download.pytorch.org/whl/cu130
```

**Gotcha — pin the exact version.** Installing without a version pin (`torch torchvision`, no `==`) pulled the newest release (2.14.0), which is *too new* for Unsloth (`unsloth requires torch<2.13.0`). Always pin to a version Unsloth's current release actually supports — check the error message from `pip install unsloth` if unsure.

**Gotcha — CPU vs CUDA build.** More than once, installing an unrelated package silently downgraded `torch` back to the plain CPU-only build from PyPI's default index (no `--index-url` needed to trigger this — any package listing `torch` as a dependency can do it). Symptom: `torch.__version__` shows a `+cpu` suffix, and `torch.cuda.is_available()` returns `False`. **Fix:** re-run the pinned install command above with `--force-reinstall`, and do it *last*, after all other packages, so nothing can silently override it again. Always spot-check `torch.__version__` after installing anything new in this environment.

Verify:
```
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```
Should show a version WITHOUT `+cpu`, and `True`.

## 5. Windows-specific: Visual Studio Build Tools + Triton

- Install "Build Tools for Visual Studio" (not the full IDE) with the "Desktop development with C++" workload, including the Windows 10/11 SDK option.
- Install the Windows fork of Triton (the standard `triton` package is Linux-only):
```
python -m pip install -U triton-windows
```

**Note:** bitsandbytes' own diagnostic (`python -m bitsandbytes`) reports `triton: not found` even when `triton-windows` is correctly installed — this is a package-name mismatch in the diagnostic itself, not a real problem. Confirm it's actually working with:
```
python -c "import triton; print(triton.__version__)"
```

## 6. Install Unsloth

```
python -m pip install unsloth
```
This pulls in `trl`, `peft`, `accelerate`, and `transformers` automatically.

**Gotcha — fsspec version conflict.** `datasets` requires `fsspec<=2025.9.0`, but installing torch pulled in a newer version. Fixed with:
```
python -m pip install "fsspec<=2025.9.0"
```

## 7. Full verification

```
python -m bitsandbytes
```
Should end with `SUCCESS!`, show a CUDA-enabled PyTorch version (no `+cpu`), and report a `CUDA_VERSION` and compute capability (e.g. `(8, 6)` for Ampere/RTX 30-series).

```
python -c "from unsloth import FastLanguageModel; print('Unsloth loaded successfully')"
```
Should print the success message after Unsloth's own startup banner and patching messages (some deprecation warnings from PyTorch internals on import are normal and not a problem).

## Final confirmed working versions

| Package | Version |
|---|---|
| Python | 3.11.9 |
| torch | 2.12.1+cu130 |
| torchvision | 0.27.1+cu130 |
| triton-windows | 3.8.0.post28 |
| bitsandbytes | 0.50.2 |
| unsloth | 2026.9.9 |
| transformers | 5.5.0 |
| trl | 0.24.0 |
| peft | 0.21.0 |
| accelerate | 1.15.0 |

## Next step

With the environment confirmed working, the next phase is writing the actual training script: loading a base model (Mistral-7B-Instruct or Llama-3-8B-Instruct) in 4-bit via Unsloth, formatting `data/dpo_training_data.jsonl` for `DPOTrainer`, and running a first QLoRA/DPO fine-tuning pass.