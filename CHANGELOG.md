# Changelog

All notable changes to **kiro-keybindings** are documented here.

## 2026.07.06

### What Changed
- **Added `scroll` and `miracle-wm` to `WM_MAP`.** Both KIROTUX editions already ship a
  `keybindings.txt` but were undetectable. `kiro-scroll` ships **scroll** (PaperWM-style sway
  fork, AUR `sway-scroll`); the installed binary is `scroll` and hardcodes `~/.config/scroll/`.
  `kiro-miracle` is the odd one out — a **Mir-based** tiler (AUR `miracle-wm-git`, vendored into
  `nemesis_repo`); binary and config dir are both `miracle-wm`.

### Files Modified
- `usr/share/kiro-keybindings/main.py`

## 2026.07.01

### What Changed
- **Added niri to `WM_MAP`.** `kiro-niri` and `kiro-ohmyniri` both shipped a
  `~/.config/niri/keybindings.txt`, but the app had no `niri` entry at all — `Super+Ctrl+S` on
  either edition showed "Could not detect a supported desktop or window manager" instead of the
  cheatsheet. One `"niri": "niri"` entry covers both: same process name, same config path,
  regardless of which edition's shell (noctalia vs waybar) is running underneath.
- **Added the other six KIROTUX Wayland editions to `WM_MAP`:** wayfire, sway, river, labwc,
  dwl, mango. Same gap as niri — every one of them already ships a `keybindings.txt`, but none
  were detectable. Verified the actual installed binary names via `pacman -Fl` before wiring
  them: `kiro-sway` ships **swayfx**, whose package installs the binary as `sway` (not
  `swayfx`); `kiro-mango`'s package is `mangowm` (upstream `mangowc`), but the binary is `mango`.
  All seven KIROTUX `keybindings.txt` files parse cleanly with `parser.parse()`.

### Files Modified
- `usr/share/kiro-keybindings/main.py`

## 2026.06.30

### What Changed
- **Export the cheatsheet to HTML / PDF from inside the app.** Added two pill buttons (**HTML**,
  **PDF**) to the header. Each regenerates that format from the *currently displayed*
  `keybindings.txt`, writes it next to the source file, and opens it. Previously the HTML/PDF
  were only ever produced out-of-band by `/kiro-keybindings-all-twms-xfce`, so they went stale
  the moment a binding changed — now the user can regenerate a fresh copy on demand.
- **One source of truth for the render logic.** The HTML template + headless-Chromium PDF
  rendering now live in the shipped app (`exporter.py`). The local `~/.bin/kiro-keybindings-html.py`
  was reduced to a thin shim that imports it, so the template and PDF code can no longer drift
  between the GUI and the batch generator.

### Technical Details
- New `usr/share/kiro-keybindings/exporter.py` — ported from `~/.bin/kiro-keybindings-html.py`.
  Public entry `export(txt_path, fmt, out_dir=None) -> Path` (`fmt` ∈ `html`/`pdf`; pdf renders
  the HTML first then prints it). Writes next to the source txt, falling back to `~/` when that
  dir is read-only (bundled/`--dev` case). Two improvements over the original: the logo is read
  live from `assets/logo.png` and base64-embedded (no more hard-coded data-URI blob that could
  drift from the app logo), and `vivaldi`/`vivaldi-stable` were added to the browser probe list
  (Kiro ships Vivaldi).
- `main.py` — `Backend` now takes the resolved source path; added `exportFinished(bool,str,str)`
  signal, `exportBusy` property, and an `export(fmt)` slot that runs the render in a **daemon
  thread** (house rule: never run a subprocess from a GUI callback) then `xdg-open`s the result.
  New `appShot` context property hides the export UI during `--shot`.
- `Cheatsheet.qml` — two header pills via a `Repeater`, styled like the existing mode toggle;
  disabled + dimmed while `exportBusy`; a bottom toast (wired to `exportFinished`) shows
  "Generating…" then the saved path or the error, auto-clearing after 4.5 s. Hidden when `appShot`.
