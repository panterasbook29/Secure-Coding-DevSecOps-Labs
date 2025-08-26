
# CI/CD & Secrets Management

## 1. Introduction & learning outcomes

**Scope.** This section explains why secrets are central to CI/CD security, how they are misused and leaked in pipeline contexts, and what high‑level design and governance decisions reduce risk. 

---

## 2. Core concepts and vocabulary

- **Secret** — Any material that, if disclosed, could lead to unauthorized access, modification, or disclosure of systems or data. Examples: API keys, database passwords, TLS private keys, SSH private keys, tokens, signing keys, encryption keys.

- **Secrets Manager / Vault** — A specialized service that stores secrets securely, controls access, provides audit trails, supports rotation, and often issues short‑lived credentials.

- **Ephemeral credentials / dynamic secrets** — Credentials that are valid only for a short window or for a specific session. Often generated on demand by a Vault or issuance system to reduce the impact of leaks.

- **Secret injection** — The mechanism by which secrets are made available to a process (CI job, container, application) at runtime without embedding them into source code or artifacts.

- **Least privilege** — The principle that an identity (human, service, or CI agent) should have only the minimal permissions required for its role.

- **Blast radius** — The scope of damage that results from a secret being compromised. Design decisions aim to minimize blast radius.

- **Secret lifecycle** — The full lifespan of a secret from creation through use, rotation, revocation, archival, and destruction.

- **Secret sprawl** — Proliferation of secrets across many locations (repos, files, images, builds) which increases risk and reduces manageability.

---

## 3. CI/CD as an attack surface: threat models

CI/CD pipelines connect source, build, test, artifact storage, and deployment systems — often with privileged access to environments. Threats to consider include:

- **Credential theft & exfiltration.** Attackers target pipeline systems to harvest secrets that enable lateral movement into production or cloud resources.
- **Pipeline trojaning / supply‑chain insertion.** Malicious changes introduced into the build or deploy process can result in compromised artifacts being delivered to users or environments.
- **Compromised third‑party actions/plugins.** Community or marketplace CI actions that run in pipeline context may contain backdoors or poorly secured code that leaks secrets.
- **Runner/agent compromise.** Persistent or shared build agents can retain secrets or provide an attacker a foothold if not ephemeral and isolated.
- **Misconfiguration & privilege misuse.** Overly broad roles or secrets with overly long lifetimes increase the chance of misuse or accidental exposure.

When constructing a threat model, enumerate the assets (source code, artifacts, deployment credentials), actors (developers, CI service, third‑party actions), entry points (pull requests, package dependencies, 3rd‑party integrations), and potential impact (data breach, code integrity loss, service disruption).

---

## 4. Secret types, classification and sensitivity

Not all secrets are equal; classify secrets to manage risk and controls appropriately.

**Categories & examples:**
- **Static long‑lived credentials:** ex: long‑lived API keys, service account tokens. Higher risk if leaked.
- **Short‑lived / dynamic credentials:** ex: database credentials issued for a short session. Lower blast radius.
- **Encryption keys:** ex: master keys for disk or vault encryption. Extremely sensitive; often require hardware or HSM protection.
- **Signing keys:** ex: artifact signing or TLS private keys. Compromise undermines trust and non‑repudiation.

**Sensitivity tiers (example):**
- **Tier 1 — Critical:** Keys that grant production access, signing keys, root credentials, HSM keys. Highest protections: HSM, hardware‑backed, multi‑party controls.
- **Tier 2 — High:** Service account keys, long‑lived tokens for sensitive services. Protect with tight ACLs and short lifetimes where possible.
- **Tier 3 — Medium:** API keys for non‑sensitive services, staging database passwords.
- **Tier 4 — Low:** Non‑sensitive tokens or keys that only access low‑value/test systems.

Use classification to decide storage, rotation frequency, who can approve access, and required audit controls.

---

## 5. Principles for secure secrets management

These high‑level principles form the foundation of secure CI/CD secrets handling.

1. **Don’t store secrets in source control.** Repositories (including forks and pull requests) are high‑risk storage. Use dedicated secret stores and prevent accidental commits with scanners and pre‑commit hooks.

2. **Centralize secrets management.** A centralized manager (vault) provides a single policy surface, auditing, automated rotation, and reduces sprawl.

3. **Prefer short‑lived, dynamic credentials.** Minimizes exposure window and makes compromise less useful.

4. **Apply least privilege & just‑in‑time access.** Grant minimal required permissions and consider time‑bound approvals for sensitive operations.

