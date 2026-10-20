# 🤝 Contributing to The Last Signal

Thank you for your interest in contributing to **The Last Signal**! 🎮

The Last Signal is an open-source post-apocalyptic MMORPG currently under development, with a **Python client** and a **Rust server**.

Contributions of all kinds are welcome — from fixing a small bug to improving tests, documentation, networking, security, CI/CD, gameplay, or game assets.

---

## 📋 Before You Start

Before contributing, we recommend that you:

1. Read the project `README.md`.
2. Check the existing GitHub Issues.
3. Look at the relevant documentation in `docs/`.
4. Make sure your contribution fits the current direction of the project.
5. For significant changes, discuss the idea before starting implementation.

The project is actively evolving, so some parts of the codebase are experimental or still under development.

---

## 🧑‍💻 Areas Where You Can Contribute

There are several areas where contributions are especially useful.

### 🦀 Rust — Server

The Rust server contains areas such as:

```text
server_rust/
├── src/
│   ├── network/
│   ├── database/
│   ├── gameplay/
│   ├── player/
│   ├── utils/
│   ├── auth/
│   ├── combat/
│   ├── config/
│   └── world/
├── migrations/
└── tests/
```

Possible contributions include:

* Server development
* Network handling
* Packet parsing
* Database integration
* Gameplay systems
* Player systems
* Authentication
* Combat systems
* Testing
* Performance improvements

Some directories are currently placeholders and will be developed progressively.

---

### 🐍 Python — Client

The Python client is located in:

```text
client_python/
```

It currently contains:

* Client connection and communication
* Packet handling
* Packet-specific modules
* Logging
* Experimental cryptography

Possible contributions include:

* Client development
* Network communication
* Packet implementation
* User interface
* Graphics
* Client-side testing
* Bug fixes
* Code quality improvements

---

### 🌐 Networking

The client/server protocol is an important part of the project.

Relevant code includes:

```text
client_python/
├── client.py
├── packet.py
└── packets/

server_rust/
└── src/
    └── network/
        ├── client.rs
        ├── handler.rs
        ├── packet.rs
        ├── parser.rs
        └── server.rs
```

Contributions can include:

* Packet definitions
* Serialization/deserialization
* Protocol tests
* Error handling
* Edge cases
* Client/server compatibility

Please avoid changing the protocol without considering its impact on both the Python client and Rust server.

---

### 🧪 Testing

Testing is an important part of the project.

Relevant locations include:

```text
tests/
server_rust/tests/
```

You can contribute by:

* Adding unit tests
* Adding integration tests
* Testing network packets
* Testing invalid input
* Testing edge cases
* Improving test coverage
* Fixing unreliable tests

A contribution that only adds useful tests is completely valid. ✅

---

### 🔐 Security & Experimental Cryptography

Security-related contributions are welcome.

The project currently contains experimental cryptographic code, including components in:

```text
client_python/crypto.py
security/
server_rust/src/security/crypto.rs
```

⚠️ **Important:** the current cryptographic system is experimental and is **not considered production-ready or secure**.

Security contributors can help with:

* Code review
* Threat modeling
* Identifying weaknesses
* Security testing
* Improving implementation
* Cryptographic research and experimentation

Please clearly explain security implications when proposing changes in this area.

---

### ⚙️ CI/CD

The project uses GitHub Actions for automation.

Possible contributions include:

* Improving workflows
* Fixing CI failures
* Improving test automation
* Improving build automation
* Improving report generation
* Improving workflow reliability
* Reducing unnecessary CI work

Workflow files are located in:

```text
.github/workflows/
```

Before modifying a workflow, make sure you understand which other workflows depend on it.

---

### 📚 Documentation

Documentation is an important part of the project.

Documentation is mainly located in:

```text
docs/
```

This includes:

* Game Design Documentation (GDD)
* Technical Design Documentation (TDD)
* Architecture
* Networking
* Database documentation
* Gameplay documentation
* Lore
* Roadmap
* Coding rules

You can contribute by:

* Fixing errors
* Improving explanations
* Adding missing documentation
* Translating documentation
* Improving the GitHub Wiki
* Keeping documentation synchronized with the code

---

### 🎨 Art & Game Assets

Contributions to the visual side of the project are also welcome.

Possible areas include:

* 3D models
* Concept art
* Illustrations
* Animations
* Weapons
* Environment assets
* fonts
* music
* Other game assets

Please discuss larger asset contributions before investing significant work into them.

