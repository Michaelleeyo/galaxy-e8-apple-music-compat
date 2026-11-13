# Maintenance rules

- Read README, docs/build.md and docs/known-issues.md before changes.
- Keep original login/MFA UI and real server validation. Never fake account,
  signature, token or success; never disable TLS, force Basic or transplant SOs.
- Never commit APK/SO/DEX, credentials, signing keys, raw authentication logs,
  challenges, certificates, account identifiers or captured request bodies.
- Preserve host 7.0.0/1614 binding and auth36 runtime namespace unless migrating
  deliberately. Obfuscated names require renewed verification after upgrades.
- Separate synthetic tests, genuine emulator authentication, ARM64 static checks,
  physical-car results, and long-term renewal. Do not extrapolate one to another.
- Run unit tests and repository scan. Use synthetic data only in tests.
- Do not create fake historical commits or replace genuine source failures with
  success. Keep known limitations and rejected alternatives documented.
- Publishing or pushing is a separate user action; no proprietary inputs in CI.
