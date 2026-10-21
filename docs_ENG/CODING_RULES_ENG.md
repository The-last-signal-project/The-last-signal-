[🏠 Documentation](README_ENG.md)

# 💻 Development Guidelines (Coding Rules)

> **Project:** The Last Signal Online

---

## 📋 Information

| Property | Value |
|-----------|-------|
| **Document** | Coding Rules |
| **Code** | DOC-010 |
| **Version** | 1.0.0 |
| **Status** | 🟢 Active |
| **Last updated** | July 15, 2026 |

---

# 📖 Table of Contents

1. Objective
2. Technologies Used
3. Project Architecture & Organization
4. Directory Structure
5. Naming Conventions
6. Python Code Style
7. Rust Code Style
8. Error Handling
9. Code Documentation
10. Git Branching Strategy
11. GitHub Workflow
12. Pull Requests
13. Testing Standards
14. Security Rules
15. Optimization Guidelines
16. Best Practices
17. Pre-Submission Checklist
18. Contributing Guidelines
19. Code of Conduct
20. License

---

# 1. Objective

This document defines the official development rules and coding standards for **The Last Signal Online**.

Its purpose is to ensure:

- a clean and homogeneous codebase;
- ease of maintenance and refactoring;
- effective collaboration across team members;
- high standards of software quality and reliability.

These rules apply to all contributors.

---

# 2. Technologies Used

| Technology | Usage |
|-------------|-------|
| Python | Game Client & Tooling |
| Rust | Game Server |
| PostgreSQL | Primary Database |
| Redis | Caching Layer |
| WebSocket / TCP | Network Communication |
| Docker | Containerization & Deployment |
| Git | Version Control |
| GitHub Actions | CI/CD Automation |
| Markdown | Documentation |

---

# 3. Project Architecture & Organization

The project is structured into independent, decoupled modules.

Each module must follow the Single Responsibility Principle (SRP).

Core domains include:

- Network
- Player & Accounts
- Inventory & Equipment
- Combat & Systems
- World & Environments
- AI & Entities
- UI & HUD

---

# 4. Directory Structure

Each directory has a well-defined responsibility.

Files must be organized strictly according to their domain and functionality.

Avoid monolithic files containing unrelated systems.

---

# 5. Naming Conventions

- Python: `snake_case` for functions and variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
- Rust: `snake_case` for functions/modules/variables, `PascalCase` for structs/enums/traits, `SCREAMING_SNAKE_CASE` for constants.
- Function and variable names must use Roman characters and clear English names.

---

# 6. Python Code Style

Python code must adhere to PEP 8 standards:

- Comprehensive type hints (`typing` / built-in types).
- Short, focused functions.
- Explicit and descriptive variable names.
- Minimal reliance on global variables.

All public functions, classes, and methods must have descriptive docstrings.

---

# 7. Rust Code Style

Rust code must adhere to idiomatic Rust standards:

- Formatted with `cargo fmt`.
- Linted with `cargo clippy` without warnings.
- Robust error handling using `Result` and `Option` (avoid unhandled `.unwrap()` in production paths).
- Complete doc comments (`///`) on public functions and structs.

---

# 8. Error Handling

Errors must never be silently ignored or swallowed.

Always:

- Display or return meaningful error context.
- Log errors to the appropriate logging subsystem with severity levels.
- Gracefully handle recoverable failures and avoid abrupt crashes.

---

# 9. Code Documentation

Every non-trivial function and module must be documented.

Comments should explain **why** the code exists rather than simply restating **what** the syntax does.

Avoid redundant or obsolete comments.

---

# 10. Git Branching Strategy

Never commit directly to the `main` branch (administrators may perform emergency fixes but must review code).

Every new feature or bug fix must be developed on a dedicated branch.

Branch naming examples:

```text
feature/login
feature/inventory
feature/chat
feature/world
```

For bug fixes:

```text
fix/login
fix/database
```

For documentation:

```text
docs/gdd
docs/readme
```

---

# 11. GitHub Workflow

