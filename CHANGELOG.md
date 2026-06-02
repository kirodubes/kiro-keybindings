# Changelog

All notable changes to **kiro-keybindings** are documented here.

## 2026.06.02

### What Changed
- **XFCE support in the app's auto-detection.** The cheatsheet now recognizes an XFCE session and
  opens `~/.config/xfce4/keybindings.txt` — the file (and the Ctrl+Super+S launch binding) were
  already shipped in `kiro-xfce`, but the app couldn't find them because its WM table was TWM-only.
  XFCE is a shipped Kiro default, so it now gets the same one-keystroke cheatsheet as the 7 TWMs.
- **`--dev` flag + bundled sample.** `kiro-keybindings --dev` loads a bundled
  `sample.keybindings.txt` (forced, overriding detection — below `--file`), so the app launches on
  *any* box with no generated file and no matching WM. Useful for development, theme work, `--shot`
  gallery renders, and testing on environments the app doesn't yet detect (e.g. a Wayland session).
  The window chip reads `sample (dev)`.
- **Plasma (KDE) support scaffolding — verified on a real Plasma Wayland VM.** App detects
  `kwin_wayland`/`kwin_x11` → `plasma` and runs natively on Wayland (confirmed visually). Ships a
  generic `kiro-keybindings.desktop` so it appears in every desktop's application menu (and can be
  bound as a launch shortcut by the user). Resilient data-file lookup: per-user
  `~/.config/<wm>/keybindings.txt` first, else a bundled
  `/usr/share/kiro-keybindings/<wm>.keybindings.txt` (read-only, package-owned — can't drift, no skell).
  **No auto global keybinding is shipped for Plasma** — see the research note below; deferred to a
  future kiro-plasma spin.
- **Light themes + dark/light toggle.** Added five light themes (Kiro Light, Arc-Light, Catppuccin
  Latte, Gruvbox Light, Solarized Light) alongside the seven dark ones. A monochrome ☾/☀ toggle in
  the header flips the swatch row between the dark and light lists; the choice persists *per mode*
  (`themeDark`/`themeLight`). Motivation: on a light desktop (e.g. default Plasma) the dark cheatsheet
  clashed — now it can match. Modelled on alacritty-tweak-tool's light/dark split.

### Technical Details
- `main.py` — added `"xfwm4": "xfce4"` and `"kwin_wayland"/"kwin_x11": "plasma"` to `WM_MAP`.
  `detect_wm()` matches the running process via `pgrep -x`. Parser/QML unchanged (the
  `keybindings.txt` format is identical across environments).
- `main.py` — `--dev` resolves to the bundled sample *before* `detect_wm()` (so it works even when a
  real WM is detected); `resolve_file()` gained a `dev` param + a `/usr/share` bundled fallback after
  the per-user path; the not-found message now hints at `--dev`.
- Plasma launch shortcut research (verified on the VM, kept for the future spin): KDE needs the
  triple format `_launch=KEY,KEY,Name` in `kglobalshortcutsrc` (single-value registers the action but
  binds no key); the key must avoid Plasma defaults (Super+Ctrl+S is taken by "Toggle stylus mode" —
  Super+K is free); on Wayland `kwin` *is* the shortcut daemon, reads the file at session start, and
  **strips `[services]` entries it doesn't know on logout**. Consequence: an additive per-user
  file-injection (e.g. `kwriteconfig6` at login) gets stripped — only `/etc/skel`-before-first-login
  or the kglobalaccel D-Bus API persist. Since Plasma is a not-yet-shipped spin and neither path is
  low-maintenance, the auto-keybinding is **deferred**; the app stays menu-launchable on Plasma.

### Files Modified
- `usr/share/kiro-keybindings/main.py`
- `usr/share/kiro-keybindings/sample.keybindings.txt` (new — bundled demo, ships with the package)
- `usr/share/applications/kiro-keybindings.desktop` (new — menu entry + launch-shortcut target)

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
