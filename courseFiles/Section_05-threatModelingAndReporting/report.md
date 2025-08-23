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
