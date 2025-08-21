## Static Analysis and Dependencies
This section is about catching problems **before** they ever hit a running environment. We’ll use static analysis to spot insecure code patterns, and dependency scanning to keep third-party packages from dragging vulnerabilities into your app.

If Section 01 was about you writing safer code, Section 02 is about putting guardrails around the whole repo so risky changes never slip through unnoticed

### Why this matters
- Most teams ship **more dependency code** than **first-party code**, if you don’t manage the supply chain, it manages you
- Bugs like **injection**, **SSRF**, and **auth flaws** are often obvious to static tools when you teach them what to look for
- Good pipelines turn “hope” into **gates**: merge gets blocked until high-risk issues are fixed or explicitly accepted

### What we’ll cover
- **SAST (Static Application Security Testing)** with **Semgrep** — fast rules, CI-friendly, catches insecure patterns in your code
- **SCA (Software Composition Analysis)** with **Snyk** (plus built-ins like ``npm audit``) — find known-vuln libraries and vulnerable transitive deps
- **SBOMs (CycloneDX/SPDX)** — generate a bill of materials and use it to track exposure
- **Version hygiene** — pinning, ranges, and how to avoid accidental upgrades that reopen old CVEs
- **Quality gates** — right way to fail a build (what to block, what to log, what to ticket)


## lab1_static_analysis_with_semgrep

## lab2_dependency_scan_with_snyk_or_trivy


***                                                       

<b><i>Continuing the course?</b>
</br>
[Click here for the Next Section](/courseFiles/Section_03-ciCdAndSecretsManagement/secretsManagement.md)</i>

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_01-secureCoding_Basics/secureCoding_Basics.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