The standard contribution workflow is:

```text
Issue
  ↓
Branch
  ↓
Development
  ↓
Automated Tests & Linting
  ↓
Pull Request
  ↓
Code Review
  ↓
Merge into main
```

No pull request may be merged without peer code review and formal approval from an authorized administrator.

---

# 12. Pull Requests

Every Pull Request must:

- Have a clear and descriptive title.
- Detail the rationale and scope of the modifications.
- Reference relevant GitHub Issues (`Fixes #123`, `Closes #456`).
- Be reviewed and approved by an administrator before merging.

---

# 13. Testing Standards

Before any merge:

- The project must compile cleanly without errors.
- All automated unit and integration tests must pass.
- No critical compiler or linter warnings.
- No unresolved known regressions.

All new features and bug fixes should include corresponding automated tests whenever feasible.

---

# 14. Security Rules

It is strictly forbidden to:

- Commit passwords, plaintext credentials, or secrets.
- Commit API keys or private tokens.
- Commit GitHub Personal Access Tokens or SSH private keys.
- Intentionally bypass or disable security checks.

Sensitive configuration parameters must be supplied via environment variables or encrypted secrets vaults.

---

# 15. Optimization Guidelines

Code must be:

- **Readable:** Function and variable names in standard English Roman alphabet (consult an English-speaking maintainer if needed).
- **Maintainable:** Clean abstractions with low cyclomatic complexity.
- **Performant:** Efficient algorithms and memory management.

Avoid premature optimization. Measure and profile before optimizing, and optimize only when a measurable bottleneck is identified.

---

# 16. Best Practices

Always:

- Write clean, self-explanatory code.
- Follow the DRY (Don't Repeat Yourself) principle.
- Prefer small, modular functions.
- Respect the system architecture.
- Document key design decisions and architectural trade-offs.

---

# 17. Pre-Submission Checklist

Before submitting a Pull Request:

- [ ] Project builds and compiles successfully.
- [ ] All test suites pass.
- [ ] Code adheres to language style guides and formatting rules.
- [ ] Documentation is updated to reflect changes.
- [ ] `CHANGELOG_ENG.md` is updated if applicable.
- [ ] No secrets, keys, or credentials committed.
- [ ] New files are correctly organized in the project tree.
- [ ] Self-review conducted.

---

# 18. Contributing Guidelines

## 📋 Requirements

Before contributing, please ensure you:

- Read the project documentation.
- Adhere to these Coding Rules.
- Abide by the [Code of Conduct](../CODE_OF_CONDUCT.md).
- Follow standard Git branching practices.

---

## 🚀 Getting Started

1. Fork the repository (for external contributors).
2. Clone your fork locally.
3. Create a descriptive feature branch (`git checkout -b feature/my-feature`).
4. Implement your changes.
5. Run the test suite and verify code quality.
6. Update documentation where appropriate.
7. Open a Pull Request targeting `main`.

---

## 💬 Commit Messages

Use standard conventional commit prefixes:

```text
feat: add player inventory management system
fix: resolve client login authentication timeout
docs: update GDD narrative specifications
refactor: improve network packet serialization
test: add integration tests for socket connection
```

---

## 🔍 Code Review

All PRs undergo review before merging. Review comments and requested changes must be addressed prior to final approval.

---

# 📜 Code of Conduct

Treat all community members and contributors with mutual respect.

All interactions should remain:

- Respectful
- Constructive
- Professional

---

# 📄 License

By contributing to **The Last Signal Online**, you agree that your contributions will be licensed under the project's open-source [LICENSE](../LICENSE).

---

Thank you for contributing to **The Last Signal Online**! 🚀

# 📚 Related Documents

- [🏠 Documentation](README_ENG.md)
- [🏗 Technical Design Document](tdd/README_ENG.md)
- [🛣 Roadmap](ROADMAP_ENG.md)
- [📝 Changelog](../CHANGELOG_ENG.md)

---

## Navigation

⬅️ Return: [Documentation](README_ENG.md)
