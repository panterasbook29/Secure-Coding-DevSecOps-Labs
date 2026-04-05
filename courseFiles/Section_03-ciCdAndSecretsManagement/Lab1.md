![image](https://github.com/user-attachments/assets/068fae26-6e8f-402f-ad69-63a4e6a1f59e)

# Hardcoded Secrets and Git History

## Goal
Find hardcoded secrets in code and Git history, block new ones locally with a pre-commit hook, and fail CI if secrets are pushed

## Start
```bash
cd ~/Secure_Coding/lab3-1/lab
```
- Initialize a repo
```bash
git init -b main
```
```bash
git config user.email "student@example.com"
```
```bash
git config user.name "Student"
```

- Plant a (fake) secret and commit it

```bash
cat > app.py <<'EOF'
import os

# Bad: hardcoded keys (for demo only)
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef1234"

def main():
    print("App started. Don't ship secrets in code.")
if __name__ == "__main__":
    main()
EOF
```
```bash
git add app.py
```
```bash
git commit -m "feat: initial app with (intentionally) hardcoded secrets"
```

- Full scan (repo + history), redact findings
```bash
gitleaks detect --source . --redact --report-format json --report-path gitleaks-report.json || true
```

<img width="1137" height="182" alt="gitleaks_1" src="https://github.com/user-attachments/assets/480d0782-9eb8-422d-8e30-fee823c6fc6a" />


- Take a quick look:
```bash
cat gitleaks-report.json
```

<img width="1109" height="383" alt="gitleaks_result" src="https://github.com/user-attachments/assets/fab3b437-ab33-445b-a2e3-a8f1a5576196" />


- Notice it flags the `ghp_` token
- It scans **history**, so the first commit shows up
- It didn't flag the `AWS` key, so, like any other tool, it's not perfect, but it flags one of them, and usually where there is one there is more!

- Add a local pre-commit hook to block new secrets
```bash
cat > .pre-commit-config.yaml <<'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks
        args: ["--staged", "--redact"]
EOF
```
```bash
pre-commit install
```
```bash
pre-commit run --all-files || true
```
- Try to add a new secret and watch the commit get **blocked**:
```bash
printf '\nSLACK_BOT_TOKEN="xoxb-111111111111-222222222222-ABCDEFabcdef1234567890"\n' >> app.py
```
```bash
git add app.py
```
```bash
git commit -m "test: try to sneak a slack token" || echo "Pre-commit blocked the secret"
```

<img width="1057" height="395" alt="pre_commit_block" src="https://github.com/user-attachments/assets/8b17978b-0f36-4c75-9e72-1cb1f9501020" />


- Revert the test change
```bash
git restore --staged app.py && git checkout -- app.py
```

`pre-commit` runs Gitleaks on staged changes only

The hook fails fast and prevents the commit

- **Fix the code:** move secrets to env + ``.gitignore``
```bash
cat > .gitignore <<'EOF'
.env
EOF
```

```bash
cat > .env.example <<'EOF'
AWS_ACCESS_KEY_ID=<set-me-in-ci-or-local-env>
AWS_SECRET_ACCESS_KEY=<set-me-in-ci-or-local-env>
GITHUB_TOKEN=<set-me-in-ci-or-local-env>
EOF
```

```bash
cat > app.py <<'EOF'
import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def main():
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, GITHUB_TOKEN]):
        print("Secrets not set (using env). See .env.example")
    else:
        print("All secrets loaded from environment.")
if __name__ == "__main__":
    main()
EOF
```

```bash
git add .gitignore .env.example app.py
```
```bash
git commit -m "fix: read secrets from env; add .env to .gitignore"
```

<img width="892" height="98" alt="secret_fix" src="https://github.com/user-attachments/assets/633d4a9d-1987-48c7-bdd4-750d6c46b0be" />


No secrets in the file anymore

``.env`` excluded from Git; CI/runner will provide secrets via secure store

### Generic bash gate
- Create ``scripts/secrets_gate.sh``:
```bash
mkdir -p scripts
```
```bash
cat > scripts/secrets_gate.sh <<'EOF'
set -euo pipefail
echo "[gate] Secrets scan (Gitleaks)"
gitleaks detect --source . --redact
echo "[gate] OK"
EOF
```
```bash
chmod +x scripts/secrets_gate.sh
```

- Run locally
```bash
./scripts/secrets_gate.sh || echo "Gate failed as expected"
```

---
[Back to the section](/courseFiles/Section_03-ciCdAndSecretsManagement/secretsManagement.md)













