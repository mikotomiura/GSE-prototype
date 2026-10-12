# Environment of the main computation

- Python 3.11.9 (64-bit, Windows 11; the reference machine has 16 logical processors).
- Packages: `requirements.txt` (numpy 2.2.6 and scikit-learn 1.5.2 as fixed in `config.json` `tools`; scipy, joblib and threadpoolctl are installed as dependencies of scikit-learn and are not imported by the scripts).
- A virtual environment outside the repository:

```bash
py -3.11 -m venv ~/.venvs/pkm-main
~/.venvs/pkm-main/Scripts/python -m pip install -r requirements.txt
```

- The check on synthetic logs before fixing (`scripts/synthetic_check.py`) was run with numpy 2.4.6; its output is identical under the pinned environment (checked with `run.sh`).
- The KeyTAR model (attacker A4) needs a GPU build of PyTorch; its version is recorded here when the model is acquired.
