# Contributing

Thanks for your interest in contributing to `leanpub-multi-action`!

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/lykinsbd/leanpub-multi-action.git
   cd leanpub-multi-action
   uv sync
   ```

3. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```

## Development

All tooling runs through [Invoke](https://www.pyinvoke.org/) tasks:

```bash
uv run invoke tests    # ruff, pylint, yamllint, pytest
uv run invoke ruff     # ruff check + format
uv run invoke pylint   # pylint only
uv run invoke yamllint # yamllint only
```

Or run tools directly:

```bash
uv run pytest tests/ -v
uv run ruff check .
uv run ruff format .
```

## Branching

- `main` — stable releases
- `dev` — integration branch, PRs target here
- Feature branches: `feature/<name>`, `docs/<name>`, `fix/<name>`

## Pull Requests

1. Create a branch from `dev`
2. Make your changes
3. Ensure all checks pass: `uv run invoke tests`
4. Ensure pre-commit hooks pass: `uv run pre-commit run --all-files`
5. Use [conventional commits](https://www.conventionalcommits.org/) for commit messages
6. Open a PR against `dev`

## Code Style

- Formatted and linted by [ruff](https://docs.astral.sh/ruff/)
- Type hints required (checked by mypy via pre-commit)
- Docstrings required (Google style)
- Pylint score must remain at 10.00/10
