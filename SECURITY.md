# 🔐 Security Policy

Thank you for helping keep **The Last Signal** safe.

The Last Signal is an open-source MMORPG currently under active development. Security is taken seriously, but some parts of the project are still experimental and should not be considered production-ready.

---

## 📌 Supported Versions

The Last Signal is currently under active development.

At this stage, there is no long-term stable release with a formal security-support lifecycle.

Security fixes are therefore primarily focused on the current development version.

| Version                         | Supported      |
| ------------------------------- | -------------- |
| Development / `main`            | ✅ Yes          |
| Older development versions      | ⚠️ Best effort |
| Unreleased / abandoned branches | ❌ No           |

---

## 🚨 Reporting a Security Vulnerability

If you believe you have discovered a security vulnerability in The Last Signal, please report it **privately**.

### 🔐 Preferred method

Please use **GitHub's Private Vulnerability Reporting** for this repository.

You can access it from the repository's **Security** tab:

**Security → Advisories → Report a vulnerability**

Private vulnerability reports allow the maintainers to investigate security issues without immediately exposing potentially sensitive technical details publicly.

### 📋 What to include

Please provide as much relevant information as possible:

* A clear description of the vulnerability
* The affected component
* The affected file or module, if known
* Steps to reproduce the issue
* The potential security impact
* Relevant logs or error messages
* A proof of concept, when appropriate
* Possible mitigation or remediation ideas

Please **do not include real credentials, private keys, personal information, or other sensitive data** in the report.

### ⚠️ If you are unsure

If you are not sure whether an issue qualifies as a security vulnerability, please report it privately anyway.

It is better to have a potentially non-security issue reviewed privately than to publicly disclose a vulnerability that could affect other users.

---

## 🔎 What Should Be Reported Privately?

Security issues that could affect the confidentiality, integrity, or availability of the project should generally be reported privately.

Examples include:

* Authentication bypasses
* Authorization vulnerabilities
* Account takeover vulnerabilities
* Improper access control
* Sensitive information exposure
* Credential or secret exposure
* SQL injection
* Network protocol vulnerabilities
* Server-side input validation issues
* Remote code execution
* Significant denial-of-service vulnerabilities
* Cryptographic weaknesses
* Security-sensitive CI/CD vulnerabilities
* Vulnerabilities that could compromise other users or the server

When in doubt, it is safer to report the issue privately first.

---
## 🧪 Experimental Cryptography

The project currently contains experimental cryptographic components.

Relevant areas include:

```text
client_python/crypto.py
security/
server_rust/src/utils/vault.rs
```

⚠️ **Important:**

The current cryptographic system is experimental and is **not considered production-ready or cryptographically secure**.

It should not be relied upon to protect sensitive information in a real-world security context.

Security researchers and contributors are welcome to review the implementation and identify weaknesses.

Potential findings include:

* Weak cryptographic design
* Incorrect implementation
* Predictability
* Key-management problems
* Randomness issues
* Authentication weaknesses
* Replay vulnerabilities
* Information leakage
* Problems in encryption/decryption logic

Please report significant vulnerabilities privately before publicly disclosing technical exploit details.

---

## 🌐 Network Security

The Last Signal uses communication between a Python client and a Rust server.

Relevant components include:

```text
client_python/
├── client.py
├── packet.py
└── packets/

server_rust/src/network/
├── client.rs
├── handler.rs
├── packet.rs
├── parser.rs
└── server.rs
```

Security issues involving network packets should be taken seriously, especially when they could allow:

* Invalid data to crash the server
* Unauthorized actions
* Authentication bypass
* Privilege escalation
* State corruption
* Unexpected server behavior
* Resource exhaustion

Network protocol changes should also be reviewed carefully because they can affect both the client and server.

---

## 🗄️ Database Security

The project contains database-related code and migrations.

Relevant locations include:

```text
server_rust/src/database/
server_rust/migrations/
database/
```

Potential security issues include:

* SQL injection
* Improper input validation
* Unauthorized database access
* Sensitive information exposure
* Incorrect permission handling
* Unsafe database queries
* Credential exposure

Never commit database credentials, passwords, API keys, or other secrets to the repository.

---

## 🔑 Secrets and Credentials

**Never commit secrets to the repository.**

This includes:

* Passwords
* API keys
* Access tokens
* Private keys
* Database credentials
* Authentication secrets
* Personal credentials
* Production configuration containing sensitive information

If a secret is accidentally committed, do not simply delete it from the latest commit and assume it is safe.

The secret should be considered compromised and should be revoked or rotated as appropriate.

---

## ⚙️ CI/CD Security

The project uses GitHub Actions for automated builds, tests, reports, and other development tasks.

Workflow files are located in:

```text
.github/workflows/
```

Security concerns involving GitHub Actions may include:

* Unsafe use of untrusted input
* Secret exposure
* Command injection
* Insecure workflow permissions
* Unsafe third-party actions
* Dependency-related vulnerabilities
* Unauthorized repository modifications

Please report serious CI/CD vulnerabilities privately.

When modifying workflows, contributors should also avoid unnecessarily increasing repository permissions.

---

## 🧪 Security Testing

Security testing is welcome.

Useful contributions may include:

* Unit tests
* Integration tests
* Fuzzing
* Input validation tests
* Network protocol tests
* Authentication tests
* Database security tests
* Regression tests for previously discovered vulnerabilities

Security tests should be deterministic, understandable, and safe to run in the project's development and CI environments.

---

## 🛡️ Responsible Disclosure

Please give the maintainers a reasonable opportunity to investigate and address a security vulnerability before publicly disclosing detailed exploit information.

Once an issue has been investigated and, where appropriate, fixed, the project may publicly document the vulnerability and its resolution.

The exact disclosure timeline may depend on:

* Severity
* Complexity
* Availability of a fix
* Potential impact
* Whether the vulnerability affects released versions

---

 ## 👥 Security Contributions

Security-related contributions are welcome.

You can contribute by:

* Reviewing security-sensitive code
* Finding vulnerabilities
* Improving validation
* Adding security tests
* Reviewing the network protocol
* Reviewing authentication
* Reviewing database access
* Auditing experimental cryptography
* Improving CI/CD security
* Improving documentation

For substantial security changes, please open a discussion or Issue before implementing the change when possible.

---

## ⚠️ Important Disclaimer

The Last Signal is an actively developed open-source project.

Its architecture, networking, authentication, cryptographic components, and other security-sensitive systems may change significantly during development.

The project should **not currently be considered a production-ready secure system**.

In particular, the experimental cryptographic implementation should not be used as a substitute for established, professionally reviewed cryptographic libraries or protocols.

---

## 📬 Thank You

Security research and responsible vulnerability reports help make The Last Signal a stronger project.

Thank you for taking the time to help improve its security. 🔐

**The Last Signal — When the world disappears, one last signal remains.**
