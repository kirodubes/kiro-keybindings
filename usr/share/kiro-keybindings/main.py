#!/usr/bin/env python
"""Kiro Keybindings — a slick PySide6/QML cheatsheet that auto-detects the running
TWM, finds that environment's keybindings.txt, and renders it with live search."""
import argparse
import os
import subprocess
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow

import exporter
from parser import parse

# Running WM process name (pgrep -x) → ~/.config/<dir>/keybindings.txt
WM_MAP = {
    "ohmychadwm": "ohmychadwm",
    "chadwm": "chadwm",
    # kiro-dusk (bakkeby's dwm fork) — binary and config dir are both "dusk";
    # keybindings.txt lives at ~/.config/dusk/keybindings.txt.
    "dusk": "dusk",
    "i3": "i3",
    "bspwm": "bspwm",
    "qtile": "qtile",
    "awesome": "awesome",
    "leftwm": "leftwm",
    "xfwm4": "xfce4",
    # All Kiro Hyprland editions (kiro-hyprland/-dms/-noctalia/-noctura) run the
    # same "Hyprland" process but are launched with --config pointing at their own
    # ~/.config/<edition>/ folder, where each ships its keybindings.txt. detect_wm()
    # special-cases Hyprland via _hypr_config_dir() to read that per-edition dir from
    # the running process; "hypr" here is only the upstream-default fallback.
    "Hyprland": "hypr",
    # kiro-niri (noctalia-shell) and kiro-ohmyniri (waybar/mako) both run the same
    # "niri" process and ship to the same ~/.config/niri/keybindings.txt — one
    # entry covers both editions.
    "niri": "niri",
    "wayfire": "wayfire",
    # kiro-sway ships swayfx (eye-candy sway fork); its package installs the
    # binary as "sway" (Provides=sway), so the process name is unchanged.
    "sway": "sway",
    # kiro-scroll ships scroll (PaperWM-style sway fork, AUR "sway-scroll"); the
    # installed binary is "scroll" and hardcodes ~/.config/scroll/.
    "scroll": "scroll",
    "river": "river",
    "labwc": "labwc",
    "dwl": "dwl",
    # kiro-mango's compositor package is "mangowm" (upstream project "mangowc"),
    # but the installed binary is "mango" (config lives at ~/.config/mango/).
    "mango": "mango",
    # kiro-miracle is the odd one out — a Mir-based tiler (AUR "miracle-wm-git",
    # vendored into nemesis_repo); binary and config dir are both "miracle-wm".
    "miracle-wm": "miracle-wm",
    "kwin_wayland": "plasma",
    "kwin_x11": "plasma",
}


def _hypr_config_dir():
    """For a running Hyprland, return its per-edition config-dir name (e.g.
    'kiro-hyprland-dms') read from the process's --config argument, or None when
    Hyprland is not running. Falls back to 'hypr' when no --config is present."""
    r = subprocess.run(["pgrep", "-x", "Hyprland"], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    pid = r.stdout.split()[0]
    try:
        args = [a for a in Path(f"/proc/{pid}/cmdline").read_bytes().decode().split("\0") if a]
    except OSError:
        return "hypr"
    for i, a in enumerate(args):
        if a == "--config" and i + 1 < len(args):
            return Path(args[i + 1]).parent.name
        if a.startswith("--config="):
            return Path(a.split("=", 1)[1]).parent.name
    return "hypr"


def detect_wm():
    """Return the config-dir name of the running TWM, or None."""
    hypr = _hypr_config_dir()
    if hypr:
        return hypr
    for proc, cfg in WM_MAP.items():
        if subprocess.run(["pgrep", "-x", proc], capture_output=True).returncode == 0:
            return cfg
    env = (os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "").lower()
    for cfg in WM_MAP.values():
        if cfg in env:
            return cfg
    return None


def resolve_file(explicit, dev=False):
    """Return (path, reasons). path is None when nothing resolves; reasons is a list of
    human-readable lines explaining the failure (for the launch-failure popup)."""
    if explicit:
        p = Path(explicit).expanduser()
        if p.exists():
            return p, []
        return None, [f"The file passed with --file does not exist:\n      {p}"]
    if dev:
        return Path(__file__).resolve().parent / "sample.keybindings.txt", []

    wm = detect_wm()
    if not wm:
        env = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "(unset)"
        stype = os.environ.get("XDG_SESSION_TYPE") or "(unset)"
        return None, [
            "Could not detect a supported desktop or window manager.",
            f"Running session: XDG_CURRENT_DESKTOP={env}, XDG_SESSION_TYPE={stype}",
            "None of the known compositors were running (pgrep) and the session name "
            "matched no known environment:",
            "      " + ", ".join(WM_MAP),
            "If this is a new Kiro environment, add its process name to WM_MAP in main.py "
            "and ship a keybindings.txt for it.",
        ]

    # Plasma is a full desktop, not a TWM: its cheatsheet sits at the .config root
    # (no <wm> subdir), matching where kiro-plasma-keybindings ships it via skel.
    if wm == "plasma":
        user = Path.home() / ".config" / "keybindings.txt"
    else:
        user = Path.home() / ".config" / wm / "keybindings.txt"
    if user.exists():
        return user, []
    bundled = Path(__file__).resolve().parent / f"{wm}.keybindings.txt"
    if bundled.exists():
        return bundled, []
    return None, [
        f"Detected environment: {wm}",
        "...but no keybindings.txt was found for it. Looked in:",
        f"      {user}",
        f"      {bundled}",
        f"The '{wm}' package has not shipped a keybindings.txt yet.",
    ]


def show_launch_error(reasons):
    """Pop a GUI dialog listing why the cheatsheet could not launch; fall back to stderr.

    GUI launchers (.desktop / global shortcut) swallow stderr, so a silent exit looks like
    the app is simply broken. A popup makes the cause visible on any not-yet-wired environment.
    """
    body = "\n".join(f"• {r}" for r in reasons) if reasons else "Unknown reason."
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)  # noqa: F841 (kept alive for exec)
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle("Kiro Keybindings")
        box.setText("The keybindings cheatsheet could not open.")
        box.setInformativeText(body)
        box.exec()
    except Exception:
        print("kiro-keybindings: could not open cheatsheet:\n" + body, file=sys.stderr)


