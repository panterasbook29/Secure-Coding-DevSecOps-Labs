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



```bash
snyk test
```
<img width="1273" height="630" alt="image" src="https://github.com/user-attachments/assets/9abe7edc-d068-4063-8bfe-43865a8e1230" />






---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)
