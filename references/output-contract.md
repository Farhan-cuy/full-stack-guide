# Completion report

At completion, provide a concise, evidence-based report containing:

1. **Outcome:** what behavior changed and how it meets the request.
2. **Scope:** key files/areas changed and important omissions intentionally left out.
3. **Contracts and risk:** public API/schema/config/auth/data behavior changed or preserved; migration/deployment implications if any.
4. **Verification:** exact commands and `PASS` / `FAIL` / `NOT RUN` results. Distinguish static inspection from executed tests.
5. **Limitations:** unverified assumptions, environment constraints, follow-up risks, and any manual steps required.

Never claim to have edited files, run commands, consulted live documentation, or passed tests without observable evidence.

## Additional items
6. **Libraries:** one line per library you verified or could not verify, in the format from `library-verification.md` (`Verified:` / `UNVERIFIED:`).
7. **Impact search:** which consumers you searched for after a contract change, and what you updated.

Write the report in the user's language. Keep commands, identifiers, and error text exactly as they appear.
