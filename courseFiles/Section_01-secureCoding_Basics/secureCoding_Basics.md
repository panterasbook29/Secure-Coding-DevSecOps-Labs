## Secure Coding Basics
This section is all about **foundations** — the habits and principles that make the difference between “working code” and **secure code**. Many developers write software that functions perfectly but unintentionally leaves open doors for attackers. Our job here is to learn how to **spot** those doors, **close** them, and **build** code that can stand up to **real-world abuse**

### Why this matters
- Most modern breaches still trace back to **basic coding flaws** like SQL injection, XSS, and insecure authentication logic
- These are not “advanced hacker tricks” — they’re preventable mistakes in code
- Learning secure coding basics means fewer late-night incidents, fewer patches in production, and more confidence in your work

### What we’ll cover
- The OWASP Top 10 as a practical guide, not just a checklist
- How attackers actually exploit common bugs
- How to patch them correctly and avoid “band-aid” fixes
- Practical coding habits you can apply immediately:
1. **Validate inputs** (never trust the user)
2. **Use safe defaults** (least privilege, secure libraries)
3. **Fail securely** (errors should not leak secrets)
4. **Keep it simple** (complexity breeds mistakes)


## Hands-On Labs
[Lab 1 – Exploit & Patch OWASP Top 10](/courseFiles/Section_01-secureCoding_Basics/Lab1.md)

**Goal** - Get familiar with the OWASP Top 10 by exploiting two classic vulnerabilities (SQL Injection + Cross-Site Scripting), then patching them in code

<br><br>

lab2_input_validation_and_sanitization


***                                                       

<b><i>Continuing the course?</b>
</br>
[Click here for the Next Section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)</i>

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_00-welcome/intro.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
