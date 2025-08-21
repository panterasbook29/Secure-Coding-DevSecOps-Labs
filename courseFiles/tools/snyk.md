**Snyk** is a developer-first security platform that helps find and fix vulnerabilities in:
- **Open-source dependencies** (SCA – Software Composition Analysis)
- **Container images** (Docker, Kubernetes)
- **Infrastructure as Code** (IaC) (Terraform, Kubernetes manifests, Helm charts)
- **Code scanning** (SAST)

It integrates seamlessly into developer workflows (CLI, IDEs, GitHub, GitLab, Jenkins, etc.) to enforce **shift-left** security in the SDLC.

## Setup
```bash
sudo apt update
```
```bash
sudo apt install npm
```
```bash
sudo npm install -g snyk
```
```bash
snyk --version
```

Now you have to make an account(there is free tier available)
```bash
snyk auth
```

## Usage
**Open-Source Dependency Scanning** - Run in a project directory (with ``package.json``, ``requirements.txt``, ``pom.xml``)
```bash
snyk test
```
Or to monitor continuosly
```bash
snyk monitor
```

**Container Image Scanning**
```bash
snyk container test <image-name>
```

**Infrastructure as Code (IaC) Scanning**

Scan Terraform, Kubernetes, or Helm configs
```bash
snyk iac test
```


**Source Code (SAST) Scanning**
```bash
snyk code test
```

**Fixing Vulnerabilities**
```bash
snyk wizard
```


---
[Back to the section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)
