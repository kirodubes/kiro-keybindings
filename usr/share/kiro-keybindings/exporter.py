#!/usr/bin/env python3
"""Render a Kiro keybindings.txt into a self-contained keybindings.html (+ printable PDF).

Canonical home for the cheatsheet HTML/PDF transform. The GUI's two export buttons and
the ~/.bin/kiro-keybindings-html.py CLI shim both call export() — keep the logic here so
the template and PDF rendering can never drift between the two callers.
"""
import base64
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

BROWSERS = ["brave", "brave-browser", "chromium", "chromium-browser",
            "vivaldi", "vivaldi-stable", "google-chrome-stable", "google-chrome"]

SECTION_RE = re.compile(r"^──\s*(\d+)\.\s*(.+?)\s*─+\s*$")
BIND_RE = re.compile(r"^\s{2}(\S.*?)\s{2,}(\S.*)$")
HEADER_ENV_RE = re.compile(r"^#\s*KEYBINDINGS\s*—\s*(.+?)\s*$")
HEADER_SRC_RE = re.compile(r"^#\s*Source:\s*(.+?)\s*$")
HEADER_GEN_RE = re.compile(r"^#\s*Generated:\s*(.+?)\s*$")


def logo_data_uri():
    """Return the app's assets/logo.png as a base64 data URI (so HTML stays self-contained)."""
    logo = Path(__file__).resolve().parent / "assets" / "logo.png"
    data = base64.b64encode(logo.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def parse(text):
    """Parse keybindings.txt into (env, source, generated, [(num, title, [(combo, action)])])."""
    env = source = generated = ""
    sections = []
    current = None
    for line in text.splitlines():
        if not env and (m := HEADER_ENV_RE.match(line)):
            env = m.group(1)
            continue
        if not source and (m := HEADER_SRC_RE.match(line)):
            source = m.group(1)
            continue
        if not generated and (m := HEADER_GEN_RE.match(line)):
            generated = m.group(1)
            continue
        if m := SECTION_RE.match(line):
            current = (int(m.group(1)), m.group(2), [])
            sections.append(current)
            continue
        if current and (m := BIND_RE.match(line)):
            current[2].append((m.group(1).strip(), m.group(2).strip()))
    return env, source, generated, sections


def render_keys(combo):
    """Render a 'super + shift + q' combo as <kbd> chips joined by + separators."""
    parts = [p for p in combo.split(" + ")]
    chips = [f"<kbd>{html.escape(p)}</kbd>" for p in parts]
    return '<span class="plus">+</span>'.join(chips)


def render(env, source, generated, sections):
    """Build the full HTML document string from parsed data."""
    cards = []
    for num, title, binds in sections:
        rows = "\n".join(
            f'        <div class="bind" data-text="{html.escape((combo + " " + action).lower())}">'
            f'<span class="keys">{render_keys(combo)}</span>'
            f'<span class="desc">{html.escape(action)}</span></div>'
            for combo, action in binds
        )
        cards.append(
            f'    <section>\n'
            f'      <h2><span class="num">{num}</span>{html.escape(title)}</h2>\n'
            f'      <div class="binds">\n{rows}\n      </div>\n'
            f'    </section>'
        )
    cards_html = "\n".join(cards)
    env_e = html.escape(env)
    source_e = html.escape(source)
    generated_e = html.escape(generated)
    return TEMPLATE.format(
        env=env_e, source=source_e, generated=generated_e, cards=cards_html, logo=logo_data_uri()
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kiro {env} — Keybindings</title>
<style>
  :root {{
    --bg: #1a1b26; --panel: #24283b; --panel-2: #2c3148; --text: #c0caf5;
    --muted: #7a82a8; --accent: #FFA500; --key-bg: #343a52; --key-border: #454c6b;
    --border: #2f3550;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--bg); color: var(--text);
    font-family: system-ui, "Segoe UI", Roboto, sans-serif; line-height: 1.5;
  }}
  header {{
    position: sticky; top: 0; z-index: 10;
    background: linear-gradient(180deg, var(--panel) 0%, rgba(36,40,59,0.96) 100%);
    border-bottom: 2px solid var(--accent); padding: 1.1rem 1.5rem 0.9rem;
    backdrop-filter: blur(6px);
  }}
  .title-row {{ display: flex; align-items: center; gap: 0.7rem; flex-wrap: wrap; }}
  .logo {{ height: 38px; width: auto; flex-shrink: 0; }}
  h1 {{ margin: 0; font-size: 1.5rem; letter-spacing: 0.5px; }}
  h1 .k {{ color: var(--accent); }}
  .subtitle {{ color: var(--muted); font-size: 0.85rem; }}
  .search-wrap {{ margin-top: 0.8rem; position: relative; max-width: 480px; }}
  #search {{
    width: 100%; padding: 0.55rem 0.9rem 0.55rem 2.2rem; font-size: 0.95rem;
    color: var(--text); background: var(--panel-2); border: 1px solid var(--border);
    border-radius: 8px; outline: none;
  }}
  #search:focus {{ border-color: var(--accent); }}
  .search-wrap::before {{
    content: "\\2315"; position: absolute; left: 0.7rem; top: 50%;
    transform: translateY(-50%); color: var(--muted); font-size: 1.1rem;
  }}
  main {{
    max-width: 1100px; margin: 0 auto; padding: 1.5rem;
    column-width: 330px; column-gap: 1.1rem;
  }}
  section {{
    background: var(--panel); border: 1px solid var(--border); border-radius: 10px;
    overflow: hidden; break-inside: avoid; margin: 0 0 1.1rem;
  }}
  section h2 {{
    margin: 0; font-size: 0.95rem; padding: 0.7rem 1rem; background: var(--panel-2);
    color: var(--accent); border-bottom: 1px solid var(--border); display: flex;
    align-items: center; gap: 0.5rem;
  }}
  section h2 .num {{
    font-size: 0.75rem; background: var(--accent); color: #1a1b26; border-radius: 5px;
    padding: 0.05rem 0.4rem; font-weight: 700;
  }}
  .binds {{ padding: 0.4rem 0.6rem; }}
  .bind {{
    display: flex; justify-content: space-between; align-items: center; gap: 0.8rem;
    padding: 0.32rem 0.4rem; border-radius: 6px;
  }}
  .bind:hover {{ background: var(--panel-2); }}
  .keys {{ display: flex; gap: 0.2rem; flex-wrap: wrap; flex-shrink: 0; }}
  kbd {{
    font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 0.72rem;
    background: var(--key-bg); border: 1px solid var(--key-border);
    border-bottom-width: 2px; border-radius: 5px; padding: 0.12rem 0.4rem;
    color: #e6ebff; white-space: nowrap;
  }}
  .plus {{ color: var(--muted); font-size: 0.7rem; align-self: center; }}
  .desc {{ color: var(--text); font-size: 0.85rem; text-align: right; opacity: 0.92; }}
  .hidden {{ display: none !important; }}
  #noresults {{
    grid-column: 1 / -1; text-align: center; color: var(--muted); padding: 2rem;
    display: none;
  }}
  footer {{
    text-align: center; color: var(--muted); font-size: 0.8rem; padding: 1.5rem;
    border-top: 1px solid var(--border);
  }}
  footer a {{ color: var(--accent); text-decoration: none; }}
  @media print {{
    @page {{ margin: 1cm; }}
    * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    body {{ background: #fff; color: #111; }}
    header {{
      position: static; background: #fff; padding: 0 0 0.6rem;
      border-bottom: 2px solid var(--accent);
    }}
    #search, .search-wrap {{ display: none; }}
    h1 {{ color: #111; }}
    h1 .k {{ color: #c47f00; }}
    .subtitle {{ color: #555; }}
    main {{ column-width: 320px; column-gap: 0.8rem; padding: 0.6rem 0 0; max-width: none; }}
    section {{
      background: #fff; border: 1px solid #bbb; break-inside: auto; margin-bottom: 0.7rem;
    }}
    section h2 {{
      background: #f2f2f2; color: #b36b00; border-bottom: 1px solid #ccc; break-after: avoid;
    }}
    .bind {{ break-inside: avoid; }}
    section h2 .num {{ background: var(--accent); color: #000; }}
    .bind:hover {{ background: none; }}
    .desc {{ color: #222; opacity: 1; }}
    .plus {{ color: #888; }}
    kbd {{ background: #eee; color: #000; border: 1px solid #bbb; }}
    footer {{ color: #555; border-top: 1px solid #ccc; }}
  }}
</style>
</head>
<body>
<header>
  <div class="title-row">
    <img class="logo" src="{logo}" alt="Kiro logo">
    <h1><span class="k">Kiro</span> {env} — Keybindings</h1>
    <span class="subtitle">Super = Windows key</span>
  </div>
  <div class="search-wrap">
    <input id="search" type="text"
      placeholder="Filter shortcuts…  (e.g. terminal, super, screenshot)"
      autocomplete="off" autofocus>
  </div>
</header>

<main id="grid">
{cards}
  <div id="noresults">No shortcuts match your filter.</div>
</main>

<footer>
  Generated from <code>keybindings.txt</code> ({generated})<br>
  Source: <code>{source}</code> · part of <a href="https://kiroproject.be">Kiro</a>
</footer>

<script>
const search = document.getElementById("search");
const noresults = document.getElementById("noresults");
search.addEventListener("input", () => {{
  const q = search.value.trim().toLowerCase();
  let anyVisible = false;
  document.querySelectorAll("section").forEach(sec => {{
    let secVisible = false;
    sec.querySelectorAll(".bind").forEach(b => {{
      const match = !q || b.dataset.text.includes(q);
      b.classList.toggle("hidden", !match);
      if (match) secVisible = true;
    }});
    sec.classList.toggle("hidden", !secVisible);
    if (secVisible) anyVisible = true;
  }});
  noresults.style.display = anyVisible ? "none" : "block";
}});
</script>
</body>
</html>
"""


def find_browser():
    """Return the first available Chromium-family browser command, or None."""
    for b in BROWSERS:
        if shutil.which(b):
            return b
    return None


def render_pdf(html_path, pdf_path, browser):
    """Render the print view of html_path to pdf_path via a headless Chromium browser."""
    subprocess.run(
        [browser, "--headless=new", "--disable-gpu", "--no-first-run",
         "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
        check=True, capture_output=True, timeout=60,
    )


def _writable_dir(preferred):
    """Return preferred if it's a writable dir, else fall back to the home dir."""
    if preferred.is_dir() and os.access(preferred, os.W_OK):
        return preferred
    return Path.home()


def export(txt_path, fmt, out_dir=None):
    """Render txt_path to HTML or PDF and return the written file's path.

    fmt is "html" or "pdf" ("pdf" renders the HTML first, then prints it). Output lands
    in out_dir, or next to the source txt; if that dir isn't writable it falls back to
    the home dir. Raises ValueError/RuntimeError on bad input or a missing browser.
    """
    src = Path(txt_path).expanduser().resolve()
    if not src.is_file():
        raise ValueError(f"{src} not found")
    env, source, generated, sections = parse(src.read_text())
    if not sections:
        raise ValueError(f"no sections parsed from {src} — is it a keybindings.txt?")

    dest_dir = Path(out_dir).expanduser() if out_dir else _writable_dir(src.parent)
    html_path = dest_dir / f"{src.stem}.html"
    html_path.write_text(render(env, source, generated, sections))
    if fmt == "html":
        return html_path

    if fmt == "pdf":
        browser = find_browser()
        if not browser:
            raise RuntimeError("no Chromium-family browser found — cannot make a PDF")
        pdf_path = html_path.with_suffix(".pdf")
        render_pdf(html_path, pdf_path, browser)
        return pdf_path

    raise ValueError(f"unknown format: {fmt!r} (expected 'html' or 'pdf')")


def _cli():
    import argparse

    ap = argparse.ArgumentParser(description="Render a keybindings.txt into HTML (+ printable PDF).")
    ap.add_argument("txt", help="path to a keybindings.txt")
    ap.add_argument("output", nargs="?", help="output .html path (default: alongside the .txt)")
    ap.add_argument("--no-pdf", action="store_true", help="skip the printable PDF")
    args = ap.parse_args()

    out_dir = Path(args.output).resolve().parent if args.output else None
    try:
        html_out = export(args.txt, "html", out_dir)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"wrote {html_out}")

    if args.no_pdf:
        return
    try:
        pdf_out = export(args.txt, "pdf", out_dir)
    except RuntimeError as e:
        print(f"warning: {e} — skipped PDF", file=sys.stderr)
        return
    print(f"wrote {pdf_out}")


if __name__ == "__main__":
    _cli()
