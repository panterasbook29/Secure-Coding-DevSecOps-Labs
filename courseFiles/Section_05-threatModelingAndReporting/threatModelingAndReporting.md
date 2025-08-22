## Threat Modeling And Reporting
This section is where we slow down to think like attackers and then communicate like professionals, you’ll learn to sketch a system, find the scary parts, and turn that into a crisp report engineers and stakeholders can act on

If earlier sections were “fix the bug,” this one is “prevent the class of bugs” and tell the story so the team moves together

### Why this matters
- Most incidents are **predictable** if you map assets, entry points, and trust boundaries early
- Good threat models **de-risk designs** before code is written and give you a shared language with product, ops, and leadership
- Clear reporting turns findings into **decisions**, not debates

### What you’ll learn
- **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) as a thinking tool, not a trivia list
- **DFDs** (Data Flow Diagrams): identify **assets**, **actors**, **data stores**, **processes**, and **trust boundaries**
- **Risk rating** you can defend (OWASP Risk Rating or simple Likelihood × Impact)
- **Secure code review basics:** how to read code like an attacker and write findings that lead to fixes
- **Reporting that lands:** reproducible steps, impact, exploit path, and concrete mitigations


## Deliverables (what “done” looks like)
- **One-page Threat Model** (PNG/PDF): DFD + top risks with STRIDE tags
- **Risk Table** (CSV/MD): risk, affected component, STRIDE category, Likelihood, Impact, Mitigation, Owner
- **Secure Code Review Report** (MD): summary, methodology, findings with severity, repro, affected code, fix guidance, and references

## Cheat sheets you’ll keep
1. STRIDE prompts (per DFD element):
- **External Entity / Actor:** Spoofing, Repudiation
- **Process / Service:** Tampering, DoS, EoP
- **Data Store:** Tampering, Info Disclosure, Repudiation
- **Data Flow (across a boundary):** Info Disclosure, Tampering, DoS

2. Risk rating (simple):
- **Likelihood:** Low / Medium / High
- **Impact:** Low / Medium / High
- **Risk** = combine on a 3×3 grid (block High/High)

3. Reporting bones (per finding):
- **Title** (punchy + component)
- **Severity** (why)
- **Context** (where in the system/code)
- **Repro** (copy-paste steps or PoC)
- **Impact** (so what)
- **Fix** (code/config change, not a platitude)
- **References** (docs, CWE/OWASP)


## Tips
### Common pitfalls to avoid
- Listing threats without **tying them to assets** (“XSS somewhere” vs “XSS in Reviews API leaks session tokens”)
- Walls of text, your model and report should fit on one page each, with appendices if needed
- “Use HTTPS” as a fix for everything, be **specific** (“Add rate limit 5/min to ``/auth/reset``”)
- No owners, every high/medium risk should have a name on it.

### Tools (pick what you like)
- **Diagramming:** Draw.io, Excalidraw, Mermaid, or hand-draw then snap a photo
- **Code review helpers:** grep, ripgrep, Semgrep outputs, IDE search
- **Risk/Report:** Markdown + CSV; keep it versioned with the code

## Hands-On Labs
[Lab 1 – STRIDE Threat Modeling](/courseFiles/Section_05-threatModelingAndReporting/Lab1.md)
**Goal:** Draw a minimal DFD for a small web app, run STRIDE across processes/flows/stores, rate risks, and produce a one-page model + mitigation backlog

[Lab 2 – Secure Code Review & Report](/courseFiles/Section_05-threatModelingAndReporting/Lab2.md)
**Goal:** Perform a focused code review (auth, input handling, sensitive data), write a concise report with repros and code-level fixes, and add a short executive summary


***               

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_04-containerAndCloudSecurity/containerAndCloudSecurity.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
