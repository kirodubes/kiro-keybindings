# Changelog

All notable changes to **kiro-keybindings** are documented here.

## 2026.06.02

### What Changed
- **XFCE support in the app's auto-detection.** The cheatsheet now recognizes an XFCE session and
  opens `~/.config/xfce4/keybindings.txt` — the file (and the Ctrl+Super+S launch binding) were
  already shipped in `kiro-xfce`, but the app couldn't find them because its WM table was TWM-only.
  XFCE is a shipped Kiro default, so it now gets the same one-keystroke cheatsheet as the 7 TWMs.

### Technical Details
- `main.py` — added `"xfwm4": "xfce4"` to `WM_MAP`. `detect_wm()` matches the running `xfwm4`
  process via `pgrep -x` and resolves `~/.config/xfce4/keybindings.txt`. Parser/QML unchanged
  (the `keybindings.txt` format is identical across environments).

### Files Modified
- `usr/share/kiro-keybindings/main.py`

## 2026.06.01

### What Changed
- Initial version of the **Kiro Keybindings** cheatsheet: a slick PySide6/QML app that
  auto-detects the running tiling window manager, locates that environment's
  `~/.config/<wm>/keybindings.txt`, and renders it as a searchable, color-coded 3-column cheatsheet.
- Goal: turn Kiro's many desktops into a selling point — *"learn any Kiro desktop in one keystroke."*
- **7 live-switchable themes** (Kiro default, Arc-Dark, Nord, Dracula, Gruvbox, Catppuccin, Neon)
  via header swatches; the choice persists across launches (`QSettings`).
- **Mono typographic keycaps** (no button chips) with `rule` category headers.
- The window fills opaque, **edge-to-edge** (no transparent margin) — fixes a transparent border that
  showed under both picom and fastcompmgr (and would affect every WM).
- v1 wired into **ohmychadwm** (Super+K + Learn/Trigger/System menu entries now open this app;
  the old `show-keybindings.sh` is kept in place as a fallback).

### Technical Details
- `main.py` — WM auto-detection (`pgrep -x`, env fallback), arg parsing, `Backend` QObject
  exposing filtered sections to QML; `--theme/--header/--keys` flags; offscreen `--shot PATH`
  renders a theme to PNG (used to build comparison galleries).
- `parser.py` — parses the shared `keybindings.txt` format (section dividers `── N. Name ──`,
  `combo  description` lines) into sections with per-token modifier classification.
- QML UI — `Cheatsheet.qml` holds the 7-theme dict, `QtCore.Settings` persistence, and the swatch
  switcher; `BindingRow.qml`/`KeyCap.qml` render typographic keys (theme colors/font passed down).
- Uses only Qt6 modules already shipped on the ISO; net-new dep is `pyside6` (pulls `shiboken6`).

### Packaging / placement
- Source repo lives in `~/KIRO/kiro-keybindings` (Kiro side of the kirodubes/erikdubois org split);
  intended GitHub home `github.com/kirodubes/kiro-keybindings`.
- Package build dir `KIRO-PKG-BUILD/kiro-keybindings/` (PKGBUILD + build.sh) builds into
  **nemesis_repo** — the user repo enabled on installed systems — so the app ships *and* updates.

### Files Modified
- `usr/bin/kiro-keybindings`, `usr/share/kiro-keybindings/{main.py,parser.py,Cheatsheet.qml,BindingRow.qml,KeyCap.qml}`, `usr/share/kiro-keybindings/assets/logo.png`, `LICENSE`
- `KIRO-PKG-BUILD/kiro-keybindings/{PKGBUILD,build.sh,readme.install}`
- ohmychadwm: `sxhkd/sxhkdrc`, `menu/ohmychadwm-menu.sh`
