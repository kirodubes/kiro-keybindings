# kiro-keybindings — project notes

PySide6/QML cheatsheet that auto-detects the running TWM and renders its
`~/.config/<wm>/keybindings.txt`. Presentation layer only — the `keybindings.txt`
files (made by `/kiro-create-keybindings`) are the source of truth.

## Layout
- `usr/bin/kiro-keybindings` — launcher (execs the Python entry).
- `usr/share/kiro-keybindings/main.py` — WM detection, `Backend` QObject, QML engine.
- `usr/share/kiro-keybindings/parser.py` — keybindings.txt → sections.
- `usr/share/kiro-keybindings/*.qml` — UI (Cheatsheet root, BindingRow, KeyCap).
- `usr/share/kiro-keybindings/assets/logo.png` — Kiro brand logo (do not recolor).

## Conventions
- Python: ruff clean, max line 120.
- The shared `keybindings.txt` format is identical across all 7 TWMs — keep the parser generic.
- Brand colors: blue `#0195F7`→`#0245B7`, green `#2FC328`; dark bg `#0F172A`/`#020617`.

## Status
v1 wired into ohmychadwm; app also detects XFCE (`xfwm4` → `~/.config/xfce4/keybindings.txt`, launch
on Ctrl+Super+S, both shipped via kiro-xfce). Phase 2 remaining: wire the other 6 TWMs' launch
entries, nemesis_repo package (`pyside6` dep) so it actually ships + updates on installed systems.