5. **Use ephemeral build environments.** Ephemeral runners reduce residual state and prevent secrets persistence across jobs.

6. **Treat secrets as data, not configuration.** Secrets require lifecycle management, access control, and auditability — unlike ordinary configuration which can be freely stored with the code.

7. **Audit & monitor access to secrets.** Maintain clear, tamper‑evident logs of who accessed what and when, and alert on unusual patterns.

8. **Harden third‑party steps & dependencies.** Vet and pin third‑party actions, and restrict which actions can run in sensitive contexts.

9. **Avoid secrets in outputs.** Prevent printing of secrets in logs or artifact metadata and obfuscate any accidental exposures quickly.

10. **Plan for compromise with rotation & revocation.** Assume secrets will leak at some point — design for quick revocation and automated replacement.

---

## 6. Architectural patterns for secrets in CI/CD

>[!TIP]
>
>This section describes common architectural approaches, the trade‑offs they bring, and suitability.

### A. CI provider native secrets store

**Description:** Use the CI/CD system’s built‑in secrets mechanism (encrypted variables) and scope them to repositories or environments.

**Pros:** Easy to use; integrated with workflows; no external system required.

**Cons:** Limited features (auditing, dynamic secrets), and a single compromise of CI provider access can expose many secrets.

**When to use:** Small projects, low sensitivity secrets, or as a complement to a vault for non‑critical values.

### B. Centralized secrets manager (Vault, cloud secret store)

**Description:** CI jobs authenticate to a dedicated secrets manager at runtime to retrieve secrets.

**Pros:** Strong policies, dynamic credential issuance, leasing, detailed audit trails, and central governance.

**Cons:** More operational complexity; requires careful authentication/bootstrapping of CI jobs.

**When to use:** Medium to large organizations, production secrets, or where audit/rotation is required.

### C. Encrypted secrets in repo (SOPS / SealedSecrets)

**Description:** Store encrypted secrets in Git for GitOps workflows; decryption occurs in a trusted context (ex: cluster sidecar or operator).

**Pros:** Works well with GitOps; maintains versioning and pull‑request traceability.

**Cons:** Key management for decryption keys is critical; risk if decryption keys are leaked.

**When to use:** GitOps pipelines where storing encrypted manifests in Git is operationally desirable.

### D. External credential injection services (ex: sidecars, init containers, CSI providers)

**Description:** During runtime, a platform component injects secrets into a workload (Kubernetes CSI driver for Vault) without storing them in the image or Git.

**Pros:** Workloads do not hold secrets at rest; access can be fine‑grained and audited.

**Cons:** Platform dependency; must secure the injection mechanism and the node/agent running it.

**When to use:** Containerized deployments (Kubernetes) requiring runtime retrieval of secrets with minimal persistent storage.

### E. Brokered short‑lived credentials (broker issuing temporary cloud tokens)

**Description:** A broker service exchanges pipeline identity for short‑lived cloud credentials (STS tokens, ephemeral DB user).

**Pros:** Minimizes long‑lived credentials and integrates with cloud IAM.

**Cons:** Broker itself needs protection and monitoring.

**When to use:** Cloud environments where native IAM supports ephemeral credentials.

---


## 7. Authentication & identity for pipelines

**Overview.** Authentication for pipelines answers a deceptively simple question: *how does a CI job prove who it is so it can request secrets or cloud credentials without embedding long‑lived keys?* The answer shapes the security posture: a weak bootstrapping model leads to long‑lived credentials, secrets-in-repos, and large blast radii. Below we expand the authentication options, typical flows, threats to each approach, and key design tradeoffs.

### 7.1 Requirements for a good pipeline identity model
- **Non‑repudiation & auditability:** Each pipeline invocation should be attributable to an identity (a repository, workflow, or actor) so access to secrets can be audited and abnormal access detected.
- **Minimal standing privileges:** Avoid giving the pipeline broad, always‑valid permissions — prefer scoped, time‑bounded privileges.
- **Difficult to spoof:** The authentication mechanism should be resilient to tampering (ex: a forked PR should not be able to impersonate the main repository and access prod secrets).
- **Practical and automatable:** The model should be automatable so developers are not tempted to create workarounds (persistent keys, service accounts in code).

### 7.2 Common authentication options 

