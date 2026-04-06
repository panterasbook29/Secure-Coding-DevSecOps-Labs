![image](https://github.com/user-attachments/assets/068fae26-6e8f-402f-ad69-63a4e6a1f59e)

# Snyk and NPM Audit

## Goal
Find and fix risky third-party packages with Snyk and npm audit

Generate an **SBOM** (CycloneDX) and add a tiny **CI gate** so bad versions don’t sneak back in

## Setup
Should have evrything from the previous labs(**Snyk**, **nodejs**, **npm**, **jq**)

```bash
cd ~/Secure_Coding/lab2-2
```

```bash
npm init -y
```

```bash
npm i lodash@4.17.20 minimist@0.0.8 js-yaml@3.13.1
```

```bash
cat > app.js <<'EOF'
const _ = require('lodash');
const minimist = require('minimist');
const yaml = require('js-yaml');

console.log('Demo app:', _. VERSION ? 'lodash loaded' : 'ok',
            typeof minimist === 'function',
            typeof yaml.safeLoad === 'function');
EOF
```

```bash
npm i
```

To use `Snyk CLI`, you must first create your account here:

- https://app.snyk.io/login

Then create a token to use here:

- https://app.snyk.io/account/personal-access-tokens

Copy the token and set it as an environment variable:

```bash
export SNYK_TOKEN=your_token_here
```

## Start

### Let's scan the project
Run both a native and a third-party scanner:

```bash
npm audit --omit=dev || true
```

<img width="1057" height="563" alt="npm_audit" src="https://github.com/user-attachments/assets/23f9ce96-b4f0-4c74-8c3f-b219db1ace09" />


<br><br>

```bash
snyk test
```

<img width="833" height="543" alt="snyk_test" src="https://github.com/user-attachments/assets/e2c6d14e-7376-4dae-8ffb-d192dfb34222" />


**What to notice**
- Which packages/versions are flagged
- Suggested **upgrade targets**
- Whether the path is a **prod** dependency (matters for gating)


### Generate an SBOM (CycloneDX)

```bash
npx @cyclonedx/cyclonedx-npm --output-file sbom.cdx.json
```

Take a peek
```bash
jq '.components | length' sbom.cdx.json
```

Use this SBOM during incidents (“are we affected by CVE-XYZ?”) and keep it with your build artifacts

### Patch the vulnerable packages
Upgrade to safe lines (don’t hand-edit lockfiles):

```bash
npm i lodash@^4.17.21 minimist@^1.2.8 js-yaml@^4.1.0
```
```bash
rm -f package-lock.json
```
```bash
npm i
```

Now you can rescan to test that the vulnerabilities were solved

## Generic Bash gate (works anywhere)
Behavior: Fails the build if Snyk finds high/critical issues, emits ``sbom.cdx.json`` as an artifact

Create ``scripts/security_gate.sh``:
```bash
mkdir -p scripts
```
```bash
cat > scripts/security_gate.sh <<'EOF'
set -euo pipefail

echo "[gate] installing deps (respect lockfile if present)"
if [ -f package-lock.json ]; then
  npm ci
else
  npm i
fi

echo "[gate] Snyk test (high+ only)"
snyk test --severity-threshold=high

echo "[gate] Generate SBOM (CycloneDX)"
npx @cyclonedx/cyclonedx-npm --output-file sbom.cdx.json

echo "[gate] OK"
EOF
```
```bash
chmod +x scripts/security_gate.sh
```
```bash
./scripts/security_gate.sh
```

<img width="570" height="512" alt="re-test" src="https://github.com/user-attachments/assets/0b0a7029-cdfd-413e-a1b9-f8e2ab27cc72" />


---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)