class Backend(QObject):
    modelChanged = Signal()
    busyChanged = Signal()
    # (ok, fmt, path-or-message) — fired on the GUI thread when an export finishes.
    exportFinished = Signal(bool, str, str)

    def __init__(self, sections, title, wm, source_path):
        super().__init__()
        self._all = sections
        self._title = title
        self._wm = wm
        self._source = source_path
        self._filter = ""
        self._busy = False

    @Property(str, constant=True)
    def title(self):
        return self._title

    @Property(str, constant=True)
    def wm(self):
        return self._wm

    @Property(bool, notify=busyChanged)
    def exportBusy(self):
        return self._busy

    def _set_busy(self, value):
        if self._busy != value:
            self._busy = value
            self.busyChanged.emit()

    @Slot(str)
    def export(self, fmt):
        """Render the live keybindings.txt to HTML/PDF in a daemon thread, then open it."""
        if self._busy:
            return
        self._set_busy(True)
        threading.Thread(target=self._export_worker, args=(fmt,), daemon=True).start()

    def _export_worker(self, fmt):
        try:
            out = exporter.export(self._source, fmt)
            subprocess.Popen(["xdg-open", str(out)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            ok, payload = True, str(out)
        except Exception as e:
            ok, payload = False, str(e)
        self._set_busy(False)
        self.exportFinished.emit(ok, fmt, payload)

    @Property("QVariantList", notify=modelChanged)
    def sections(self):
        if not self._filter:
            return self._all
        out = []
        for section in self._all:
            if self._filter in section["name"].lower():
                out.append(section)
                continue
            rows = [
                b for b in section["bindings"]
                if self._filter in b["combo"].lower() or self._filter in b["desc"].lower()
            ]
            if rows:
                out.append({"name": section["name"], "bindings": rows})
        return out

    @Slot(str)
    def setFilter(self, text):
        self._filter = text.strip().lower()
        self.modelChanged.emit()


def main():
    ap = argparse.ArgumentParser(prog="kiro-keybindings")
    ap.add_argument("--file", help="explicit keybindings.txt (overrides auto-detect)")
    ap.add_argument("--dev", action="store_true",
                    help="load the bundled sample keybindings (launches anywhere; for dev/screenshots/theming)")
    ap.add_argument("--title", help="override the window title text")
    ap.add_argument("--theme", default="", help="force a theme (overrides the saved choice); blank = use saved")
    ap.add_argument("--header", default="rule", help="category header style: rule | bar | dot | plain")
    ap.add_argument("--keys", default="mono", help="keycap style: boxed | outline | text | mono")
    ap.add_argument("--shot", help="render the window to this PNG (offscreen) and exit")
    args = ap.parse_args()

    path, reasons = resolve_file(args.file, args.dev)
    if not path or not path.exists():
        if not reasons:
            reasons = ["No keybindings.txt found for this environment (try --dev for the sample)."]
        show_launch_error(reasons)
        return 1

    title, sections = parse(str(path))
    wm = "sample (dev)" if args.dev else (detect_wm() or title or "")

    if args.shot:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["QT_QUICK_BACKEND"] = "software"

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("kiro")
    app.setApplicationName("kiro-keybindings")
    backend = Backend(sections, args.title or title or "Keybindings", wm, str(path))

    here = Path(__file__).resolve().parent
    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("backend", backend)
    ctx.setContextProperty("appTheme", args.theme)
    ctx.setContextProperty("appHeader", args.header)
    ctx.setContextProperty("appKeys", args.keys)
    # Full desktops (Plasma) expect normal window decorations; TWMs want no titlebar.
    # Frameless is used only on Wayland TWMs: on X11, FramelessWindowHint makes Qt tag the
    # window _KDE_NET_WM_WINDOW_TYPE_OVERRIDE, which dwm-family WMs leave unmanaged (no
    # border, no keyboard focus). X11 TWMs get a plain Qt.Dialog the WM manages and focuses.
    is_plasma = detect_wm() == "plasma"
    ctx.setContextProperty("appDecorated", is_plasma)
    ctx.setContextProperty("appFrameless", app.platformName() != "xcb" and not is_plasma)
    ctx.setContextProperty("appShot", bool(args.shot))
    ctx.setContextProperty("logoPath", QUrl.fromLocalFile(str(here / "assets" / "logo.png")).toString())
    engine.load(QUrl.fromLocalFile(str(here / "Cheatsheet.qml")))
    roots = engine.rootObjects()
    if not roots:
        return 1

    if args.shot:
        window = roots[0]

        def grab():
            if isinstance(window, QQuickWindow):
                window.grabWindow().save(args.shot)
            app.quit()

        QTimer.singleShot(900, grab)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