- `~/.bin/kiro-keybindings-html.py` — now a shim that adds the dev app dir to `sys.path` and
  calls `exporter._cli()`; `kiro-keybindings-all.sh` and `/kiro-keybindings-all-twms-xfce` keep
  working unchanged.
- Verified: shim produces valid HTML (logo embedded) + PDF (`%PDF`, 724 KB) from a real
  `keybindings.txt`; QML loads clean offscreen; both pills render in a live windowed run.

### Files Modified
- `usr/share/kiro-keybindings/exporter.py` (new)
- `usr/share/kiro-keybindings/main.py`
- `usr/share/kiro-keybindings/Cheatsheet.qml`
- `~/.bin/kiro-keybindings-html.py` (→ shim, outside this repo)
- `CLAUDE.md`

### Plasma support: fix the data path + unhide the launcher

#### What Changed
- **The cheatsheet now works on KDE Plasma.** `detect_wm()` already mapped `kwin_wayland`/`kwin_x11`
  to `plasma`, but `resolve_file()` then looked for `~/.config/plasma/keybindings.txt` (TWM-style
  `<wm>` subdir) while kiro-plasma-keybindings ships the file at the `.config` **root**
  (`~/.config/keybindings.txt`) — so the app never found it and exited "no keybindings found".
  Special-cased Plasma to read the root path.
- **Unhid the launcher on Plasma.** The app's `.desktop` carried `NotShowIn=KDE` (a deliberate
  guard while no Plasma data shipped). Now that the path resolves to a real, fully-populated
  `keybindings.txt`, the launcher is surfaced on Plasma too.

#### Technical Details
- `main.py` — `resolve_file()` branches on `wm == "plasma"` to build `~/.config/keybindings.txt`
  (no `<wm>` subdir); all TWMs keep the `~/.config/<wm>/keybindings.txt` path. The existing bundled
  fallback (`<share>/plasma.keybindings.txt`) is untouched.
- `kiro-keybindings.desktop` — removed the `NotShowIn=KDE;` line and its now-stale comment.

#### Files Modified
- `usr/share/kiro-keybindings/main.py`
- `usr/share/applications/kiro-keybindings.desktop`

### Launch-failure popup: enumerate *why* the cheatsheet didn't open

#### What Changed
- **A GUI popup now explains a failed launch instead of dying silently.** When started from a
  global shortcut or `.desktop`, the app's old `stderr` "no keybindings.txt found" message was
  invisible — the app just appeared broken. It now shows a `QMessageBox` listing the concrete
  cause(s): when **no WM is detected** it prints the live `XDG_CURRENT_DESKTOP`/`XDG_SESSION_TYPE`,
  the full list of known compositors it probed, and a hint to add the new env to `WM_MAP`; when a
  WM **is** detected but has no data it names the environment and the exact paths it checked. This
  is aimed squarely at the Wayland TWMs still to be wired — launching the app on a not-yet-supported
  compositor now tells you exactly what's missing.

#### Technical Details
- `main.py` — `resolve_file()` now returns `(path, reasons)`; `reasons` is a list of human-readable
  failure lines built per case (bad `--file`, undetected WM, detected-but-no-file). New
  `show_launch_error(reasons)` pops a `QtWidgets.QMessageBox` (lazy-imported so the success path
  stays on `QGuiApplication`), falling back to `stderr` on a headless box. Verified: enumerated
  reasons for all three cases; `--dev` success path still renders; ruff clean.

#### Files Modified
- `usr/share/kiro-keybindings/main.py`

## 2026.06.29

### What Changed
- **Hyprland is now detected.** Pressing the keybindings launcher under Hyprland reported "no
  keybindings.txt found for this environment" because the WM auto-detection table had no Hyprland
  entry — so it fell through to None even though `~/.config/hypr/keybindings.txt` ships with
  kiro-hyprland. Added the mapping; the cheatsheet now opens on Hyprland boxes.

### Technical Details
- `main.py` `WM_MAP` — added `"Hyprland": "hypr"`. The compositor's process name is `Hyprland`
  (capital H), matched by the existing `pgrep -x` pass; config dir is `hypr`. `XDG_CURRENT_DESKTOP`
  is empty under Hyprland, so the env fallback can't help — process detection is the load-bearing
  path. Verified live on the Hyprland box: `detect_wm()` returns `hypr` and resolves the real file.

