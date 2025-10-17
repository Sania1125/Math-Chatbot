
# Math-Chatbot

A small interactive math chatbot that safely evaluates arithmetic expressions and some functions.

## Features
- Safe evaluation using Python AST (whitelisted operators and functions)
- Supports: +, -, *, /, **, sqrt(), pow(), sin(), cos(), tan(), log()/ln(), exp(), abs(), floor(), ceil()
- Percentage literals like `50%` (interpreted as `0.5`)
- Statistics: `mean(...)`, `avg(...)`, `median(...)` (accepts multiple args or a single list)
- Structured JSON output using the `--json` CLI flag

## Usage

Run interactively:

```powershell
python "c:\Users\BZU\OneDrive\Desktop\vs code files\Math-Chatbot\python.py"
```

Run with JSON structured responses:

```powershell
python "c:\Users\BZU\OneDrive\Desktop\vs code files\Math-Chatbot\python.py" --json
```

Examples you can type at the prompt:
- `4 + 5 * 3`
- `sqrt(9)`
- `pow(2,3)` or `2**3`
- `50% * 200`
- `mean(1,2,3)` or `mean([1,2,3])`
- `median(1,3,2,4)`

## Tests

Run the unit tests with pytest (install first if needed):

```powershell
python -m pip install -r requirements.txt  # optional
python -m pip install pytest
python -m pytest -q
```

## CI / Status

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` which runs the test suite on push and pull requests to `main` across multiple Python versions.

![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)

Replace `<owner>` and `<repo>` with your GitHub username and repository name to make the badge link work.

## Installation (recommended)

1. Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies (if you create `requirements.txt`) or at least pytest for tests:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt  # if provided
python -m pip install pytest
```

## Contributing

Contributions are welcome. A good workflow:

1. Fork the repository and create a feature branch.
2. Run the test suite locally: `python -m pytest -q`.
3. Open a pull request and GitHub Actions will run the tests automatically.

## License

This project is provided as-is for learning and experimentation.
