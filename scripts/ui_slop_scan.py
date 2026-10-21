#!/usr/bin/env python3
"""Advisory scanner for generic-looking or careless UI code.

Flags surface tells only: placeholder text, marketing filler, default gradients, motion defaults,
generic UI strings, and a few common accessibility slips. It cannot judge design quality: a clean
scan does not mean the design is good, and findings can be false positives. Read the matching rule
in references/frontend-design-quality.md before acting on a finding.

Usage:
  python scripts/ui_slop_scan.py <file-or-dir> [<file-or-dir> ...]   # print findings, exit 0
  python scripts/ui_slop_scan.py --strict <paths>                    # exit 1 if any finding
  python scripts/ui_slop_scan.py --selftest                          # verify the rules themselves

Standard library only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

EXTENSIONS = {".html", ".htm", ".css", ".scss", ".sass", ".less", ".js", ".jsx", ".ts", ".tsx",
              ".vue", ".svelte", ".astro", ".php", ".erb", ".twig", ".hbs"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", ".svelte-kit", "vendor", "__pycache__", "coverage"}
MAX_BYTES = 1_000_000

I = re.IGNORECASE

# (rule id, category, message, compiled regex applied per line)
LINE_RULES = [
    ("placeholder-text", "content",
     "Placeholder content (lorem ipsum, John/Jane Doe, 'your text here'); use real or clearly marked content.",
     re.compile(r"lorem ipsum|\b(john|jane) doe\b|\byour (text|title|name|company) here\b", I)),
    ("marketing-filler", "content",
     "Marketing filler; say plainly what the product does.",
     re.compile(r"\b(seamless(ly)?|unlock the power|supercharge[ds]?|revolutioni[sz]e[ds]?|cutting[- ]edge|next[- ]gen(eration)?|game[- ]?changer|elevate your|empower(s|ing)? your)\b", I)),
    ("invented-proof", "content",
     "Possible invented social proof (round user counts, 'trusted by'); never fabricate numbers, quotes, or customers.",
     re.compile(r"\btrusted by\b|\b\d{1,3}(,\d{3})*\s?[kKmM]?\+\s+(users|customers|teams|companies|downloads)\b", I)),
    ("default-gradient", "style",
     "Default purple/blue gradient or gradient text; use only if chosen for this subject.",
     re.compile(r"from-(purple|violet|indigo)-\d+[^\"'`]*to-(blue|pink|indigo|purple|fuchsia)-\d+|#667eea|#764ba2|bg-clip-text[^\"'`]*text-transparent|text-transparent[^\"'`]*bg-clip-text", I)),
    ("glass-and-glow", "style",
     "Frosted-glass or glow effect used as decoration; check it serves the design.",
     re.compile(r"backdrop-blur|backdrop-filter\s*:\s*blur|shadow-(purple|indigo|violet|blue)-\d+", I)),
    ("transition-all", "motion",
     "'transition: all' animates unintended properties; list the properties.",
     re.compile(r"transition\s*:\s*all\b|\btransition-all\b", I)),
    ("decorative-motion", "motion",
     "Looping decorative animation (bounce/pulse/ping); use motion to show state change.",
     re.compile(r"\banimate-(bounce|pulse|ping|spin)\b|animation(-name)?\s*:[^;]*\binfinite\b", I)),
    ("generic-ui-text", "content",
     "Generic UI text; say what will happen or what went wrong and how to fix it.",
     re.compile(r">\s*(Submit|Click here|Something went wrong|An error occurred|Error occurred|Oops!?)\s*<|['\"](Something went wrong|An error occurred|Oops!?)['\"]", I)),
    ("focus-outline-removed", "a11y",
     "Focus outline removed; make sure a visible replacement exists (focus-visible).",
     re.compile(r"outline\s*:\s*(none|0)\b|\boutline-none\b", I)),
    ("img-without-alt", "a11y",
     "Image without an alt attribute (use alt=\"\" for decoration).",
     re.compile(r"<img\b(?![^>]*\balt\s*=)[^>]*>", I)),
    ("clickable-non-control", "a11y",
     "Click handler on a non-interactive element; use a button or link (or add role, tabindex, key handling).",
     re.compile(r"<(div|span|li|td)\b(?![^>]*\b(role|tabindex)\s*=)[^>]*(\bonClick\b|\bonclick\b|@click\b|\(click\))", I)),
    ("placeholder-as-label", "a11y",
     "Input with a placeholder but no label hook (id/aria-label/aria-labelledby/name on the same tag); a placeholder is not a label.",
     re.compile(r"<input\b(?![^>]*\b(aria-label|aria-labelledby|id)\s*=)[^>]*\bplaceholder\s*=[^>]*>", I)),
]

# file-level rules: (rule id, category, message, trigger regex, required-absent regex)
FILE_RULES = [
    ("no-reduced-motion", "motion",
     "Animations are defined but no prefers-reduced-motion handling was found in this file.",
     re.compile(r"@keyframes|animation\s*:|\banimate-", I),
     re.compile(r"prefers-reduced-motion|motion-reduce|motion-safe", I)),
]


def iter_files(paths: list[str]):
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and f.suffix.lower() in EXTENSIONS and not (SKIP_DIRS & set(f.parts)):
                    yield f


def scan_text(text: str, name: str):
    findings = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        for rid, cat, msg, rx in LINE_RULES:
            if rx.search(line):
                findings.append((name, i, rid, cat, msg, line.strip()[:120]))
    for rid, cat, msg, trigger, absent in FILE_RULES:
        m = trigger.search(text)
        if m and not absent.search(text):
            line_no = text[: m.start()].count("\n") + 1
            findings.append((name, line_no, rid, cat, msg, lines[line_no - 1].strip()[:120]))
    return findings


def scan_paths(paths: list[str]):
    findings = []
    for f in iter_files(paths):
        try:
            if f.stat().st_size > MAX_BYTES:
                continue
            findings.extend(scan_text(f.read_text(encoding="utf-8", errors="replace"), str(f)))
        except OSError as exc:
            print(f"NOT SCANNED {f}: {exc}", file=sys.stderr)
    return findings


SLOPPY = '''<section class="bg-gradient-to-r from-purple-500 to-blue-500">
  <h1 class="bg-clip-text text-transparent">Unlock the power of seamless work</h1>
  <p>Lorem ipsum dolor sit amet. Trusted by 10k+ users.</p>
  <img src="hero.png">
  <div onClick={go}>Go</div>
  <input placeholder="Email">
  <button class="transition-all animate-bounce" style="outline: none">Submit</button>
  <p>Something went wrong</p>
</section>
<style>@keyframes spin2 { from { opacity: 0 } to { opacity: 1 } }</style>
'''

CLEAN = '''<main>
  <h1>Invoices</h1>
  <label for="q">Search invoices</label>
  <input id="q" type="search" placeholder="Customer or number">
  <img src="logo.svg" alt="">
  <button type="button" class="focus-visible:ring-2">Save changes</button>
  <p>No invoices match. Clear the filters or create an invoice.</p>
</main>
'''


def selftest() -> int:
    expected = {"placeholder-text", "marketing-filler", "invented-proof", "default-gradient", "transition-all",
                "decorative-motion", "generic-ui-text", "focus-outline-removed", "img-without-alt",
                "clickable-non-control", "placeholder-as-label", "no-reduced-motion"}
    got = {f[2] for f in scan_text(SLOPPY, "sloppy")}
    clean = scan_text(CLEAN, "clean")
    problems = []
    if not expected <= got:
        problems.append(f"rules did not fire on the sloppy sample: {sorted(expected - got)}")
    if clean:
        problems.append(f"false positives on the clean sample: {[(f[2], f[1]) for f in clean]}")
    if problems:
        print("SELFTEST FAIL")
        for p in problems:
            print("-", p)
        return 1
    print(f"SELFTEST PASS ({len(expected)} rules fire on the sloppy sample, 0 findings on the clean sample)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--strict", action="store_true", help="exit 1 when there is any finding")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.paths:
        ap.error("give at least one file or directory, or use --selftest")
    findings = scan_paths(args.paths)
    for name, line, rid, cat, msg, snippet in findings:
        print(f"{name}:{line}: [{cat}/{rid}] {msg}\n    {snippet}")
    print(f"\n{len(findings)} advisory finding(s). Heuristic only: a clean scan does not mean the design is good.")
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
