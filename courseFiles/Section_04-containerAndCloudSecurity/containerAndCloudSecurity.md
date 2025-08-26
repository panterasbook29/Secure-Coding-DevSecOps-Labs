# Container And Cloud Security


## 1. Introduction 

**Scope.** This chapter explains the theoretical foundations required to design, operate, and secure containerized applications and cloud infrastructure. It emphasizes architectural tradeoffs, common attack vectors, defense‑in‑depth patterns, and governance considerations.

---

## 2. Core concepts

- **Container image** — A layered, immutable artifact that packages an application and its runtime dependencies.
- **Container registry** — A storage and distribution service for container images (public or private).  
- **Container runtime** — The software that runs containers (containerd, runc, CRI‑O).  
- **Orchestrator** — A control plane that schedules and manages containers at scale (ex: Kubernetes).  
- **Pod / Task** — Smallest deployable unit in an orchestrator (Kubernetes Pod contains one or more containers).  
- **Node** — A host (VM or physical) running container runtime and scheduled workloads.  
- **Sidecar** — Secondary container running alongside application container to provide auxiliary services (logging, proxying, secrets retrieval).  
- **Admission controller** — Pluggable component in orchestrators that intercepts creation/updates of objects and enforces policies.  
- **CNI (Container Network Interface)** — Plugin model for networking in Kubernetes.  
- **Immutable infrastructure** — Pattern: do not mutate running systems; replace with updated images.  
- **Supply chain provenance** — Evidence about how an artifact was built: source commit, build environment, dependencies, and signatures.  

---

## 3. Container fundamentals and the attack surface

### 3.1 Why containers change the game
Containers increase agility and density but alter the attacker’s target: instead of monolithic hosts, there are many ephemeral workloads, shared kernel surfaces, and complex control planes. Security must adapt to dynamic topology and ephemeral identities.

### 3.2 Key assets to protect
- Container images and build artifacts.  
- Container registries and artifact stores.  
- Orchestrator control plane (API servers, controllers).  
- Node OS and container runtimes.  
- Secrets, config maps, and mounted volumes.  
- Network connectivity and service meshes.  
- Logs, telemetry, and artifact signing keys.

### 3.3 Core attack vectors
- **Malicious or compromised images** — images that include backdoors, malware, or hidden credentials.  
- **Registry compromise** — malware that replaces images, or unauthorized pushes to registries.  
- **Orchestrator control plane attacks** — stolen kubeconfig, API token exfiltration, or privileged admission bypass.  
- **Node escape attacks** — container vulnerabilities exploited to break out to the host kernel or filesystem.  
- **Lateral movement** across the cluster via weak network segmentation or overly permissive service accounts.  
- **Supply‑chain tampering** — compromised build systems or dependencies introduce malicious code before deployment.  

### 3.4 Threat modeling for containerized apps
When threat modeling, include: which images are used, who can push to registries, what identities have admin access to the cluster, what network flows are allowed, and where sensitive data is stored or accessible at runtime.

---

## 4. Image supply chain: building secure container images

A secure image pipeline prevents introduction of malicious content and provides assurance about what is run in production.

### 4.1 Principles for secure builds
- **Reproducible and minimal builds:** Smaller base images reduce attack surface. Reproducible builds improve traceability.  
- **Immutable artifacts:** Build once, sign, and promote artifact across environments rather than rebuilding per environment.  
- **Least privilege in build environment:** Builders and signing keys should be tightly controlled and used only by automated systems.  
- **Dependency vetting & SBOMs:** Produce a Software Bill of Materials listing all dependencies; scan for known vulnerabilities and suspicious packages.  

### 4.2 Recommended Dockerfile and image build practices
- Use official, minimal base images (distroless, scratch) where possible.  
- Order Dockerfile instructions to leverage caching for reproducible layers but avoid injecting secrets during build.  
- Remove build‑time artifacts and package manager caches in the same layer to avoid leaving sensitive data.  
- Run as non‑root user inside the image unless root is strictly necessary.  
- Install only required runtime dependencies; avoid including compilers and debuggers in production images.  

### 4.3 Signing and provenance
- **Artifact signing:** Sign images with tools like Cosign so consumers can verify origin and integrity.  
- **Provenance metadata:** Record build provenance (commit id, builder image, build env) and attach to images.  
- **Promote signed images across environments:** Use a signed image for staging and promote the same signed digest to production to avoid rebuild inconsistencies.

---

## 5. Registry security and artifact provenance

Registries are high‑value targets. Protect them with strong controls and verify images before deployment.

### 5.1 Registry hardening
- Use private registries with authentication and RBAC.  
- Enforce image immutability for production registries; prevent force‑push or tag overwrite.  
- Enable vulnerability scanning on push; block images with critical vulnerabilities for production.  
- Use TLS everywhere and validate certificates for registry endpoints.  

### 5.2 Access control & auditing
- Limit who can push images; require CI/CD systems to push signed images rather than developers pushing directly.  
- Maintain audit logs for pushes, pulls, and permission changes.  
- Implement short‑lived tokens for registry access when possible.