### Files Modified
- `usr/share/kiro-keybindings/main.py`

## 2026.06.15

### What Changed
- **Localized the desktop entry.** Added a translated `Comment` and a new `GenericName`
  ("Keyboard Shortcut Reference") in 14 languages (de, fr, nl, es, it, pt_BR, pt, ru, pl, uk,
  zh_CN, ja, tr, cs). Brand `Name` and technical `Keywords` stay English.

### Technical Details
- `usr/share/applications/kiro-keybindings.desktop` — `GenericName=` + `GenericName[xx]=` block
  after `Name=`; `Comment[xx]=` block after `Comment=`. `desktop-file-validate` clean.

### Files Modified
- `usr/share/applications/kiro-keybindings.desktop`

## 2026.06.05

### What Changed
- **Search now matches category names too.** Previously the live filter only searched each binding's
  key combo and description, so typing a section name (e.g. `workspaces`) returned nothing. Now a
  filter that matches a section's name shows that whole section; otherwise it falls back to the
  per-binding combo/description match as before. Case-insensitive substring, so `work` or `multimon`
  also hit their categories.

### Technical Details
- `main.py` — in `Backend.sections`, short-circuit on `self._filter in section["name"].lower()` to
  emit the full section before falling through to the per-binding row filter.

### Files Modified
- `usr/share/kiro-keybindings/main.py`

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
  generic `kiro-keybindings.desktop` so it appears in TWM/XFCE application menus (hidden on Plasma via
  `NotShowIn=KDE` until a `plasma.keybindings.txt` ships — otherwise it's a dead launcher there).
  Resilient data-file lookup: per-user
  `~/.config/<wm>/keybindings.txt` first, else a bundled
  `/usr/share/kiro-keybindings/<wm>.keybindings.txt` (read-only, package-owned — can't drift, no skell).
  **No auto global keybinding is shipped for Plasma** — see the research note below; deferred to a
  future kiro-plasma spin.
- **Light themes + dark/light toggle.** Added seven light themes (Kiro Light, Arc-Light, Nord Light,
  Dracula Light, Gruvbox Light, Catppuccin Latte, Solarized Light) to match the seven dark ones — so
  the swatch row is the same width in both modes and the toggle stays aligned. A monochrome ☾/☀ toggle
  in the header flips the swatch row between the dark and light lists; the choice persists *per mode*
  (`themeDark`/`themeLight`). Motivation: on a light desktop (e.g. default Plasma) the dark cheatsheet
  clashed — now it can match. Modelled on alacritty-tweak-tool's light/dark split.
- **Window decorations per environment.** Frameless on TWMs (correct — they manage their own
  decorations), but a normal **decorated, titled window on Plasma** ("Kiro Keybindings" title + real
  min/max/close + border). A frameless panel on a full desktop read as broken, and KWin was
  half-decorating it inconsistently; requesting proper decorations fixes it. Verified on the VM.

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
- Themes: `Cheatsheet.qml` gained the seven light theme dicts, split `themeList` into `darkThemes`/
  `lightThemes` with `activeThemeList` keyed off `appSettings.mode`, and added the ☾/☀ toggle; the
  selected-swatch ring now uses the theme title color (a white ring was invisible on light). Fixed a
  latent bug in `KeyCap.qml`: plain non-modifier keycaps were hardcoded to `#E2E8F0` (a dark-theme
  grey) instead of the theme's `key` palette color — invisible on light backgrounds; now theme-driven.
- Decorations: `main.py` exposes `appDecorated = detect_wm() == "plasma"`; `Cheatsheet.qml` selects
  `Qt.Window` when set, else `Qt.FramelessWindowHint | Qt.Dialog`, and now sets the window `title`.
  The `.desktop` gained `NotShowIn=KDE`.

### Files Modified
- `usr/share/kiro-keybindings/main.py`
- `usr/share/kiro-keybindings/Cheatsheet.qml` (light themes + dark/light toggle)
- `usr/share/kiro-keybindings/KeyCap.qml` (theme-driven plain keycap color)
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
