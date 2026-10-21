# Adapter template

Copy this file to `framework-families/<area>/<name>.md` and replace every placeholder with concrete, checkable content. An adapter that only repeats generic advice should not be added: the validator rejects adapters that are identical to each other, and every adapter needs the five sections below.

# <Area>: <Technology>

One or two lines: what this covers and what it does not.

## Detection
Files, dependencies, entry points, and config that prove this technology is really in use (not just installed).

## Idioms
How well-run projects in this technology usually do routing, validation, authorization, persistence, errors, and tests. Name real APIs and files.

## Pitfalls
Five or so concrete mistakes that are common in this technology and that tests rarely catch.

## Verify
Exact commands to build, lint, type-check, and test. Say how to find the project's real scripts.

## Version-sensitive
APIs and defaults that differ between major versions. State that the installed version must be checked (`../../references/library-verification.md`) before relying on any of them.
