#!/usr/bin/env python3
"""Validate skill package structure, metadata, local links, evals, adapters, fixtures, and agent-neutrality.

Standard library only. Exit code 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


REQUIRED = [
    "SKILL.md", "README.md", "CHANGELOG.md",
    "references/workflow.md", "references/architecture.md", "references/scope-control.md",
    "references/security.md", "references/contracts.md", "references/data-integrity.md",
    "references/debugging.md", "references/testing.md", "references/output-contract.md",
    "references/adapters.md", "references/library-verification.md", "references/portable-patterns.md",
    "references/frontend-design-quality.md",
    "evals/evals.json", "evals/README.md",
    "adapters/INDEX.md", "adapters/_template.md",
    "adapters/laravel-next/README.md", "adapters/laravel-next/references/backend.md",
    "adapters/framework-families/README.md",
    "integrations/AGENTS.snippet.md",
    "scripts/validate_package.py", "scripts/check_fixtures.py", "scripts/ui_slop_scan.py",
]
for rel in REQUIRED:
    if not (ROOT / rel).is_file():
        err(f"Missing required file: {rel}")

# ---------- packaging hygiene ----------
for p in ROOT.rglob("*"):
    if "__pycache__" in p.parts or p.suffix in {".pyc", ".pyo"} or p.name == ".DS_Store":
        err(f"Compiled or junk artifact in package: {p.relative_to(ROOT)}")
    if "node_modules" in p.parts:
        err(f"node_modules must not be packaged: {p.relative_to(ROOT)}")

# ---------- SKILL.md frontmatter ----------
skill = ROOT / "SKILL.md"
version = None
if skill.exists():
    text = skill.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm_match:
        err("SKILL.md has no YAML frontmatter")
    else:
        fm = fm_match.group(1)
        # top-level keys -> folded value text
        values: dict[str, str] = {}
        key = None
        for line in fm.split("\n"):
            m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
            if m and not line.startswith(" "):
                key = m.group(1)
                values[key] = m.group(2).strip()
            elif key:
                values[key] = (values[key] + " " + line.strip()).strip()
        name = values.get("name", "").strip()
        if name != ROOT.name:
            err(f"Frontmatter name '{name}' must equal the folder name '{ROOT.name}'")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            err("Frontmatter name must be lowercase letters, digits, hyphens (max 64)")
        desc = re.sub(r"^>\s*", "", values.get("description", "")).strip()
        if not desc:
            err("Frontmatter description is empty")
        elif len(desc) > 1024:
            err(f"Frontmatter description is {len(desc)} chars (max 1024)")
        if "compatibility" not in values:
            err("Frontmatter is missing 'compatibility'")
        elif len(re.sub(r"^>\s*", "", values["compatibility"])) > 500:
            err("Frontmatter compatibility exceeds 500 chars")
        if "metadata" not in values:
            err("Frontmatter is missing 'metadata'")
    m = re.search(r"^  version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", text, re.M)
    version = m.group(1) if m else None
    if not version:
        err("Could not read metadata.version in SKILL.md")
    if len(text.splitlines()) > 500:
        err("SKILL.md exceeds 500 lines; move detail into references/")
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    if "framework-agnostic" not in text.lower() and "framework-agnostic" not in readme.lower():
        err("Missing framework-agnostic positioning")
    if version and f"v{version}" not in readme:
        err(f"README.md heading does not mention v{version}")

changelog = ROOT / "CHANGELOG.md"
if version and changelog.exists() and not re.search(rf"^## {re.escape(version)}\s+—", changelog.read_text(encoding="utf-8"), re.M):
    err(f"CHANGELOG.md has no top-level entry for version {version}")

# ---------- evals ----------
evalfile = ROOT / "evals/evals.json"
data: dict = {}
if evalfile.exists():
    try:
        data = json.loads(evalfile.read_text(encoding="utf-8"))
        if data.get("skill_name") != "fullstack-engineering-guide":
            err("Unexpected eval skill_name")
        if data.get("version") != version:
            err(f"evals version {data.get('version')!r} != skill version {version!r}")
        evals = data.get("evals")
        if not isinstance(evals, list) or not evals:
            err("evals must be a non-empty list")
        else:
            ids = [e.get("id") for e in evals]
            if len(ids) != len(set(ids)):
                err("Duplicate eval IDs")
            for item in evals:
                exp = item.get("expected_output", {})
                for k in ("must_include", "must_not_include"):
                    if not isinstance(exp.get(k), list) or not exp.get(k):
                        err(f"Eval {item.get('id')} lacks non-empty {k}")
                if not item.get("prompt"):
                    err(f"Eval {item.get('id')} lacks prompt")
                fx = item.get("fixture")
                if fx:
                    fx_path = ROOT / fx
                    if not fx_path.is_dir():
                        err(f"Eval {item.get('id')} fixture missing: {fx}")
                    else:
                        parent = fx_path.parent
                        if not (parent / "GRADING.md").is_file() or not (parent / "acceptance").is_dir():
                            err(f"Fixture {parent.name} needs GRADING.md and acceptance/")
                    if not item.get("grade_command"):
                        err(f"Eval {item.get('id')} has a fixture but no grade_command")
    except (json.JSONDecodeError, OSError) as exc:
        err(f"Invalid evals/evals.json: {exc}")

# ---------- local markdown links ----------
for md in ROOT.rglob("*.md"):
    body = md.read_text(encoding="utf-8")
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        path_part = target.split("#", 1)[0]
        if path_part and not (md.parent / path_part).resolve().exists():
            err(f"Broken local link in {md.relative_to(ROOT)}: {target}")

# ---------- Core must stay free of stack-specific conventions and agent brand wording ----------
core_files = [ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]
for md in core_files:
    body = md.read_text(encoding="utf-8")
    if re.search(r"ApiFormRequest|successResponse|Spatie|SANCTUM_STATEFUL_DOMAINS|SWR key array", body, re.I):
        err(f"Stack-specific convention leaked into Core file: {md.relative_to(ROOT)}")
    # architecture.md may list instruction file names; everything else must be agent-neutral
    if md.name != "architecture.md" and re.search(r"\b(Claude|Anthropic|Cursor|Copilot|Codex|Gemini|Windsurf|ChatGPT|OpenAI)\b", body):
        err(f"Agent-brand wording in Core file (keep it agent-neutral): {md.relative_to(ROOT)}")

# ---------- adapters ----------
families = sorted((ROOT / "adapters/framework-families").rglob("*.md"))
families = [f for f in families if f.name != "README.md"]
sections = ["## Detection", "## Idioms", "## Pitfalls", "## Verify", "## Version-sensitive"]
texts: dict[Path, str] = {}
for f in families:
    body = f.read_text(encoding="utf-8")
    texts[f] = body
    for s in sections:
        if s not in body:
            err(f"Adapter {f.relative_to(ROOT)} lacks section '{s}'")
    if len(body) < 1500:
        err(f"Adapter {f.relative_to(ROOT)} is too thin ({len(body)} chars)")
paths = list(texts)
for i in range(len(paths)):
    for j in range(i + 1, len(paths)):
        ratio = difflib.SequenceMatcher(None, texts[paths[i]], texts[paths[j]]).ratio()
        if ratio > 0.8:
            err(f"Adapters are near-identical ({ratio:.2f}): {paths[i].relative_to(ROOT)} vs {paths[j].relative_to(ROOT)}")

index = ROOT / "adapters/INDEX.md"
if index.exists():
    idx = index.read_text(encoding="utf-8")
    for f in families:
        rel = f.relative_to(ROOT / "adapters").as_posix()
        if rel not in idx:
            err(f"adapters/INDEX.md does not list adapter {rel}")
    if "laravel-next/README.md" not in idx:
        err("adapters/INDEX.md does not list the Laravel + Next.js adapter")

# ---------- fixtures ----------
for name in ("node-api-mini", "python-api-mini"):
    base = ROOT / "evals/fixtures" / name
    for rel in ("repo", "acceptance", "GRADING.md"):
        if not (base / rel).exists():
            err(f"Fixture {name} is missing {rel}")

# ---------- scanner self-test ----------
scanner = ROOT / "scripts/ui_slop_scan.py"
if scanner.is_file():
    res = subprocess.run([sys.executable, "-B", str(scanner), "--selftest"], capture_output=True, text=True, timeout=60)
    if res.returncode != 0:
        err("scripts/ui_slop_scan.py self-test failed: " + (res.stdout + res.stderr).strip().replace("\n", " | "))

if errors:
    print("PACKAGE VALIDATION: FAIL")
    for e in errors:
        print(f"- {e}")
    sys.exit(1)
print(
    f"PACKAGE VALIDATION: PASS (version={version}, evals={len(data.get('evals', []))}, "
    f"adapters={len(families)}, markdown_files={len(list(ROOT.rglob('*.md')))})"
)
