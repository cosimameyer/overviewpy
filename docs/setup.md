# Development setup

This guide walks you through everything you need to get `overviewpy` running locally so you can contribute code, tests, or documentation.

## Required tools

| Tool | Purpose | Install |
|------|---------|---------|
| [Python](https://www.python.org/) ≥ 3.9 | Runtime | [python.org](https://www.python.org/downloads/) or via your system package manager |
| [uv](https://docs.astral.sh/uv/) | Package & virtual environment manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| [Git](https://git-scm.com/) | Version control | [git-scm.com](https://git-scm.com/downloads) |
| [GitHub CLI](https://cli.github.com/) *(optional)* | Open PRs, review issues from the terminal | `brew install gh` / [cli.github.com](https://cli.github.com/) |

## Fork and clone

1. Click **Fork** on the [overviewpy repository](https://github.com/cosimameyer/overviewpy) to get your own copy.
2. Clone your fork locally:

    ```console
    git clone https://github.com/<your-username>/overviewpy.git
    cd overviewpy
    ```

3. Add the upstream remote so you can pull in future changes:

    ```console
    git remote add upstream https://github.com/cosimameyer/overviewpy.git
    ```

## Install dependencies

`uv` handles creating the virtual environment and installing all dependencies in one step:

```console
uv sync --group dev
```

This installs the package in editable mode together with all development dependencies (pytest, jupyter, sphinx, etc.). The virtual environment is created automatically at `.venv/`.

To also install the optional documentation dependencies:

```console
uv sync --group dev --extra docs
```

## Run the tests

```console
uv run pytest tests/
```

To also generate a coverage report:

```console
uv run pytest tests/ --cov=overviewpy --cov-report=term-missing
```

## Build the docs locally

The documentation site is built with [MkDocs](https://www.mkdocs.org/) and the [Material theme](https://squidfunk.github.io/mkdocs-material/). To preview it locally:

```console
uv run mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. The site reloads automatically when you save a file.

## Work on a feature or bug fix

```console
# Create a branch
git checkout -b name-of-your-bugfix-or-feature

# ... make your changes ...

# Run the tests
uv run pytest tests/

# Commit and push
git add .
git commit -m "short description of change"
git push origin name-of-your-bugfix-or-feature
```

Then open a pull request from your fork on GitHub. See [Contributing](contributing.md) for the full guidelines.

## Keeping your environment up to date

After pulling new changes from upstream, re-run `uv sync` to pick up any dependency changes:

```console
git pull upstream main
uv sync --group dev
```

## Working with Jupyter notebooks

The example notebook in `docs/example.ipynb` is executed as part of the docs build. To open it locally:

```console
uv run jupyter notebook docs/example.ipynb
```
