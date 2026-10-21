import os
import random
import socket
import struct
import sys
import pytest


HOST = "127.0.0.1"
PORT = 5000

TESTS = 1000



@pytest.mark.security
def create_packet(packet_type, payload):

    body = (
        struct.pack("!H", packet_type)
        + payload
    )

    return (
        struct.pack("!I", len(body))
        + body
    )

@pytest.mark.security
def send_packet(packet):

    try:

        with socket.create_connection(
            (HOST, PORT),
            timeout=2,
        ) as sock:

            sock.sendall(packet)

            return True

    except Exception:

        return False

@pytest.mark.security
def random_payload():

    size = random.randint(0, 4096)

    return os.urandom(size)

@pytest.mark.security
def random_packet():

    packet_type = random.choice([
        1,      # PING
        2,      # LOGIN
        3,      # CHAT
        4,      # MOVE
        5,      # LOG
        0,
        6,
        255,
        65535,
    ])

    return create_packet(
        packet_type,
        random_payload(),
    )

@pytest.mark.security
def main():

    print("# Packet Fuzzing")
    print()

    successful = 0
    failed = 0

    for _ in range(TESTS):

        packet = random_packet()

        if send_packet(packet):
            successful += 1
        else:
            failed += 1

    print("| Statistique | Valeur |")
    print("|---|---:|")
    print(f"| Paquets envoyés | {TESTS} |")
    print(f"| Connexions réussies | {successful} |")
    print(f"| Connexions échouées | {failed} |")

    print()

    if failed:

        print(
            "⚠️ Certaines connexions ont échoué."
        )

        sys.exit(1)

    print("✅ Le serveur est resté accessible.")


if __name__ == "__main__":
    main()