**OIDC federation (recommended modern approach)**
- **How it works:** The CI provider issues an OIDC token for the running job, which encodes claims such as repository, workflow, job id, and actor. The secrets backend (or cloud IAM) validates the token, checks claims against a mapping policy, and issues short‑lived credentials or returns secrets.
- **Benefits:** No static secret is required in the repo; tokens are short‑lived and can be validated cryptographically; fine‑grained mapping allows scoping by repo and environment.
- **Risks to manage:** Misconfigured claim mappings or overly permissive trust relationships can allow token misuse. Forked pull requests sometimes run in untrusted contexts — policies should forbid giving such job tokens access to sensitive resources.

**AppRole / role-based bootstrap (Vault-style)**
- **How it works:** A role is defined in the vault with policies; the CI job authenticates by presenting a role id and a secret (or another proof) to obtain a token. Role bindings restrict what resources can be requested.
- **Benefits:** Flexible policy model, can be integrated with existing vault machinery, supports lease‑based tokens.
- **Risks to manage:** The initial secret used for authentication must be protected; typically it is kept in the CI provider's secrets store or ephemeral environment. If that secret becomes long‑lived or widely shared, it undermines security.

**Cloud provider service accounts / machine identities**
- **How it works:** CI jobs run under an IAM identity controlled by the cloud provider (service account). That identity is granted permissions to access secret stores or specific resources.
- **Benefits:** Leverages cloud IAM controls and logging; often integrates with cloud provider tooling for temporary credentials.
- **Risks to manage:** Service account keys can be long‑lived if not managed properly. Also, if many pipelines share the same service account, the blast radius of compromise is large.

**Certificates and signed assertions**
- **How it works:** The pipeline holds a private key (or agent) that can sign assertions. The secrets backend validates signatures and issues tokens.
- **Benefits:** Strong cryptographic assurance if keys are secured (HSM-backed or ephemeral agents). Useful where OIDC is not available.
- **Risks to manage:** Key protection and rotation are critical. Private keys embedded in images or repos are an anti‑pattern.

### 7.3 Threats & mitigations specific to pipeline identity
- **Forked pull request abuse:** Disallow access to production secrets for untrusted contexts; require manual approval for sensitive environments.  
- **Replay or token reuse:** Enforce very short token lifetimes, and tie tokens to job ids and nonces.  
- **Overly broad trust relationships:** Scope trust to exact repository names, branches, or workflow IDs.  
- **Bootstrap secret leakage:** Minimize what must be stored in the CI provider; prefer OIDC or ephemeral role exchanges instead of static credentials.


---

## 8. Secret injection patterns and runtime handling 

**Overview.** Once authentication is solved, the next design question is how to hand secrets to the process safely — without persisting them where attackers can find them.

### 8.1 Pattern comparisons (strengths & weaknesses)

**Environment variables**
- **Pros:** Simple, supported by most tooling, straightforward to pass into build/test processes.  
- **Cons:** Environment variables can be leaked via `ps` listings on shared systems, captured in logs accidentally, or inherited by child processes. They may also be visible to debugging tools if not restricted.
- **Mitigations:** Avoid echoing env vars; use ephemeral runners; filter sensitive env vars from logs; use process isolation.

**In‑memory files / tmpfs mounts**
- **Pros:** Limits exposure to runtime; strict file permissions restrict read access; easier to avoid accidental printing.  
- **Cons:** Some platforms may swap memory to disk; careful configuration of tmpfs and node permissions is needed.
- **Mitigations:** Mount as tmpfs where available; configure the platform to avoid swapping sensitive pages to disk; secure node-level access.

**Agent/sidecar approach**
- **Pros:** Secrets are never present in the process environment; the app requests secrets via a local API with controlled access. This is powerful for complex workloads.  
- **Cons:** Introduces another trusted component; the agent must be carefully secured to prevent local attacks.
- **Mitigations:** Secure the IPC channel (Unix sockets with permissions), harden the agent, and monitor agent requests.

**STDIN / pipeline pipes**
- **Pros:** Avoids environment or disk; transient.  
- **Cons:** Not all tools support reading secrets from STDIN; complex scripting may accidentally capture values.  
- **Mitigations:** Use this pattern where supported and ensure command histories and logs do not capture the inputs.

### 8.2 Operational concerns
- **Core dumps:** Ensure core dumps are disabled for processes handling secrets, or configure `ulimit` and OS settings to prevent sensitive memory from being written to disk.  
- **Process listings:** Avoid passing secrets as CLI arguments; some systems expose process command lines to other users.  
- **Container images:** Never bake secrets into images; use runtime injection only.  
- **Cleanup:** Explicitly zero memory or remove files where possible after use; rely on ephemerality of runner environments.

