# GitHub Copilot Instructions - Python CLI Project

## 1. Environment & Package Management
- **Language:** Python 3.11+
- **Package Manager:** pip (dependencies tracked in `requirements.txt` or `setup.py`)
- **Environment:** Run within a standard `venv` virtual environment.
- **Coding Style & Linting:** Ruff (strict, PEP 8 aligned, formatting via Ruff format)
- **Type Checking:** Mypy (strict type hints required)
- **Testing:** Pytest (for unit and integration tests)

## 2. CLI Architecture & Coding Standards
- **CLI Framework:** Prefer `argparse` (standard library) or `click` for command-line interface argument parsing.
- **Naming Conventions:** 
  - Functions, variables, and file names: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Type Hints:** Always provide explicit type hints for function signatures, arguments, and return values (e.g., `def parse_arguments(args: list[str]) -> argparse.Namespace:`).
- **Modern Syntax:** 
  - Use `|` instead of `Optional` or `Union` from the `typing` module.
  - Use modern collection type hints (e.g., `list[str]`, `dict[str, int]`) instead of `List`, `Dict`.

## 3. Terminal I/O & Error Handling
- **Exit Codes:** Always return explicit system exit codes using `sys.exit()`. 
  - `0` for success.
  - `1` for general runtime errors.
  - `2` for invalid CLI usage/arguments.
- **Standard Streams:** Write normal output to `sys.stdout`. Write errors, warnings, and logs exclusively to `sys.stderr`.
- **Exceptions:** Never use bare `except:`. Catch specific errors (e.g., `FileNotFoundError`, `ValueError`).
- **User Interrupts:** Gracefully handle `KeyboardInterrupt` (Ctrl+C) to prevent raw Python stack traces in the terminal.
- **Rich Output:** If colorized or structured terminal output is needed, prefer `rich` or standard ANSI escape codes.

## 4. Documentation
- **Docstrings:** Use Google-style docstrings for public classes and functions.
- **CLI Help:** Every command, argument, and option must have a clear, concise `help` string.

## 5. Testing CLI Applications
- **Framework:** Write unit and integration tests using `pytest`.
- **CLI Testing:** Use `pytest` to mock inputs and capture `stdout`/`stderr` using pytest's `capsys` fixture.

---

## DO / DON'T Examples

### Good (DO)
```python
import sys
import argparse

def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(description="A clean CLI tool.")
    parser.add_argument("--file", type=str, required=True, help="Path to the input file")
    
    args = parser.parse_args(argv)
    
    try:
        # Business logic here
        print(f"Processing: {args.file}", file=sys.stdout)
        return 0
    except FileNotFoundError as e:
        print(f"Error: The file '{args.file}' was not found.", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        return 130

if __name__ == "__main__":
    sys.exit(main())
```

### Bad (DON'T)
```python
import sys

# BAD: No type hints, using sys.argv directly without parser, bare except, raw print for errors, no exit code
def main():
    try:
        file = sys.argv[1]
        # logic
    except:
        print("An error occurred!") # BAD: raw print to stdout, no custom exit code
```
