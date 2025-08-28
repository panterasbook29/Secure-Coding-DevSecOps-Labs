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

# ⚠️ Bad: hardcoded keys (for demo only)
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


- 
























