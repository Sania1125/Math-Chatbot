# Math-Chatbot

A small interactive math chatbot that **safely** evaluates arithmetic, basic functions, and simple statistics — now with degree/radian control, JSON output, and better tests.

![status](https://img.shields.io/github/actions/workflow/status/<owner>/<repo>/ci.yml?branch=main)

---

## Why this exists

- **Safe by design**: Uses a tight AST whitelist. No attributes, no imports, no comprehensions.
- **Friendly**: Works interactively or one-shot with `-c`.
- **Flexible**: Percentages (`50%` → `0.5`), degree symbol (`60°`), or `--angle deg`.
- **Stats built-in**: `mean/avg`, `median`, `min/max`, `sum`, `var`, `std`.

---

## Quickstart

```bash
# create & activate venv (recommended)
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# install
pip install -e .[dev]

# interactive
mathbot

# one-shot
mathbot -c "4 + 5 * 3"
mathbot -c "sin(30)" --angle deg
mathbot -c "50% * 200"
mathbot -c "median(1,3,2,4)"
mathbot -c "var([1,2,3])"
mathbot -c "factorial(5)"
