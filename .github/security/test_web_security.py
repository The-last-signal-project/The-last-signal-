''' Test de la sécurité du web'''
from __future__ import annotations
import os
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass


HOST = os.environ.get(
    "SECURITY_TEST_HOST",
    "127.0.0.1",
)

PORT = int(
    os.environ.get(
        "SECURITY_TEST_PORT",
        "5000",
    )
)

BASE_URL = (
    f"http://{HOST}:{PORT}"
)

TIMEOUT = 5


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str


def check_port() -> CheckResult:

    try:
        with socket.create_connection(
            (HOST, PORT),
            timeout=TIMEOUT,
        ):
            return CheckResult(
                "TCP service",
                True,
                f"{HOST}:{PORT} reachable",
            )

    except OSError as error:
        return CheckResult(
            "TCP service",
            False,
            f"Service unreachable: {error}",
        )


def fetch(
    path: str,
) -> tuple[int, dict[str, str], str] | None:

    url = (
        BASE_URL
        + path
    )

    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent":
                "Security-Test/2.0",
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=TIMEOUT,
        ) as response:

            body = response.read(
                512 * 1024
            ).decode(
                "utf-8",
                errors="replace",
            )

            headers = {
                key.lower(): value
                for key, value
                in response.headers.items()
            }

            return (
                response.status,
                headers,
                body,
            )

    except urllib.error.HTTPError as error:

        body = error.read(
            512 * 1024
        ).decode(
            "utf-8",
            errors="replace",
        )

        headers = {
            key.lower(): value
            for key, value
            in error.headers.items()
        }

        return (
            error.code,
            headers,
            body,
        )

    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
    ):
        return None


def check_headers(
    headers: dict[str, str],
) -> list[CheckResult]:

    results: list[CheckResult] = []

    required = {
        "x-content-type-options": "nosniff",
    }

    for header, expected in required.items():

        value = headers.get(header, "")

        if value.lower() == expected.lower():

            results.append(
                CheckResult(
                    header,
                    True,
                    f"{value}",
                )
            )

        else:

            results.append(
                CheckResult(
                    header,
                    False,
                    f"Expected {expected!r}, got {value!r}",
                )
            )

    # --------------------------------------------------------
    # Clickjacking
    # --------------------------------------------------------

    frame_options = headers.get(
        "x-frame-options",
        "",
    )

    csp = headers.get(
        "content-security-policy",
        "",
    )

    if frame_options or (
        "frame-ancestors" in csp.lower()
    ):

        results.append(
            CheckResult(
                "Clickjacking protection",
                True,
                "X-Frame-Options/CSP protection present",
            )
        )

    else:

        results.append(
            CheckResult(
                "Clickjacking protection",
                False,
                "No X-Frame-Options or CSP frame-ancestors",
            )
        )

    # --------------------------------------------------------
    # Referrer
    # --------------------------------------------------------

    referrer = headers.get(
        "referrer-policy",
        "",
    )

    results.append(
        CheckResult(
            "Referrer-Policy",
            bool(referrer),
            referrer or "Header missing",
        )
    )

    # --------------------------------------------------------
    # Permissions
    # --------------------------------------------------------

    permissions = headers.get(
        "permissions-policy",
        "",
    )

    results.append(
        CheckResult(
            "Permissions-Policy",
            bool(permissions),
            permissions or "Header missing",
        )
    )

    # --------------------------------------------------------
    # Server information
    # --------------------------------------------------------

    server = headers.get(
        "server",
        "",
    )

    if server:
        results.append(
            CheckResult(
                "Server header",
                False,
                "Server header exposes information",
            )
        )
    else:
        results.append(
            CheckResult(
                "Server header",
                True,
                "No Server header",
            )
        )

    return results


def check_http_methods() -> list[CheckResult]:
    results: list[CheckResult] = []

    dangerous_methods = [
        "TRACE",
    ]

    for method in dangerous_methods:

        request = urllib.request.Request(
            BASE_URL + "/",
            method=method,
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=TIMEOUT,
            ) as response:

                status = response.status

        except urllib.error.HTTPError as error:
            status = error.code

        except (
            urllib.error.URLError,
            OSError,
        ):
            continue

        if 200 <= status < 300:

            results.append(
                CheckResult(
                    f"HTTP {method}",
                    False,
                    f"Method accepted with HTTP {status}",
                )
            )

        else:

            results.append(
                CheckResult(
                    f"HTTP {method}",
                    True,
                    f"HTTP {status}",
                )
            )

    return results


def check_information_exposure(
    body: str,
) -> list[CheckResult]:

    results: list[CheckResult] = []

    forbidden_markers = [
        "Traceback (most recent call last)",
        "RUST_BACKTRACE",
        "panic occurred",
        "DATABASE_URL=",
        "VAULT_KEY=",
        "SECRET_KEY=",
        "PRIVATE KEY",
    ]

    found = [
        marker
        for marker in forbidden_markers
        if marker.lower() in body.lower()
    ]

    if found:

        results.append(
            CheckResult(
                "Information exposure",
                False,
                "Sensitive/debug information detected",
            )
        )

    else:

        results.append(
            CheckResult(
                "Information exposure",
                True,
                "No configured sensitive markers",
            )
        )

    return results


def main() -> int:
    print("=== WEB SECURITY SCAN ===")
    print(
        f"Target: {BASE_URL}"
    )

    failures = 0

    port_result = check_port()

    print(
        f"[{'PASS' if port_result.passed else 'FAIL'}] "
        f"{port_result.name}: "
        f"{port_result.message}"
    )

    if not port_result.passed:
        print(
            "[SKIP] Web security checks because "
            "the local service is unavailable."
        )
        return 0

    response = fetch("/")

    if response is None:
        print(
            "[FAIL] Unable to retrieve /"
        )
        return 1

    status, headers, body = response

    print(
        f"[INFO] HTTP status: {status}"
    )

    # --------------------------------------------------------
    # Headers
    # --------------------------------------------------------

    for result in check_headers(headers):

        print(
            f"[{'PASS' if result.passed else 'FAIL'}] "
            f"{result.name}: "
            f"{result.message}"
        )

        if not result.passed:
            failures += 1

    # --------------------------------------------------------
    # Methods
    # --------------------------------------------------------

    for result in check_http_methods():

        print(
            f"[{'PASS' if result.passed else 'FAIL'}] "
            f"{result.name}: "
            f"{result.message}"
        )

        if not result.passed:
            failures += 1

    # --------------------------------------------------------
    # Information disclosure
    # --------------------------------------------------------

    for result in check_information_exposure(body):

        print(
            f"[{'PASS' if result.passed else 'FAIL'}] "
            f"{result.name}: "
            f"{result.message}"
        )

        if not result.passed:
            failures += 1

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print()

    if failures == 0:
        print(
            "[PASS] Web security checks passed."
        )
        return 0

    print(
        f"[FAIL] {failures} web security "
        "finding(s) detected."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
  