### 5.3 Provenance verification before deployment
- Use signature verification and SBOM checks in admission controllers or CI gates.  
- Require that deployed images be signed and provenance metadata match the expected build pipeline.

---

## 6. Orchestration security

Kubernetes is the most widely used orchestrator and therefore a common target; understanding its control plane, RBAC, and extensibility points is critical.

### 6.1 Cluster architecture & attack surface
- **API server:** Central control plane for cluster state. Exposed API endpoints must be authenticated and authorized.  
- **etcd:** The cluster datastore containing secrets and state; must be encrypted at rest and access restricted.  
- **Controller managers / schedulers:** Service accounts and controllers act with privileges—limit and audit them.  
- **Kubelets & nodes:** Each node runs kubelet which communicates with the API; kubelet compromise can be serious.

### 6.2 Authentication & authorization
- **Authentication:** Use strong auth to the API server (OIDC, x509 client certs, cloud IAM).  
- **RBAC:** Define fine‑grained roles and avoid cluster‑admin for human users. Prefer least privilege for controllers and operators.  
- **Admission controllers:** Use mutating and validating admission controllers to enforce security posture (PodSecurityAdmission, OPA/Gatekeeper, Kyverno).

### 6.3 Secrets management in Kubernetes
- Kubernetes Secrets are base64‑encoded by default — not encrypted. For production, enable EncryptionConfig for etcd or use external secret stores (Vault, Secrets Store CSI Driver).  
- Limit which service accounts can mount or access secrets and audit secret access.

### 6.4 Pod security and policies
- **Pod Security Standards / Policies:** Enforce restrictions on privilege escalation, host path mounts, running as root, and allowed capabilities.  
- **NetworkPolicies:** Control pod‑to‑pod communications via network policy enforcement.  
- **Resource quotas and limits:** Prevent denial of service from resource exhaustion by bounding CPU/memory.

### 6.5 Extension points and risks
- **Custom controllers and operators:** They run with permissions and can escalate privileges if poorly designed—treat them like code that affects cluster state.  
- **Admission webhooks:** They can mutate or validate objects; ensure their availability and security (TLS, auth).  

---

## 7. Runtime container security and hardening

Runtime security focuses on minimizing the attack surface of running workloads and detecting malicious behavior.

### 7.1 Host & runtime hardening
- Keep the host OS minimal and patched; use immutable infrastructure and rebuild nodes rather than patching in place.  
- Harden the container runtime (use updated versions of containerd/runc), enable seccomp and safer default OCI runtimes.  
- Reduce the kernel attack surface by disabling unused features and using kernel hardening features (secure boot, kernel lockdown where applicable).

### 7.2 Workload hardening
- Run containers as non‑root users; drop unnecessary Linux capabilities.  
- Use seccomp, AppArmor or SELinux profiles to restrict syscalls and file access.  
- Disable privilege escalation and use read‑only root filesystems where possible.  
- Limit inbound and outbound network access and apply minimal set of capabilities required.

### 7.3 Detection and runtime protection
- Use runtime threat detection tools (ex: Falco) to detect suspicious in‑container behaviors: unexpected execs, shell access, container escapes attempts, and suspicious outbound connections.  
- Monitor process, file, and network activity within containers; correlate with orchestrator events.

### 7.4 Immutable workload patterns
- Immutable images and declarative deployments reduce configuration drift and help ensure what runs in production corresponds to what was reviewed and signed.

---

## 8. Networking and microsegmentation

Secure network architecture prevents lateral movement and reduces blast radius.

### 8.1 Layered network controls
- **Cluster network policies** — Use CNI plugins that support NetworkPolicy and enforce pod‑level egress/ingress rules.  
- **Service mesh** (optional) — Use a service mesh (ex: Istio, Linkerd) for mTLS between services, centralized policy enforcement, and observability.  
- **Ingress/Egress controls** — Gate ingress via API gateways and WAFs; control egress with egress gateways or NATs to limit data exfiltration.

### 8.2 Identity and mutual TLS
- Implement service‑to‑service identity (mTLS) so services authenticate each other independent of network address.  
- Use short‑lived certificates issued by a control plane (mesh or PKI) and automate rotation.

### 8.3 Network segmentation patterns
- Segment by environment (dev/stage/prod), by team, or by sensitivity.  
- Apply zero‑trust principles: never implicitly trust traffic within the cluster; verify identity and authorization at the service layer.

---

## 9. Storage, volumes, and data protection

Containers are often stateless, but when state is required, storage must be protected.

### 9.1 Types of volumes and risks
- **HostPath / local volumes:** High risk if used for persistent app data: may allow privilege escalation or data leakage.  
- **Networked storage (NFS, CSI drivers):** Must be access‑controlled and encrypted if sensitive.  
- **Ephemeral volumes and caches:** Ensure cleanup to avoid sensitive residual data.

### 9.2 Data protection strategies
- Encrypt data at rest using provider KMS or disk encryption layers.  
- Use volume encryption for sensitive PersistentVolumes and control who can mount these volumes.  
- For backups and snapshots, ensure encryption and access control, and protect backup credentials.

