'''Test de sécurité python'''
from __future__ import annotations
import ast
from pathlib import Path


ROOT = Path.cwd().resolve()

IGNORED_DIRECTORIES = {
    ".git",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
}


def should_ignore(path: Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return True

    return any(
        part in IGNORED_DIRECTORIES
        for part in relative.parts
    )


class SecurityVisitor(ast.NodeVisitor):

    def __init__(
        self,
        path: Path,
    ) -> None:
        self.path = path
        self.findings: list[tuple[int, str]] = []

    def report(
        self,
        node: ast.AST,
        message: str,
    ) -> None:

        line = getattr(
            node,
            "lineno",
            0,
        )

        self.findings.append(
            (
                line,
                message,
            )
        )

    def visit_Call(
        self,
        node: ast.Call,
    ) -> None:

        # ----------------------------------------------------
        # eval()
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "eval"
        ):
            self.report(
                node,
                "Use of eval()",
            )

        # ----------------------------------------------------
        # exec()
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "exec"
        ):
            self.report(
                node,
                "Use of exec()",
            )

        # ----------------------------------------------------
        # compile()
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "compile"
        ):
            self.report(
                node,
                "Dynamic compile() usage",
            )

        # ----------------------------------------------------
        # os.system()
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "system"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "os"
        ):
            self.report(
                node,
                "os.system() command execution",
            )

        # ----------------------------------------------------
        # pickle.loads / pickle.load
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {
                "load",
                "loads",
            }
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pickle"
        ):
            self.report(
                node,
                "Unsafe pickle deserialization",
            )

        # ----------------------------------------------------
        # subprocess shell=True
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {
                "run",
                "Popen",
                "call",
                "check_call",
                "check_output",
            }
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        ):

            for keyword in node.keywords:

                if keyword.arg != "shell":
                    continue

                if (
                    isinstance(
                        keyword.value,
                        ast.Constant,
                    )
                    and keyword.value.value is True
                ):
                    self.report(
                        node,
                        "subprocess with shell=True",
                    )

        # ----------------------------------------------------
        # SQL construit par concaténation/interpolation
        # ----------------------------------------------------

        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in {
                "execute",
                "executemany",
            }
        ):

            if node.args:

                query = node.args[0]

                if isinstance(
                    query,
                    (
                        ast.JoinedStr,
                        ast.BinOp,
                    ),
                ):
                    self.report(
                        node,
                        "Potential dynamically constructed SQL query",
                    )

        self.generic_visit(node)


def scan_file(
    path: Path,
) -> list[tuple[int, str]]:

    try:
        source = path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:
        return []

    except OSError:
        return []

    try:
        tree = ast.parse(
            source,
            filename=str(path),
        )

    except SyntaxError as error:
        return [
            (
                error.lineno or 0,
                "Python syntax error",
            )
        ]

    visitor = SecurityVisitor(path)

    visitor.visit(tree)

    return visitor.findings


def main() -> int:
    print("=== PYTHON SECURITY SCAN ===")

    failures = 0
    files = 0

    for path in ROOT.rglob("*.py"):

        if should_ignore(path):
            continue

        files += 1

        findings = scan_file(path)

        for line, message in findings:

            relative = path.relative_to(ROOT)

            print(
                f"[FAIL] {relative}:{line} - {message}"
            )

            failures += 1

    print()
    print(
        f"Python files inspected: {files}"
    )

    if failures == 0:
        print(
            "[PASS] No configured Python security "
            "anti-pattern detected."
        )
        return 0

    print(
        f"[FAIL] {failures} Python security "
        f"finding(s) detected."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
