#!/usr/bin/env python
"""Kiro Keybindings — a slick PySide6/QML cheatsheet that auto-detects the running
TWM, finds that environment's keybindings.txt, and renders it with live search."""
import argparse
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow

from parser import parse

# Running WM process name (pgrep -x) → ~/.config/<dir>/keybindings.txt
WM_MAP = {
    "ohmychadwm": "ohmychadwm",
    "chadwm": "chadwm",
    "i3": "i3",
    "bspwm": "bspwm",
    "qtile": "qtile",
    "awesome": "awesome",
    "leftwm": "leftwm",
}


def detect_wm():
    """Return the config-dir name of the running TWM, or None."""
    for proc, cfg in WM_MAP.items():
        if subprocess.run(["pgrep", "-x", proc], capture_output=True).returncode == 0:
            return cfg
    env = (os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION") or "").lower()
    for cfg in WM_MAP.values():
        if cfg in env:
            return cfg
    return None


def resolve_file(explicit):
    if explicit:
        return Path(explicit).expanduser()
    wm = detect_wm()
    if wm:
        candidate = Path.home() / ".config" / wm / "keybindings.txt"
        if candidate.exists():
            return candidate
    return None


class Backend(QObject):
    modelChanged = Signal()

    def __init__(self, sections, title, wm):
        super().__init__()
        self._all = sections
        self._title = title
        self._wm = wm
        self._filter = ""

    @Property(str, constant=True)
    def title(self):
        return self._title

    @Property(str, constant=True)
    def wm(self):
        return self._wm

    @Property("QVariantList", notify=modelChanged)
    def sections(self):
        if not self._filter:
            return self._all
        out = []
        for section in self._all:
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
    ap.add_argument("--title", help="override the window title text")
    ap.add_argument("--theme", default="", help="force a theme (overrides the saved choice); blank = use saved")
    ap.add_argument("--header", default="rule", help="category header style: rule | bar | dot | plain")
    ap.add_argument("--keys", default="mono", help="keycap style: boxed | outline | text | mono")
    ap.add_argument("--shot", help="render the window to this PNG (offscreen) and exit")
    args = ap.parse_args()

    path = resolve_file(args.file)
    if not path or not path.exists():
        print("kiro-keybindings: no keybindings.txt found for this environment", file=sys.stderr)
        return 1

    title, sections = parse(str(path))
    wm = detect_wm() or (title or "")

    if args.shot:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        os.environ["QT_QUICK_BACKEND"] = "software"

    app = QGuiApplication(sys.argv)
    app.setOrganizationName("kiro")
    app.setApplicationName("kiro-keybindings")
    backend = Backend(sections, args.title or title or "Keybindings", wm)

    here = Path(__file__).resolve().parent
    engine = QQmlApplicationEngine()
    ctx = engine.rootContext()
    ctx.setContextProperty("backend", backend)
    ctx.setContextProperty("appTheme", args.theme)
    ctx.setContextProperty("appHeader", args.header)
    ctx.setContextProperty("appKeys", args.keys)
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
