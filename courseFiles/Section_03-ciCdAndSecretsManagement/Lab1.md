## Goal
Find hardcoded secrets in code and Git history, block new ones locally with a pre-commit hook, and fail CI if secrets are pushed

## Setup
```bash
git clone https://github.com/gitleaks/gitleaks.git
```
```bash
cd gitleaks
```
```bash
make build
```
```bash
sudo mv gitleaks /usr/local/bin/
```
```bash
pip3 install --user pre-commit
```
```bash
sudo apt install git
```

## Start
```bash
mkdir -p ~/section03-ciCdAndSecretsManagement/lab1 && cd ~/section03-ciCdAndSecretsManagement/lab1
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
<img width="476" height="202" alt="image" src="https://github.com/user-attachments/assets/f6ec0b0e-07bf-460c-be63-701a119d7cdf" />

- Take a quick look:
```bash
cat gitleaks-report.json
```
<img width="1350" height="443" alt="image" src="https://github.com/user-attachments/assets/7df00bb4-261c-4372-9f98-cfbb1e50d87a" />

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

<img width="719" height="464" alt="image" src="https://github.com/user-attachments/assets/3598d201-27ed-4667-b776-cb9a5eedd899" />


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

<img width="726" height="101" alt="image" src="https://github.com/user-attachments/assets/f8bb9efc-55d3-4131-919c-014aaf5de89f" />

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













