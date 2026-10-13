# Environment of the main computation

- Python 3.11.9 (64-bit, Windows 11; the reference machine has 16 logical processors).
- Packages: `requirements.txt` (numpy 2.2.6 and scikit-learn 1.5.2 as fixed in `config.json` `tools`; scipy, joblib and threadpoolctl are installed as dependencies of scikit-learn and are not imported by the scripts).
- A virtual environment outside the repository:

```bash
py -3.11 -m venv ~/.venvs/pkm-main
~/.venvs/pkm-main/Scripts/python -m pip install -r requirements.txt
```

- The check on synthetic logs before fixing (`scripts/synthetic_check.py`) was run with numpy 2.4.6; its output is identical under the pinned environment (checked with `run.sh`).
- The KeyTAR model (attacker A4) runs in a second virtual environment, separate from the main computation (check 6, 2026-10-13): Python 3.11.9, PyTorch 2.7.1+cu128 (CUDA 12.8; the GPU is an NVIDIA GeForce RTX 5060 Ti, 16 GB, compute capability 12.0, driver 610.88), transformers 4.49.0 (the version the artifact pins), accelerate 1.4.0, datasets 3.3.2 (used only to read the format of the released training data). Full list: `requirements-keytar.txt`.

```bash
py -3.11 -m venv ~/.venvs/pkm-keytar
~/.venvs/pkm-keytar/Scripts/python -m pip install torch==2.7.1 --index-url https://download.pytorch.org/whl/cu128
~/.venvs/pkm-keytar/Scripts/python -m pip install transformers==4.49.0 accelerate==1.4.0 datasets==3.3.2
```

- pip-audit 2.10.1 on `requirements-keytar.txt` (2026-10-13) lists known advisories for transformers 4.49.0 (37), torch 2.7.1 (10), accelerate 1.4.0, datasets 3.3.2 and fsspec 2024.12.0 (1 each). transformers is kept at the artifact's version because the default generation (group beam search with a diversity penalty) is the artifact's setting. The venv only loads the local checkpoint whose SHA-256 is recorded (`data.md`), offline, with no server; PyTorch 2.7 loads `pytorch_model.bin` with `weights_only=True`.
