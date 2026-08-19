# Repository Guidelines

## Project Overview
This repository is a Red-DiscordBot cog for Bible verse lookup, search, and note management. The main cog lives in `bible/bible.py`; it reads bundled verse JSON, formats Discord embeds, and stores user notes in Redbot `Config`.

## Architecture & Data Flow
- Commands are defined on `Bible(commands.Cog)` in `bible/bible.py`.
- `bible lookup` parses a book reference, normalizes translation/book names, resolves a JSON file under `bible/data/<translation>/`, then paginates verse text into embeds.
- `memory add/remove/list` read and mutate the global `Config` `Notes` list.
- `search` and `isearch` scan verse JSON files under `bible/data/akjv/` and build paginated embed output.
- Helper functions at module scope handle translation detection, book normalization, metadata lookup, and verse offsets.

## Key Directories
- `bible/` — cog package.
- `bible/bible.py` — cog implementation and helper functions.
- `bible/data/` — bundled Bible data by translation (`akjv/`, `asv/`, `bsb/`) plus `sources/` archives.
- `bible/tests/` — pytest unit tests.
- `README.md` — Discord install/load and command examples.

## Development Commands
- Create venv (Python 3.11 via uv): `uv venv .venv -p 3.11`
- Install dependencies: `uv pip install -r bible/requirements.txt pip --python .venv/bin/python`
- Run tests: `.venv/bin/python -m pytest bible/tests/`
- Preview a lookup reply: `PYTHONPATH=. .venv/bin/python scripts/preview_lookup.py "Genesis 1:1"`
- Load in Redbot: `.repo add anvil https://github.com/fight-the-good-fight/redbot-bible-cog`, then `.cog install anvil bible`, `.load bible`
- Update in Redbot: `.cog update`, `.restart`

## Code Conventions & Common Patterns
- Keep command handlers async and inside `Bible`.
- Prefer small pure helpers for parsing/normalization; current helpers include `get_book_info`, `detect_translation`, `fix_book_name`, and `get_verse_offset`.
- Use lower-case translation keys (`akjv`, `asv`, `bsb`) and normalized book keys (`songofsolomon`, `revelation`, etc.).
- Preserve existing Discord UX patterns: `pagify(...)`, `menu(...)`, and green embeds.
- Notes are stored as dicts with `number`, `book`, `chapter`, `verse`, `note`; keep that shape stable.
- Error handling is intentionally user-facing: `CommandNotFound` is ignored, `AttributeError`/`ValueError` get a friendly message, and unexpected exceptions are re-raised.
- `bible/.vscode/settings.json` prefers `ms-python.autopep8` formatting in the editor, but the repo has no dedicated formatter config.

## Important Files
- `bible/bible.py` — commands, parsing, lookup, search, and note storage.
- `bible/__init__.py` — Redbot entry point (`setup(bot)`).
- `bible/info.json` — cog metadata for Redbot.
- `bible/requirements.txt` — runtime/test dependencies.
- `bible/tests/bible_test.py` — current unit coverage for helper functions.
- `README.md` — operator/user-facing install and usage notes.
- `testme.py` — scratch regex experiment; not part of the cog.

## Runtime/Tooling Preferences
- This is a Python/Red-DiscordBot project, not a standalone app.
- Python 3.11 required: `Red-DiscordBot==3.5.24` declares `requires_python >=3.8.1,<3.12`.
- The venv is uv-managed, not Homebrew: Homebrew python paths move on upgrade/migration and break the venv's interpreter symlink (happened 2026-08); uv keeps builds at a stable path (`~/.local/share/uv/python/cpython-3.11-macos-aarch64-none`).
- `uv venv` omits pip; install it explicitly or the pytest chain fails on `import pip`.
- Runtime dependency list is minimal: `Red-DiscordBot==3.5.24`, `future`, `pytest`.
- The code imports `discord`, so the Redbot/Discord environment must be available when importing the cog.
- There is no `pyproject.toml`, `setup.py`, or package manager metadata; deps come from `bible/requirements.txt` via `uv pip` (or plain `pip`).
- Keep `.vscode` and `__pycache__` out of version control (`.gitignore`).

## Testing & QA
- Primary test framework: `pytest`.
- Existing tests cover helper behavior in `bible/tests/bible_test.py`; there are no command-level integration tests in this repo.
- Add focused unit tests around parsing and metadata helpers when changing behavior.
- Verify with `.venv/bin/python -m pytest bible/tests/`.
- If imports fail, confirm the environment includes Redbot/discord dependencies before changing code.

## Critical Rules
- Follow directions exactly: when user says "not making changes", do NOT modify any files
- No subagents
- When in doubt about scope, ask for clarification before proceeding
- Prefer small files, targeted by category
- NEVER assume "checking for updates" means "apply updates"
- Surgical edits
- Always prioritize user's explicit constraints over default behavior
- Stay on topic and in scope of task
- When you write a file or need to modify it, edit it, do not write it from scratch
- If you need to overwrite a file, create temporary file first, make sure it is correct then replace the target file, do not delete the real file unless these conditions are met
- When editing a file, make sure you are not just inserting the same block multiple times by accident
- helpers go into their own small file
- test files import the helpers as needed
- verification of test code AFTER the tests have been written.
- always open a branch when making changes
- when opening a pull request make it a draft
