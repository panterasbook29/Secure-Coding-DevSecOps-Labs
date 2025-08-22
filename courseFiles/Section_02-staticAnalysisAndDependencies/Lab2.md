## Goal
Find and fix risky third-party packages with Snyk and npm audit

Generate an **SBOM** (CycloneDX) and add a tiny **CI gate** so bad versions don’t sneak back in

## Setup
Should have evrything from the previous labs(**Snyk**, **nodejs**, **npm**, **jq**)

```bash
mkdir -p ~/section02-lab2 && cd ~/section02-lab2
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


## Start

### Let's scan the project
Run both a native and a third-party scanner:

```bash
npm audit --omit=dev || true
```
<img width="983" height="507" alt="image" src="https://github.com/user-attachments/assets/81e5ae4d-353e-4372-b584-712cd5fca3a3" />

<br><br>

```bash
snyk test
```
<img width="1273" height="630" alt="image" src="https://github.com/user-attachments/assets/9abe7edc-d068-4063-8bfe-43865a8e1230" />

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

<img width="644" height="605" alt="image" src="https://github.com/user-attachments/assets/30740190-163e-4523-83ee-e1ab12413f2a" />


---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)
