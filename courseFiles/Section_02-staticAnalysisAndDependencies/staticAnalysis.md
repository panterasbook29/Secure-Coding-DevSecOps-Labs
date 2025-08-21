## Static Analysis and Dependencies
This section is about catching problems **before** they ever hit a running environment. We’ll use static analysis to spot insecure code patterns, and dependency scanning to keep third-party packages from dragging vulnerabilities into your app.

If Section 01 was about you writing safer code, Section 02 is about putting guardrails around the whole repo so risky changes never slip through unnoticed

### Why this matters
- Most teams ship **more dependency code** than **first-party code**, if you don’t manage the supply chain, it manages you
- Bugs like **injection**, **SSRF**, and **auth flaws** are often obvious to static tools when you teach them what to look for
- Good pipelines turn “hope” into **gates**: merge gets blocked until high-risk issues are fixed or explicitly accepted

### What we’ll cover
- **SAST (Static Application Security Testing)** with [Semgrep](/courseFiles/tools/semgrep.md) — fast rules, CI-friendly, catches insecure patterns in your code
- **SCA (Software Composition Analysis)** with [Snyk](/courseFiles/tools/snyk.md) (plus built-ins like ``npm audit``) — find known-vuln libraries and vulnerable transitive deps
- **SBOMs (CycloneDX/SPDX)** — generate a bill of materials and use it to track exposure
- **Version hygiene** — pinning, ranges, and how to avoid accidental upgrades that reopen old CVEs
- **Quality gates** — right way to fail a build (what to block, what to log, what to ticket)

### SAST vs DAST vs SCA (60-second cheat sheet)
- **SAST:** reads your code and flags risky patterns before runtime, great for PR checks (we’ll use [Semgrep](/courseFiles/tools/semgrep.md))
- **DAST:** pokes the running app from the outside, useful, but after you’ve deployed something
- **SCA:** reads your lockfiles/manifests to find known bad package versions (we’ll use [Snyk](/courseFiles/tools/snyk.md) and native tools)

In this section we focus on **SAST + SCA**

## What “good” looks like
- **Pinned, reproducible builds** (``package-lock.json``, ``poetry.lock``, ``go.mod``, ``Cargo.lock`` checked in)
- **Semgrep** runs on every PR; high/critical findings block the merge
- **Snyk** (or equivalent) runs on every PR; known critical vulns in production paths block
- **SBOM** generated on release; kept with artifacts; searchable in incidents
- **Exceptions are explicit** (one-line allow list with a documented expiry date)

### Quick mental model: where to put each control
- **Local dev:** ``semgrep --config p/owasp-top-ten --error`` and ``snyk test`` before commit
- **CI (PR):** same commands, plus upload SARIF or HTML reports
- **CI (main):** generate SBOM, run a full Snyk scan, fail on new criticals, store artifacts
- **Scheduled:** weekly dependency update PRs (Dependabot/Renovate) + scan on open

## Tiny pipeline examples 
**(copy/paste friendly)**


***GitHub Actions — Semgrep + Snyk on PRs***
```
# .github/workflows/security.yml
name: Security Checks
on:
  pull_request:
    branches: [ main ]
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: semgrep/semgrep-action@v1
        with:
          config: p/owasp-top-ten
          generateSarif: true
          sarifFile: semgrep.sarif
          auditOn: error
      - uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm audit --omit=dev || true  # info only; Snyk will gate
      - run: npm i -g snyk
      - run: snyk auth ${{ secrets.SNYK_TOKEN }}
      - run: snyk test --severity-threshold=high
```

<br><br>

***SBOM on release (Node example, CycloneDX)***
```
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: [ 'v*.*.*' ]
jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx @cyclonedx/cyclonedx-npm --output-file sbom.cdx.json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.cdx.json
```

## Hands-On Labs
Before the first lab, be sure to check out the [Semgrep Documentation](/courseFiles/tools/semgrep.md) so you have it ready for the lab

[Lab 1 – Semgrep SAST: Catch and Gate Insecure Code](/courseFiles/Section_02-staticAnalysisAndDependencies/Lab1.md)
**Goal:** Install Semgrep, run a focused rule set on a small Node/Express service, reproduce real findings (string-built SQL, unsafe innerHTML, insecure cookies), then fix and set a merge gate

<br><br>

Before this Lab, be sure to check out the [Snyk Documentation](/courseFiles/tools/snyk.md) so you have it ready for the lab

[Lab 2 – Dependencies, SBOM & Supply Chain](/courseFiles/Section_02-staticAnalysisAndDependencies/Lab2.md)
**Goal:** Use Snyk (and native package tools) to surface vulnerable libs in a real project (Juice Shop or the Lab 2 service), generate an SBOM, implement pinning + upgrade PRs, and add a CI failure threshold


***                                                       

<b><i>Continuing the course?</b>
</br>
[Click here for the Next Section](/courseFiles/Section_03-ciCdAndSecretsManagement/secretsManagement.md)</i>

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