### 8.3 Patterns in Kubernetes & container orchestrators
- **CSI secrets driver / Vault CSI provider:** A common pattern where Kubernetes mounts secrets from a secret provider into pods on demand. This can provide ephemeral mounts and integrates with RBAC.  
- **Sidecar injectors:** A sidecar container authenticates to Vault and writes secrets to an in‑memory volume; the main container reads them without ever contacting Vault.  
- **SealedSecrets / SOPS for GitOps:** Encrypted manifests are stored in Git and decrypted inside the cluster by a controller with the decryption key; good for GitOps but requires strong key custody.

---

## 9. Secret lifecycle: generation, rotation, revocation, archival

**Overview.** Treating secrets like ephemeral, managed objects reduces risk. The lifecycle mindset emphasizes automation and auditability.

### 9.1 Generation best practices
- Use cryptographically secure random generators (avoid homegrown RNGs).  
- Consider HSM or cloud KMS for root keys or signing keys.  
- Tag secrets with metadata: owner, purpose, environment, classification tier, and creation date.

### 9.2 Distribution & usage
- Distribute secrets only to authorized identities and only at runtime.  
- Prefer dynamic issuance when possible: instead of storing DB admin creds, request short‑lived DB user creds from a broker.  

### 9.3 Rotation strategies
- **Scheduled rotation:** Regular automated replacement based on sensitivity (ex: daily for ephemeral tokens, quarterly for service keys).  
- **Event-driven rotation:** Rotate on suspicious activity, human termination, role change, or suspected compromise.  
- **Rolling rotation:** For production services, perform rolling updates so consumers refresh credentials without downtime.

### 9.4 Revocation & emergency response
- Have a documented and automated revocation path: revoke tokens, disable keys, and cut off access to compromised identities.  
- Post‑revocation, rotate dependent secrets and roll forward with new credentials.  
- Maintain a runbook that includes who must be notified, logs to preserve for forensics, and how to coordinate between CI, platform, and security teams.

---

## 10. Logging, telemetry, and leakage risks 

### 10.1 Why logs matter — the dual nature of observability
Observability is essential: logs, traces, and metrics allow teams to detect failures, investigate incidents, and prove compliance. But logs are also a prime leakage path for secrets. Design choices about what to log, how to redact it, and where logs live directly affect security.

### 10.2 Common leakage vectors in CI/CD
- **Build output and console logs:** Build scripts, test runners, and third‑party tools sometimes print environment variables, error messages, or stack traces containing secrets."  
- **Artifact contents and metadata:** Configuration files, compiled binaries, or package metadata that accidentally include credentials or hardcoded endpoints.  
- **Log aggregation and forwarding:** Centralized logging systems pull logs from many sources; if ingestion points aren’t filtered or access‑controlled, secrets can be stored or viewed widely.  
- **Transient runtime storage:** Temporary files or caches on build agents may persist sensitive material if cleanup fails.  
- **Third‑party integrations:** Monitoring hooks or external services that receive telemetry can inadvertently capture secrets unless sanitized.

### 10.3 Redaction, masking and secure logging practices
- **Redaction at the source:** The most reliable place to redact secrets is before logs leave the process — configure CI runners and agents to filter or mask values designated as secrets.  
- **Structured logs with typed fields:** Use structured logging and classify fields as `secret`, `sensitive`, or `public`. Logging frameworks can then enforce masking policies for sensitive fields.  
- **Tokenization or hashing:** When you must record evidence of an action without storing the secret, store a salted hash or token instead of the secret itself. This supports correlation without disclosure.  
- **Retention minimization:** Reduce retention periods for logs that may contain sensitive context. Archive necessary audit entries to a hardened, access‑controlled store.

### 10.4 Secure aggregation and access controls
- **Limit who can read logs:** Apply RBAC to logging backends; separate roles for engineers, auditors, and security analysts.  
- **Encrypt logs at rest and in transit:** Use TLS for forwarding and strong encryption for storage.  
- **Immutable audit stores for high‑sensitivity events:** For critical secrets operations, write audit events to append‑only stores or WORM storage to prevent tampering.

### 10.5 Detection & response from telemetry
- **Anomaly detection:** Define normal baselines for secret access (volume, sources, times) and alert on deviations (ex: a non‑authorized repo requesting prod secrets).  
- **Correlation across systems:** Combine CI logs, Vault audit logs, cloud IAM logs, and deployment records to build a complete picture during investigations.  
- **Automated containment:** Configure automated actions for high confidence alerts (ex: automatically revoke a token when an exfiltration pattern is detected), but ensure human‑in‑the‑loop for sensitive revocations.

