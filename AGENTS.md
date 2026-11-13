# Maintenance rules

- Read README, docs/build.md and docs/known-issues.md before changes.
- Keep original login/MFA UI and real server validation. Never fake account,
  signature, token or success; never disable TLS, force Basic or transplant SOs.
- Preserve host 7.0.0/1614 binding and auth36 runtime namespace unless migrating
  deliberately. Obfuscated names require renewed verification after upgrades.
- Separate synthetic tests, genuine emulator authentication, ARM64 static checks,
  physical-car results, and long-term renewal. Do not extrapolate one to another.
- Run unit tests and repository scan. Use synthetic data only in tests.
- Archive superseded observations; list only current issues and outstanding
  validation in docs/known-issues.md.
- Keep release summaries and current status aligned with version-specific evidence.
