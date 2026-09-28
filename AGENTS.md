# Repository Guidelines

## Project Structure & Module Organization

The application is a compact Windows desktop widget. `jalawidget.py` contains the complete Tkinter interface, Jalali date formatting, window movement, and shutdown behavior. `jalawidget.spec` is the PyInstaller configuration used to create the executable. Treat `build/` as temporary PyInstaller output and `dist/jalawidget.exe` as the packaged artifact; do not edit either by hand. There is currently no dedicated test directory or asset directory.

## Setup, Run, and Build Commands

Use Python 3 on Windows. Tkinter and `ctypes` come from the standard library; install the external runtime and packaging dependencies with:

```powershell
python -m pip install jdatetime pyinstaller
```

Run the widget directly during development:

```powershell
python .\jalawidget.py
```

Build the windowed executable using the checked-in specification:

```powershell
python -m PyInstaller --clean .\jalawidget.spec
```

The finished binary is written to `dist\jalawidget.exe`. For a quick syntax check, run `python -m compileall .\jalawidget.py`.

## Coding Style & Naming Conventions

Follow PEP 8 with four-space indentation. Use `snake_case` for functions, methods, variables, and dictionaries; use `PascalCase` for classes such as `PersianDateWidget`; reserve uppercase names for constants. Keep Persian display text in UTF-8 and preserve the existing right-to-left wording. Prefer small methods for UI actions and keep widget styling values near widget construction. New imports should be explicit and grouped with standard-library imports before third-party imports.

## Testing Guidelines

No automated test framework is configured. Before submitting a change, run the syntax check and launch the widget manually. Verify the Persian date, font fallback, bottom-right placement, drag behavior, right-click close action, and DPI scaling on Windows. If adding tests, place them in `tests/`, name files `test_*.py`, and use `pytest`.

## Commit & Pull Request Guidelines

Git history is not included in this checkout, so no repository-specific commit convention can be inferred. Use short, imperative subjects such as `Fix widget placement on scaled displays`. Keep commits focused. Pull requests should explain the user-visible change, list manual verification performed, and include a screenshot for visual or layout changes. Link any relevant issue and call out new dependencies or packaging changes.

## Generated Files & Configuration

Do not commit routine changes under `build/`. Rebuild `dist/jalawidget.exe` only when a release artifact is intentionally required. Never add local virtual environments, caches, or machine-specific font files.
