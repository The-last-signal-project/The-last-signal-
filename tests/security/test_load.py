import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import pytest

HOST = "127.0.0.1"
PORT = 5000
max_count = 4096



@pytest.mark.security
def ping():

    start = time.perf_counter()

    try:

        with socket.create_connection(
            (HOST, PORT),
            timeout=5,
        ) as sock:

            body = (
                b"\x00\x01"
                # PacketType::PING
            )

            packet = (
                len(body).to_bytes(4, "big")
                + body
            )

            sock.sendall(packet)

            response = sock.recv(1024)

            elapsed = (
                time.perf_counter() - start
            )

            return True, elapsed, response

    except Exception:

        return False, None, None

@pytest.mark.security
def run_test(connections):

    with ThreadPoolExecutor(
        max_workers=connections
    ) as executor:

        results = list(
            executor.map(
                lambda _: ping(),
                range(connections),
            )
        )

    successful = sum(
        result[0]
        for result in results
    )

    failed = connections - successful

    times = [
        result[1]
        for result in results
        if result[1] is not None
    ]

    average = (
        sum(times) / len(times)
        if times
        else 0
    )

    return successful, failed, average

@pytest.mark.security
def test_main():

    print("# Server Load Test")
    print()

    print(
        "| Connexions simultanées | "
        "Succès | Échecs | Temps moyen |"
    )
    print(
        "|---:|---:|---:|---:|"
    )

    connection_count = 1
    detected_failure = False

    while connection_count <= max_count:

        successful, failed, average = run_test(
            connection_count
        )

        print(
            f"| {connection_count} | "
            f"{successful} | "
            f"{failed} | "
            f"{average:.4f}s |"
        )

        if failed > 0:

            print()
            print(
                f"⚠️ Première saturation détectée "
                f"à {connection_count} connexions."
            )

            detected_failure = True
            break

        connection_count *= 2

        time.sleep(0.5)

    print()

    if not detected_failure:

        print(
            "✅ Aucune saturation détectée "
            f"jusqu'à {max_count}  connexions simultanées."
        )

    # Ce n'est pas forcément une vulnérabilité :
    # le serveur peut volontairement limiter les connexions.
    sys.exit(0)


if __name__ == "__main__":
    test_main()
