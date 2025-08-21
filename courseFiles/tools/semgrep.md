**Semgrep** is a lightweight static analysis tool for finding bugs, enforcing code standards, and preventing security vulnerabilities. It’s designed to be fast, customizable, and easy to integrate into developer workflows, CI/CD pipelines, and DevSecOps practices

### Why use Semgrep?
- Finds security issues early (QL injection, XSS, hardcoded secrets)
- Enforces secure coding standards with custom rules
- Works across multiple languages: Python, JavaScript, Go, Java, C, etc
- Integrates seamlessly into GitHub, GitLab, Bitbucket, Jenkins, and more

## Setup 
```bash
sudo apt update
```
```bash
sudo apt install python3-pip
```
```bash
pip install semgrep
```

Check it works
```bash
semgrep --version
```

## Usage
**Quick Scan with Built-in Rules**
```bash
semgrep --config=auto .
```

---

**Using Public Rule Registry**

Semgrep maintains a [public registry of rule](https://semgrep.dev/explore)

Examples: 

- ``p/security-audit`` -> security audit rules
- ``p/secrets`` -> detects API keys, tokens, credentials
- ``p/xss`` -> cross-site scripting patterns
```bash
semgrep --config=p/security-audit .
```

---

**Login to get access to more rules**
```bash
semgrep login
```



## Writing custom rules
**Example:** Detect use of ``eval()`` in **Python**
```bash
rules:
  - id: avoid-eval
    patterns:
      - pattern: eval(...)
    message: "Avoid using eval(); it can lead to code injection vulnerabilities."
    severity: ERROR
    languages: [python]
```

---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)
