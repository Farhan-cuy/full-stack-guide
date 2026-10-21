#!/usr/bin/env python3
"""Validate eval fixtures and grade a candidate repository against a fixture.

Usage:
  python scripts/check_fixtures.py
      Check every fixture: baseline tests must PASS and acceptance tests must FAIL on the untouched repo.
  python scripts/check_fixtures.py --grade <fixture> <candidate_repo_dir>
      Copy the candidate, add the hidden acceptance tests, run the whole test command, report PASS/FAIL.

Standard library only. A fixture whose runtime is missing is reported as NOT RUN (never as PASS).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "fixtures"

# name -> (required executable, command run inside the repo, subdirectory that holds tests)
CONFIG = {
    "node-api-mini": ("node", ["node", "--test"], "tests"),
    "python-api-mini": (sys.executable, [sys.executable, "-m", "unittest", "discover", "-s", "tests"], "tests"),
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120)


def runtime_available(exe: str) -> bool:
    return Path(exe).exists() or shutil.which(exe) is not None


def stage(repo: Path, work: Path) -> Path:
    dest = work / "repo"
    shutil.copytree(repo, dest, ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
    return dest


def add_acceptance(fixture_dir: Path, repo: Path, tests_sub: str) -> None:
    target = repo / tests_sub
    target.mkdir(parents=True, exist_ok=True)
    for f in (fixture_dir / "acceptance").iterdir():
        shutil.copy2(f, target / f.name)


def check_all() -> int:
    failures = 0
    for name, (exe, cmd, tests_sub) in CONFIG.items():
        fixture_dir = FIXTURES / name
        if not fixture_dir.is_dir():
            print(f"FAIL {name}: fixture directory missing")
            failures += 1
            continue
        if not runtime_available(exe):
            print(f"NOT RUN {name}: runtime '{exe}' not found")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            repo = stage(fixture_dir / "repo", work)
            base = run(cmd, repo)
            if base.returncode != 0:
                print(f"FAIL {name}: baseline tests should pass on the untouched repo\n{base.stdout}{base.stderr}")
                failures += 1
                continue
            add_acceptance(fixture_dir, repo, tests_sub)
            acc = run(cmd, repo)
            if acc.returncode == 0:
                print(f"FAIL {name}: acceptance tests pass on the untouched repo (fixture has no seeded defect)")
                failures += 1
                continue
        print(f"PASS {name}: baseline passes, acceptance fails as designed")
    return 1 if failures else 0


def grade(name: str, candidate: Path) -> int:
    if name not in CONFIG:
        print(f"Unknown fixture '{name}'. Known: {', '.join(CONFIG)}")
        return 2
    exe, cmd, tests_sub = CONFIG[name]
    if not candidate.is_dir():
        print(f"Candidate directory not found: {candidate}")
        return 2
    if not runtime_available(exe):
        print(f"NOT RUN {name}: runtime '{exe}' not found")
        return 3
    with tempfile.TemporaryDirectory() as tmp:
        repo = stage(candidate, Path(tmp))
        add_acceptance(FIXTURES / name, repo, tests_sub)
        result = run(cmd, repo)
    print(result.stdout + result.stderr)
    verdict = "PASS" if result.returncode == 0 else "FAIL"
    print(f"{verdict} {name}: baseline + acceptance tests on the candidate")
    return 0 if result.returncode == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--grade", nargs=2, metavar=("FIXTURE", "CANDIDATE_DIR"))
    args = parser.parse_args()
    if args.grade:
        return grade(args.grade[0], Path(args.grade[1]))
    return check_all()


if __name__ == "__main__":
    sys.exit(main())
