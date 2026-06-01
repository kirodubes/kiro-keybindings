"""Parse a Kiro keybindings.txt into structured sections for the cheatsheet UI."""
import re

_SECTION_RE = re.compile(r"^──\s*\d+\.\s*(.+?)\s*─{2,}\s*$")
_HEADER_NAME_RE = re.compile(r"KEYBINDINGS\s*[—–-]\s*(.+?)\s*$")
_GAP_RE = re.compile(r"\s{2,}")

_MOD_CLASS = {
    "super": "super", "mod": "super", "meta": "super", "win": "super",
    "ctrl": "ctrl", "control": "ctrl", "primary": "ctrl",
    "shift": "shift",
    "alt": "alt", "mod1": "alt",
}
_PRETTY = {
    "super": "Super", "mod": "Super", "meta": "Super", "win": "Super",
    "ctrl": "Ctrl", "control": "Ctrl", "primary": "Ctrl",
    "shift": "Shift",
    "alt": "Alt", "mod1": "Alt",
}


def _token(tok):
    low = tok.strip().lower()
    return {"label": _PRETTY.get(low, tok.strip()), "kind": _MOD_CLASS.get(low, "key")}


def parse(path):
    """Return (title, sections); sections = [{name, bindings:[{combo, desc, tokens}]}]."""
    title = None
    sections = []
    current = None

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip():
                continue

            if line.lstrip().startswith("#"):
                if title is None:
                    m = _HEADER_NAME_RE.search(line)
                    if m:
                        title = m.group(1)
                continue

            m = _SECTION_RE.match(line)
            if m:
                current = {"name": m.group(1), "bindings": []}
                sections.append(current)
                continue

            parts = _GAP_RE.split(line.strip(), maxsplit=1)
            if len(parts) != 2:
                continue
            combo, desc = parts[0].strip(), parts[1].strip()
            tokens = [_token(k) for k in combo.split("+") if k.strip()]

            if current is None:
                current = {"name": "General", "bindings": []}
                sections.append(current)
            current["bindings"].append({"combo": combo, "desc": desc, "tokens": tokens})

    return title, sections