---

# 🔎 Finding an Issue

The best way to start contributing is to look through the **open GitHub Issues**.

Issues may cover different difficulty levels and areas of the project.

Look for issues related to your skills or interests.

For example:

```text
🦀 Rust
🐍 Python
🌐 Networking
🧪 Testing
🔐 Security
⚙️ CI/CD
📚 Documentation
🎨 Art
```

If an issue interests you, you can comment on it before starting work.

For larger changes, discussing the approach first can help avoid duplicated or unnecessary work.

---

# 🛠 Development Setup

Clone the repository:

```bash
git clone https://github.com/DDCoder23/The-last-signal-.git
cd The-last-signal-
```

Then install the dependencies required for the part of the project you want to work on.

### Python

The Python client is located in:

```text
client_python/
```

Python dependencies may be required depending on the component being developed.

### Rust

The Rust server is located in:

```text
server_rust/
```

Cargo is used to manage the Rust project.

For example:

```bash
cd server_rust
cargo build
```

---

# 🌿 Git Workflow

Please use a dedicated branch for each contribution.

Do **not** develop directly on `main`.

A typical workflow is:

```text
main
  │
  └── feature/my-change
          │
          ├── changes
          ├── tests
          └── Pull Request
                  │
                  ↓
                main
```

Create a branch from an up-to-date `main`:

```bash
git checkout main
git pull origin main
git checkout -b feature/my-change
```

Use a descriptive branch name.

Examples:

```text
feature/network-tests
feature/python-login
feature/rust-packet-parser
fix/login-error
fix/packet-validation
docs/update-architecture
docs/improve-contributing
test/network-protocol
ci/improve-build
```

---

# 💻 Making Changes

Keep changes focused.

A Pull Request should preferably solve **one problem or implement one coherent feature**.

Avoid mixing unrelated changes into the same PR.

For example, avoid a PR that simultaneously:

* changes the network protocol;
* rewrites unrelated Python code;
* modifies the CI;
* changes documentation;
* and reformats the entire repository.

Smaller PRs are easier to review, test, and merge. 👍

---

# 🧪 Testing Your Changes

Before opening a Pull Request, test the changes locally whenever possible.

### Rust

From `server_rust/`:

```bash
cargo test
```

You should also make sure that the project still builds:

```bash
cargo build
```

### Python

### Python

Run the standard Python test suite from the repository root:

```bash
python -m pytest tests/ --ignore=tests/security
```

This runs the suite without the security tests: the files in
`tests/security/` require the `DATABASE_PATH` environment variable
(a server database) and fail during collection without it. Note that
`-m "not security"` is not enough, because pytest still collects
those files before filtering.

If your change affects both the Python client and Rust server, test both sides when possible.

---

# 📝 Commit Messages

Write clear commit messages that describe the change.

Good examples:

```text
Add network packet tests
Fix login packet parsing
Improve Rust network handler tests
Add Python client packet validation
Update architecture documentation
Fix CI report generation
```

Avoid vague messages such as:

```text
update
fix
changes
stuff
test
```

A commit should give another developer a reasonable idea of what changed.

---

# 🔄 Keeping Your Branch Updated

The `main` branch may change while you are working.

Before opening or updating a Pull Request, make sure your branch is reasonably up to date with `main`.

If your branch becomes significantly outdated or conflicts appear, update it carefully and resolve conflicts before requesting a final review.

When resolving conflicts, make sure you do not accidentally remove changes made by other contributors.

---

# 📦 Pull Requests

When your work is ready:

1. Push your branch to GitHub.
2. Open a Pull Request targeting `main`.
3. Explain what you changed.
4. Explain why the change was needed.
5. Mention the relevant Issue when applicable.
6. Describe the tests you performed.
7. Mention anything that still needs attention.

A useful Pull Request description can follow this structure:

```markdown
## What does this PR do?

Briefly describe the changes.

## Why?

Explain the reason for the change.

## Related Issue

Closes #123

## Testing

- [x] Rust tests
- [x] Python tests
- [x] Manual testing

## Notes

Anything reviewers should know.
```

---

# 👀 Pull Request Review

Pull Requests may be reviewed before being merged.

Reviewers may request:

* Code changes
* Additional tests
* Documentation
* Clarifications
* Improvements to error handling
* Changes to the implementation

Code review is part of the development process and is intended to improve the project, not to criticize contributors.

Please keep discussions constructive and technical.