### 10.6 Incident handling for leaked secrets
- **Immediate steps:** Revoke the exposed credential, rotate affected secrets, and quarantine affected artifacts or images.  
- **Forensic preservation:** Preserve relevant logs, job metadata, and runner snapshots for analysis before rotation (copy to a secured forensics store).  
- **Communication and disclosure:** Follow your incident response policy for notifying internal stakeholders and external parties if required by regulation.

---

## 11. Governance, policy, and compliance considerations 

### 11.1 Translating technical controls into policy
Policies reduce ambiguity. Write policies that specify required technical controls (ex: “All Tier‑1 secrets must be stored in the centralized vault and must not be present in Git history”) as well as processes (ex: approval flow for production secrets access).

### 11.2 Defining roles and separation of duties
- **Owners and custodians:** Every high‑sensitivity secret should have a defined owner (business or application owner) and a custodian (platform/security team).  
- **Separation of duties (SoD):** Require that the person who deploys production code is not the sole approver for production secrets changes, for particularly sensitive systems.  
- **Approval workflows:** Use multi‑party approvals for sensitive operations (ex: deploys that access Tier‑1 secrets require two approvers from different teams).

### 11.3 Policy elements to include
- **Classification & handling rules:** Map secret tiers to specific storage, rotation frequency, and access controls.  
- **Access request procedures:** How developers request production credentials, including justifications, expiration, and auditing requirements.  
- **Emergency procedures:** Clear steps for revocation, escalation, and notification in case of suspected compromise.  
- **Audit & review cadence:** Regular policy reviews, periodic audits of secrets inventory, and spot checks of pipeline configurations.

### 11.4 Regulatory & compliance mapping
- **PCI DSS:** Requires strong controls for key management when handling payment information; includes access controls, rotation, and audit trails.  
- **GDPR:** Controls around access to personal data may implicate secrets that grant access to data stores; ensure access is logged and justified.  
- **ISO/IEC 27001:** Requires information security management processes that include key and secrets management.  

Map your organizational compliance needs to concrete technical controls so audits become evidence‑driven rather than ad‑hoc.

---

## 12. Supply‑chain risks & third‑party components

### 12.1 Deep dive: how third‑party steps become exfiltration vectors
Third‑party actions or plugins often run with the same privileges as your steps. If they are compromised or malicious, they can call home with secrets or write artifacts that include credentials. This risk increases when you allow community‑authored steps or broad network egress from build jobs.

### 12.2 Practical isolation design patterns
- **Split workflows by trust level:** Keep untrusted code (open‑source dependencies, community actions) in separate build stages that do not have access to secrets. Only move artifacts to a trusted stage once they pass verification.  
- **Network egress controls:** Block or restrict network egress from build environments unless explicitly required and approved.  
- **Execution sandboxing:** Run community or unreviewed actions in highly constrained sandboxes or ephemeral containers without persistent storage.

### 12.3 Verifying provenance and integrity
- **Artifact signing and verification:** Sign build artifacts and record provenance metadata (which source commit and which workflow produced the artifact). Verify signatures before deployment.  
- **Dependency integrity (SBOMs):** Maintain a Software Bill of Materials for builds and scan dependencies for known vulnerabilities and supply‑chain anomalies.  
- **Pinning and immutability:** Use immutable references (SHAs) for actions and dependencies instead of loose version tags.

---


## 13. Recommended readings and standards 

A curated list for deeper study and policy justification:
- **NIST SP 800‑57 (Key Management)** — Lifecycle and cryptographic key management guidance.  
- **OWASP CI/CD Security Cheat Sheet** — Practical mitigations for CI/CD systems.  
- **SLSA (Supply‑chain Levels for Software Artifacts)** — Framework for supply‑chain integrity.  
- **HashiCorp Vault Best Practices** — Patterns for dynamic secrets, leasing, and vault architecture.  
- **Cloud provider guides:**  AWS, Azure, and GCP best practices for secrets management and IAM.  
- **In‑toto, Sigstore, and Cosign** — Emerging tooling for artifact provenance and signing.  

---



## lab1_hardcoded_secret_detection

## lab2_insecure_pipeline_exploitation


***                                                       

<b><i>Continuing the course?</b>
</br>
[Click here for the Next Section](/courseFiles/Section_04-containerAndCloudSecurity/containerAndCloudSecurity.md)</i>

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_02-staticAnalysisAndDependencies/staticAnalysis.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