### 9.3 Secrets and configuration storage
- Avoid storing secrets in plain files in images; use secrets managers and mount them at runtime with tight ACLs.  
- Protect configuration that contains sensitive endpoints or access controls with the same rigor as secrets.

---

## 10. Identity, authentication, and authorization in cloud-native environments

Identity is the cornerstone of cloud security: treat humans, workloads, and control plane components as identities.

### 10.1 Workload identity
- Use workload identity mechanisms (ex: Kubernetes ServiceAccount mapped to cloud IAM via Workload Identity, or projected tokens validated by the cloud) so pods can assume cloud identities without embedding keys.  
- Assign least privilege to workload identities and apply attribute based access where supported.

### 10.2 Human identity & developer workflows
- Enforce strong authentication for developer access (SSO, MFA, short‑lived sessions).  
- Avoid long‑lived static keys for humans; prefer temporary credentials and audits of elevated operations.

### 10.3 Authorization models
- Use least‑privilege RBAC across orchestrator and cloud IAM.  
- Consider policy engines (OPA/Gatekeeper, IAM conditions) for contextual authorization (ex: time, source IP, repository tag).  

---

## 11. Cloud provider security models and shared responsibility

Cloud security blends provider responsibilities with customer responsibilities; understanding this split is critical.

### 11.1 Shared responsibility model (conceptual)
- **Cloud provider responsibility:** The provider secures the cloud infrastructure (physical hosts, hypervisor, host OS, managed services' underlying infrastructure).  
- **Customer responsibility:** The customer secures their data, workloads, identity configurations, network controls, and application code deployed in the cloud.

### 11.2 Service models and implications (IaaS, PaaS, SaaS)
- **IaaS:** More customer responsibility (OS, runtime hardening).  
- **PaaS / managed containers:** Provider manages more layers (control plane), but customers still responsible for app security and configuration.  
- **SaaS:** Most security is managed by provider; customers control data and user access.

### 11.3 Provider‑specific controls and features
- Use cloud provider features for identity federation, KMS/HSM, VPC service controls, private endpoints, and managed security services where they align with policy and risk tolerance.

---

## 12. Infrastructure as Code (IaC) security

>[!TIP]
>
>IaC increases speed but can bake insecure defaults into infrastructure. Treat IaC templates as first‑class security artifacts.

### 12.1 Common IaC risks
- Hardcoded secrets in templates, permissive network rules, overly broad IAM permissions, and misconfigured storage buckets.  

### 12.2 Secure IaC practices
- Store IaC in version control and peer‑review changes.  
- Use static analysis and policy as code (ex: Terraform Sentinel, OpenPolicyAgent / Conftest) to catch insecure patterns before apply.  
- Separate templates by environment and reduce blast radius via modular design.  

---

## 13. Observability: logging, metrics, tracing and detection

Observability enables detection and response but must be designed to avoid leaking secrets and scale with ephemeral environments.

### 13.1 Log collection and centralization
- Collect node, container and orchestrator logs centrally with strong access controls.  
- Ensure logs are labeled with contextual metadata (pod, node, cluster, image digest) to speed investigations.

### 13.2 Metrics and tracing
- Collect resource and application metrics to detect anomalies (CPU spikes, request latencies).  
- Distributed tracing helps identify behavior changes and suspicious flows between services.

### 13.3 Runtime detection patterns
- Define detection rules for runtime anomalies (unexpected execs, new binaries, unexpected egress).  
- Correlate CI/CD events (new build promoted) with runtime telemetry for timeline reconstruction.

---

## 14. Incident response and forensics in container/cloud environments

>[!IMPORTANT]
>
>Containers and cloud introduce new challenges for forensics due to ephemerality and distributed state.

### 14.1 Readiness & playbooks
- Maintain playbooks that cover common incidents: image compromise, cluster breach, data exfiltration, and cryptomining.  
- Define roles and escalation paths; preserve evidence before rotating secrets or reimaging nodes.

### 14.2 Forensic data sources
- Container image digests, registry logs, orchestrator audit logs, host-level logs, network captures (where feasible), cloud API logs, and persistent storage snapshots.  
- Preserve etcd snapshots if API or control plane compromise is suspected (ensure they are securely stored).  

### 14.3 Containment & recovery
- Quarantine affected nodes or workloads, revoke credentials, roll forward with known-good signed images, and rebuild nodes from trusted images.  
- After containment, perform root cause analysis and update controls and playbooks.

---



## lab1_insecure_dockerfile_and_fix

## lab2_cloud_bucket_misconfiguration



***

<b><i>Continuing the course?</b>
</br>
[Click here for the Next Section](/courseFiles/Section_05-threatModelingAndReporting/threatModelingAndReporting.md)</i>

<b><i>Want to go back?</b>
</br>
[Click here for the Previous Section](/courseFiles/Section_03-ciCdAndSecretsManagement/secretsManagement.md)

<b><i>Looking for a different section? </b></br>[Back to Section Directory](/coursenavigation.md)</i>