---

# 📐 Code Guidelines

Follow the existing conventions of the part of the project you are modifying.

In general:

* Keep code readable.
* Prefer clear names.
* Avoid unnecessary complexity.
* Keep functions reasonably focused.
* Handle errors explicitly.
* Avoid unrelated refactoring.
* Add tests when appropriate.
* Document non-obvious behavior.
* Do not introduce unnecessary dependencies.

If a project-specific coding rule applies, follow the relevant documentation in `docs/`.

---

# 📚 Documentation Requirements

If your contribution introduces a significant new feature or changes existing behavior, consider whether the documentation needs to be updated.

Documentation may include:

* Architecture documentation
* Network documentation
* Database documentation
* Gameplay documentation
* GDD/TDD
* Wiki pages
* Code comments or API documentation

The goal is to keep the documentation and implementation consistent.

---

# ⚠️ Experimental Components

Some parts of The Last Signal are prototypes or experimental systems.

In particular:

* Some Rust modules are currently placeholders.
* The networking protocol is still evolving.
* The cryptographic system is experimental.
* Some gameplay systems are prototypes.
* The project architecture may change as development progresses.

Do not assume that every existing component represents the final architecture.

When contributing to experimental systems, clearly explain important design decisions in your Pull Request.

---

# 🚫 What Not to Do

Please do not:

* Commit passwords, API keys, private keys, or other secrets.
* Commit personal credentials or sensitive data.
* Modify unrelated parts of the project without a reason.
* Force-push over another contributor's work.
* Submit generated code without understanding and testing it.
* Add dependencies without considering whether they are necessary.
* Bypass security checks or CI failures without understanding the cause.
* Submit deliberately malicious code or tests.

If you discover a security vulnerability, please report it responsibly rather than publicly exposing sensitive details.

---

# 🐛 Bug Reports

If you find a bug, check the existing Issues first.

If it has not already been reported, create an Issue containing as much useful information as possible.

Include:

* What happened
* What you expected to happen
* Steps to reproduce the problem
* Relevant error messages
* Environment information
* Relevant logs
* A minimal reproduction when possible

A good bug report helps contributors reproduce and fix the problem faster.

---

# 💡 Feature Proposals

Before implementing a large new feature, consider opening an Issue to discuss it.

A useful proposal should explain:

* What the feature is
* Why it would be useful
* How it could work
* Which part of the project it affects
* Potential technical difficulties

Large features may require changes to the GDD, TDD, architecture, or roadmap before implementation.

---

# 🌍 Translations

The project may contain documentation in multiple languages.

When contributing translations:

* Preserve the meaning of the original documentation.
* Keep technical terminology consistent.
* Avoid translating code, commands, file paths, or API names unnecessarily.
* Keep links working.
* Clearly indicate unfinished translations when necessary.

Translations are welcome and can be valuable contributions even without code changes.

---

# 🤝 Communication

The Last Signal is an open-source project, and contributors may have different levels of experience.

Please:

* Be respectful.
* Explain technical decisions clearly.
* Ask questions when something is unclear.
* Give constructive feedback.
* Help other contributors when possible.

For the project's community standards and expected behavior, please read the [Code of Conduct](CODE_OF_CONDUCT.md).

You do not need to be an expert to contribute.

Small improvements, documentation fixes, tests, and beginner-friendly Issues are all valuable contributions. ❤️

---

# 🚀 First Contribution?

If this is your first contribution, a good starting point is:

1. Read the README.
2. Look through the open Issues.
3. Choose a small task matching your interests.
4. Create a dedicated branch.
5. Make your changes.
6. Run the relevant tests.
7. Open a Pull Request.

You can start with something as small as:

```text
🧪 Add a missing test
📚 Fix documentation
🐛 Fix a small bug
🐍 Improve a Python component
🦀 Improve a Rust component
⚙️ Fix a CI issue
🌐 Improve a network test
```

Every contribution helps move the project forward. 🚀

---

# 📖 Further Documentation

The project documentation is located in:

```text
docs/
```

For technical or design questions, consult the relevant documentation before making major changes.

You can also use the GitHub Wiki for contributor-oriented information and practical guides.

---

## Thank You! ❤️

Thank you for taking the time to contribute to **The Last Signal**.

Whether you submit a small documentation fix, a test, a bug fix, a new feature, or a larger system, your contribution helps the project grow.

**The Last Signal — When the world disappears, one last signal remains.**
