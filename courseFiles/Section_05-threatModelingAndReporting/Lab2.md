## Goal
Do a **focused code review** of a real app (OWASP **Juice Shop**), confirm at least one issue with a quick repro, and produce a short report engineers can act on

## Setup
```bash
sudo apt install ripgrep
```

```bash
mkdir -p ~/section05-lab2 && cd ~/section05-lab2
```

```bash
docker run -d --name juice -p 3000:3000 bkimminich/juice-shop
```
Visit ``http://localhost:3000``

```bash
git clone https://github.com/juice-shop/juice-shop.git
```

```bash
cd juice-shop
```

## Start
### Quick discovery
- Grep for sensitive patterns

Where are tokens stored in the front end?
```bash
rg -n "localStorage|sessionStorage|document.cookie" --iglob "frontend/**"
```

---

Any raw HTML sinks?
```bash
rg -n "innerHTML|outerHTML|dangerouslySetInnerHTML"
```

---

Auth & reset paths (names vary between versions; this finds them)
```bash
rg -n "login|authenticate|reset|password|token" --iglob "**/*.(ts|js|ts|html)"
```

---

Server-side JWT handling
```bash
rg -n "jwt|jsonwebtoken|verify|sign" --iglob "*/**.(js|ts)"
```

---

- Run Semgrep
```bash
semgrep --config p/owasp-top-ten
```

<img width="191" height="54" alt="image" src="https://github.com/user-attachments/assets/81aa090b-5581-4abf-9052-c7b810169f6d" />


- Open the first 3–5 findings that look security relevant (injection, auth/session, XSS), ignore noisy style issues


### Propose a code-level fix (concise)
You’re not rewriting Juice Shop; you’re showing **how** to fix the class of bug

Pick the matching snippet and paste it into your report with comments

**Safer output (XSS)**
```
- element.innerHTML = userInput;
+ element.textContent = userInput; // no HTML interpretation
```
**Or server side:**
```
- res.send(`<h1>${q}</h1>`)
+ res.json({ title: String(q) })
```

**Plus:** add a **CSP** that forbids ``unsafe-inline`` and ``javascript:`` URLs

---

**HttpOnly session cookies (instead of LocalStorage)**
```
- localStorage.setItem('token', jwt)
+ // server sets cookie: Set-Cookie: sid=...; HttpOnly; Secure; SameSite=Lax
```

And on the client, read auth state from server, not from ``localStorage``

---

**Uniform password reset response**
```
- if (userExists) return res.status(200).send("Email sent");
- else return res.status(404).send("No such user");
+ // Always the same
+ return res.status(200).send("If the account exists, you'll receive an email.")
```

### Write the report
Create a file with this template and fill it in

```bash
cat > report.md <<'EOF'
# Secure Code Review Report — Juice Shop (focused sample)

**Scope:** Auth, input handling, sensitive data  
**Method:** ripgrep searches + Semgrep (p/owasp-top-ten) + manual review  
**Date/Reviewer:** YYYY-MM-DD / @yourname

## Executive Summary (3–5 sentences)
- One paragraph on what you looked at and the single most important risk.

## Findings

### [H] Cross-Site Scripting via reflected/DOM sink
**Where:** <file / component / route>  
**Repro:** paste `<iframe src="javascript:alert(\`xss\`)">` into <field/route> → alert fires  
**Impact:** Session/token theft, account takeover  
**Root cause:** Untrusted input written to HTML sink  
**Fix:** Use `textContent` / server-side encoding; add CSP forbidding inline scripts  
**References:** OWASP XSS, CWE-79

### [M] Token persisted in LocalStorage
**Where:** <file line(s)>  
**Evidence:** `localStorage.setItem('token', ...)`  
**Impact:** XSS → token theft; persistent auth until manual clear  
**Fix:** HttpOnly cookie session; short TTL; rotate on privilege change  
**References:** OWASP Session Management, CWE-922

### [M] Password reset user enumeration (if observed)
**Where:** <API path or UI>  
**Repro:** Valid vs random email → different message/status/timing  
**Impact:** Account harvesting → targeted attacks  
**Fix:** Uniform response + rate limit on endpoint  
**References:** OWASP ASVS V2, CWE-204

## Appendix
- Semgrep command: `semgrep --config p/owasp-top-ten --error .`
- Useful grep searches you ran
- Screenshots (runtime repro, DevTools storage)
EOF
```







---
[Back to the section](/courseFiles/Section_05-threatModelingAndReporting/threatModelingAndReporting.md)
