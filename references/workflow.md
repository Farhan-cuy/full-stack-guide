# Core workflow: inspect, plan, change, verify

## 1. Establish the actual environment
- Inspect repository instructions, manifests, lockfiles, runtime/toolchain versions, CI configuration, and relevant tests.
- Identify the smallest end-to-end path touched by the task (UI → client → API → use case → persistence, where applicable).
- Read the closest maintained sibling implementation and its tests. Prefer evidence from this repository over remembered conventions.
- Check installed versions and official documentation when behavior is version-sensitive. Do not infer versions from file names or old examples.

## 2. Define scope before editing
Write down requested behavior, acceptance criteria, affected contracts, and explicitly excluded work. Trace consumers and producers of changed fields. Avoid scaffolding unrelated CRUD, abstractions, dependencies, migrations, or UI redesigns. Ask a focused question if a material ambiguity cannot safely be resolved from the repository.

## 3. Choose a pattern
Priority order: (1) explicit user requirements and safety constraints; (2) current repository behavior and contracts; (3) installed-version official docs; (4) a matching adapter; (5) simplest defensible fallback. If these conflict, report the conflict rather than silently changing public behavior.

## 4. Implement in small steps
- Keep changes localized and reversible.
- Follow established architecture unless it is directly responsible for the bug or creates a security/data-integrity risk.
- Separate use-case/business logic when it improves cohesion, transaction boundaries, or testability; do not add empty pass-through layers.
- Keep secrets and authorization decisions on trusted server boundaries. Validate untrusted inputs at boundaries.
- For cross-layer work, preserve one coherent contract from producer through consumer.

## 5. Verify and report
- Inspect the diff for scope creep, generated artifacts, secrets, unintended contract changes, and missing tests.
- Run the narrowest relevant tests first, then lint/type-check/build or broader tests when feasible.
- Record exact commands and observed outcomes. Mark checks not run as `NOT RUN`; never imply a test passed merely because code looks plausible.
- Report summary, files/areas changed, contract/security/data implications, verification evidence, known gaps, and follow-up risks.

## 6. Verify libraries and search for consumers
Before relying on a library API you have not seen working in this repository, follow `library-verification.md`. After changing any contract, run the impact search in `contracts.md` and update every consumer found.
